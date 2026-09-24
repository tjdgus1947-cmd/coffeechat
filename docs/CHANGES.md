# 리팩터링 기록 (2026.09)

프로젝트 종료 후 코드와 DB를 다시 점검하며 고친 내용입니다.
각 항목은 **문제 → 원인 → 변경 → 확인 방법** 순서로 적었습니다.

---

## 1. 같은 슬롯 중복 예약

**문제**: 두 멘티가 거의 동시에 같은 시간 슬롯을 예약하면 둘 다 성공할 수 있었다.

**원인**: 예약 생성이 "슬롯 조회 → `is_booked` 확인 → 예약 INSERT → 슬롯 UPDATE" 순서였다. 두 요청이 모두 조회 단계를 통과하면 둘 다 INSERT 한다(check-then-act 경쟁 조건). DB에도 `coffee_chats.availability_id`에 UNIQUE가 없어서 막아 줄 장치가 없었다.

**변경**
- 슬롯 선점을 **조건부 UPDATE** 한 번으로 처리: `UPDATE mentor_availability SET is_booked = true WHERE id = ? AND is_booked = false`. PostgreSQL은 같은 행의 UPDATE를 행 잠금으로 직렬화하므로, 두 번째 요청은 조건이 false가 돼 0행이 갱신되고 409를 받는다.
- 예약 INSERT가 실패하면 선점한 슬롯을 되돌린다(보상 처리, `finally`).
- 최종 안전장치로 `coffee_chats.availability_id`에 UNIQUE 추가. 승인·거절 시 이 값을 NULL로 바꾸고, PostgreSQL UNIQUE는 NULL끼리 중복으로 보지 않으므로 "대기 중 예약은 슬롯당 1건"이 된다.
- 승인·거절도 `WHERE status = 'pending'` 조건부 UPDATE로 바꿔, 두 번 눌러도 채팅방이 한 번만 생긴다.
- 거절 시 슬롯을 삭제하던 동작을 **다시 예약 가능 상태로 되돌리도록** 변경했다.

**확인**: `tests/test_bookings.py`. 로컬 PostgreSQL에서 UNIQUE 위반도 확인했다.

---

## 2. 404·409가 전부 500으로 바뀜

**원인**: `try` 안에서 `raise HTTPException(404)`를 던져도 바로 아래 `except Exception`이 잡아서 500으로 다시 던졌다. `HTTPException`도 `Exception`의 하위 클래스이기 때문이다.

**변경**: 모든 라우터의 `except Exception` 앞에 `except HTTPException: raise`를 두었다. 500 응답의 `detail`에 내부 예외 메시지(`str(e)`)를 그대로 내보내던 부분은 일반 문구로 바꿨다.

---

## 3. 다른 사용자 데이터를 수정할 수 있던 API

**문제**: 백엔드는 RLS를 우회하는 service_role 키를 쓴다. 그런데 아래 API가 **요청 본문이나 쿼리의 `user_id`를 그대로 믿었다.** 로그인하지 않아도, 남의 id만 알면 수정할 수 있었다.

| API | 문제 |
|---|---|
| `POST /api/profile/update-introduction` | 남의 자기소개·임베딩 덮어쓰기 |
| `POST /api/location/update` | 남의 위치 변경 |
| `POST /api/availability/` | 남의 이름으로 예약 슬롯 생성 |
| `GET /api/matching/*`, `/api/profile/introduction`, `/api/locations/map-data/*` | 로그인 없이 조회 |

**변경**: 모두 `Depends(get_current_user_id)`로 토큰에서 사용자를 꺼내 쓰고, 본문의 `user_id`는 하위 호환용으로만 받아서 무시한다. 프론트에서 토큰 없이 `axios`를 직접 쓰던 3곳은 토큰이 붙는 `api` 인스턴스로 바꿨다.

**확인**: `tests/test_auth_scope.py`. 남의 `user_id`를 보내도 본인 행만 바뀌는지 검증한다.

---

## 4. 테이블 전체를 읽어 오던 조회 ("`.eq()` 버그 우회")

**문제**: 매칭·지도 API가 내 프로필 1건을 찾으려고 **테이블 전체를 페이지 단위로 가져와** 파이썬에서 `user_id`를 비교했다. 요청 한 번에 `users`, `mentor_profiles`, `mentee_profiles` 전체를 읽었다.

**원인**: 개발 당시 `.eq()`가 동작하지 않는다고 판단해 우회한 코드였다. `user_id`는 UNIQUE 인덱스가 있는 컬럼이라 `.eq()`로 1행만 읽는 게 정상이다.

**변경**: `.eq("user_id", ...)` 단건 조회로 교체했다. 지도 API는 `users(full_name)` 임베드로 이름을 JOIN해서 쿼리 3번으로 줄였다.

---

## 5. 매칭 후보 검색을 DB로 이동 (pgvector)

**이전**: 상대 역할 프로필 **전체**의 1024차원 임베딩을 API 서버로 가져와 파이썬에서 코사인 유사도를 계산했다. 사용자 수에 비례해 네트워크 전송량과 CPU가 늘어나는 구조다.

**변경**
- DB 함수 `match_candidates`: `ORDER BY embedding <=> 질의벡터 LIMIT N`으로 가까운 후보 N(=200)명만 반환한다.
- `embedding`을 `vector(1024)`로 고정하고 **HNSW 인덱스**(`vector_cosine_ops`)를 추가했다. 벡터 인덱스는 차원이 정해진 컬럼에만 만들 수 있다.
- 이후 단계(거리 반영 → BM25 → 리랭킹 → 개인화)는 그대로 API에서 처리한다.

**주의**: 현재 데이터(약 100명)에서는 플래너가 인덱스보다 순차 스캔을 고를 수 있고, 체감 차이도 거의 없다. 후보 풀(200)이 전체 인원보다 크므로 결과도 이전과 같다. 이 변경의 의미는 **사용자 수가 늘어도 API 서버가 읽는 양이 일정하게 유지되는 구조**라는 데 있다. 성능 수치를 주장하려면 데이터를 늘려 `EXPLAIN ANALYZE`로 직접 측정해야 한다.

---

## 6. 리랭커가 영어 전용 모델이었음

**문제**: `cross-encoder/ms-marco-MiniLM-L-6-v2`는 영어 MS MARCO로만 학습된 모델이다. 주석에는 "한국어 특화"라고 적혀 있었다.

**변경**: 기본 모델을 다국어(한국어 포함) 리랭커 `BAAI/bge-reranker-v2-m3`로 교체했다. 임베딩 모델 bge-m3와 같은 계열이다. `RERANKER_MODEL` 환경변수로 바꿀 수 있다.

---

## 7. 점수 스케일 불일치와 리랭킹 결과 유실

**문제 1**: Cross-Encoder 출력은 범위가 없는 로짓(예: -8 ~ 9)이다. 여기에 ×100을 해서 0~100 점수와 가중 평균했다. 로짓이 음수면 점수도 음수가 된다.
**변경 1**: 시그모이드로 0~1 확률로 바꾼 뒤 ×100 한다. 큰 음수에서 `exp` 오버플로가 나지 않게 부호별로 나눠 계산했다.

**문제 2**: 리랭킹은 `combined_score`로 정렬했는데, 다음 단계인 개인화는 `final_score`로 다시 정렬했다. 그래서 개인화가 적용되는 사용자(예약 3건 이상)는 리랭킹 결과가 사라졌다.
**변경 2**: 모든 단계가 `final_score` 하나를 갱신하고 다음 단계가 이어받게 통일했다.

---

## 8. BM25 한국어 토큰화

**문제**: 공백 기준으로만 토큰을 나눠서 "데이터를"과 "데이터"가 다른 단어로 취급됐다.

**변경**: 한글 단어는 **2글자씩 겹쳐 자른 bigram**으로 토큰화한다("데이터를" → 데이, 이터, 터를). 형태소 분석기 없이 조사·어미 차이를 흡수하는 방식으로, Elasticsearch의 CJK bigram과 같은 원리다. 문서 길이(`avgdl`)도 같은 토큰 기준으로 계산하도록 맞췄다.

---

## 9. N+1 쿼리 (채팅)

**문제**: 메시지 목록을 가져온 뒤 **메시지마다** `users`를 조회해 발신자 이름을 붙였다. 메시지가 100개면 쿼리가 101번이다. 채팅방 목록도 방 하나당 쿼리를 5번 보냈다(그중 1번은 결과를 쓰지도 않았다).

**변경**: 발신자·참여자 id를 모아 `IN` 조회 1번으로 가져와 dict로 매핑한다.

**확인**: `test_채팅_메시지_발신자_이름은_한번에_조회한다`. 메시지 6개에도 `users` 조회가 1번인지 검증한다.

---

## 10. DB 무결성·인덱스 (`docs/migrations/001`)

| 추가 | 이유 |
|---|---|
| `coffee_chats.status` CHECK + NOT NULL | 허용 상태값 밖의 값 차단 (`reviews.rating`에는 이미 CHECK가 있었음) |
| `mentor_availability` CHECK `end_time > start_time` | 잘못된 슬롯 차단 |
| `mentor_availability.mentor_id`, `user_likes` FK | FK가 없어 존재하지 않는 멘토·사용자를 가리킬 수 있었음 (`liked_mentor_id` → `mentor_profiles.id`) |
| `coffee_chats (mentor_id, created_at desc)` 등 복합 인덱스 | 예약 목록 조회 패턴(`WHERE mentor_id = ? ORDER BY created_at DESC`)에 맞춤 |
| `location` GiST 인덱스 | `ST_DWithin` 반경 검색은 GiST가 있어야 인덱스를 탄다 |
| `idx_chat_rooms_coffee_chat` 삭제 | UNIQUE 제약이 이미 같은 인덱스를 만듦 (중복) |
| `update_connection_weights()` 삭제 | 어디에도 트리거로 연결되지 않았고, 연결하면 `users.id`를 `profile.id` FK 컬럼에 넣어 실패하는 함수 |

---

## 11. RLS (`docs/migrations/002`)

- 프론트는 anon 키로 Supabase에 직접 접근한다. 그래서 **RLS가 꺼진 테이블은 로그인한 누구나 전체를 읽고 쓸 수 있다.**
- 모든 테이블에 RLS를 켜고, 프론트가 실제로 쓰는 작업에만 최소 정책을 열었다.
- 채팅방·메시지·멘토 프로필 생성은 백엔드만 하도록 프론트용 INSERT 정책을 제거했다.
- 후기 작성은 "본인이 멘티이고 **승인된** 커피챗"일 때만 허용한다.

---

## 12. 기타

- 마이페이지 찜 목록 버그: 찜은 `liked_mentor_id`에 `mentor_profiles.id`를 저장하는데, 마이페이지는 이를 `users.id`로 조회했고 존재하지 않는 `company` 컬럼까지 요청해 목록이 비어 있었다. `mentor_profiles` 기준으로 조회하고 회사명은 `career_info`에서 추출하도록 수정했다. (마이그레이션 사전 점검에서 FK 대상이 코드와 다르다는 걸 발견해 함께 바로잡음)
- 프론트가 호출하는데 백엔드에 없던 `POST /api/chat/messages/{id}/read`를 추가했다.
- 사용하지 않고 스키마와도 맞지 않던 `api/coffeechats.py`(존재하지 않는 컬럼 사용, 인증 없음)를 삭제했다.
- 없는 테이블(`user_interactions`)에 쓰던 미사용 함수를 삭제했다.
- 인증 토큰 앞부분을 로그로 출력하던 코드를 삭제했다.
- `requirements.txt`에 누락됐던 `python-multipart`(회원가입 Form 처리)를 추가했다.
- 테스트와 GitHub Actions CI(백엔드 pytest, 프론트 빌드)를 추가했다.

---

## 13. 로그인하면 백엔드 전체 권한이 그 사용자로 바뀌던 문제

**문제**: RLS를 켠 뒤 회원가입에서 `users` INSERT가 403(`new row violates row-level security policy`)으로 실패했다.

**원인**: supabase-py 클라이언트는 `sign_up`이나 `sign_in`이 성공하면 **그 사용자의 토큰으로 Authorization 헤더를 교체**한다. 백엔드는 service_role 클라이언트 하나를 전역으로 공유하는데, 여기서 로그인까지 처리했다. 그래서 누군가 로그인하면 그 뒤의 모든 DB 요청(다른 사용자의 요청 포함)이 **마지막으로 로그인한 사용자 권한**으로 나갔다. RLS가 꺼져 있을 때는 드러나지 않던 문제다.

**변경**: 회원가입과 로그인은 요청마다 새로 만든 일회용 클라이언트(`new_auth_client`, 세션 저장 안 함)에서 처리하고, 공용 클라이언트는 DB 작업에만 쓴다.

**확인**: `test_로그인은_공용_클라이언트가_아닌_일회용_클라이언트로_한다`

---

## 남은 과제 (의도적으로 하지 않은 것)

- **FK 참조 대상 통일**: 같은 "멘토"를 테이블마다 `users.id`, `auth.users.id`, `mentor_profiles.id`로 다르게 참조한다. 통일하려면 데이터 이관과 프론트 전반 수정이 필요해, 이번 범위에서는 FK 누락만 보완했다.
- **AI 자기소개 생성 API 인증**: 회원가입 전에 호출되는 API라 로그인을 요구할 수 없다. 운영하려면 요청 수 제한(rate limit)이 필요하다.
- **채팅방 목록 쿼리**: 방마다 마지막 메시지와 안 읽은 수를 따로 조회한다(방당 2회). 뷰나 RPC 하나로 합칠 수 있다.
- **매칭 품질 평가**: 정답 셋이 없어 정확도를 측정하지 못했다.
