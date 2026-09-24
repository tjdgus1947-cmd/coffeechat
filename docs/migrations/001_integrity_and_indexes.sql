-- =====================================================================
-- 001_integrity_and_indexes.sql
-- 목적
--   1. 같은 슬롯의 중복 예약을 DB 레벨에서 차단
--   2. 상태값·시간값 무결성 제약 추가
--   3. 참조 무결성(FK)이 빠진 컬럼 보완
--   4. 조회 패턴에 맞는 인덱스 추가, 중복 인덱스 제거
--   5. 임베딩 후보 검색을 DB로 내리는 match_candidates 함수 추가
--
-- 트랜잭션으로 묶었으므로 중간에 하나라도 실패하면 전체가 롤백된다.
-- 실행 전 000_precheck.sql 결과가 모두 0행인지 확인할 것.
-- =====================================================================
begin;

-- ---------------------------------------------------------------------
-- 1. 중복 예약 차단
--    예약 생성 시 availability_id가 채워지고, 승인/거절 시 NULL로 바뀐다.
--    PostgreSQL의 UNIQUE는 NULL끼리 중복으로 보지 않으므로
--    "대기 중인 예약은 슬롯당 1건"이 보장된다.
-- ---------------------------------------------------------------------
alter table coffee_chats
    add constraint coffee_chats_availability_id_key unique (availability_id);

-- ---------------------------------------------------------------------
-- 2. 무결성 제약
-- ---------------------------------------------------------------------
alter table coffee_chats
    alter column status set default 'pending',
    alter column status set not null,
    add constraint coffee_chats_status_check
        check (status in ('pending', 'approved', 'rejected'));

update mentor_availability set is_booked = false where is_booked is null;
alter table mentor_availability
    alter column is_booked set not null,
    add constraint mentor_availability_time_check check (end_time > start_time);

-- ---------------------------------------------------------------------
-- 3. 빠져 있던 FK
--    mentor_availability.mentor_id 는 mentor_profiles.id 를 저장한다 (availability.py 기준)
--    user_likes 의 두 컬럼은 users.id 를 저장한다 (MyPageView.vue 기준)
-- ---------------------------------------------------------------------
alter table mentor_availability
    add constraint mentor_availability_mentor_id_fkey
        foreign key (mentor_id) references mentor_profiles(id) on delete cascade;

alter table user_likes
    add constraint user_likes_user_id_fkey
        foreign key (user_id) references users(id) on delete cascade,
    add constraint user_likes_liked_mentor_id_fkey
        foreign key (liked_mentor_id) references users(id) on delete cascade;

-- ---------------------------------------------------------------------
-- 4. 인덱스
-- ---------------------------------------------------------------------
-- 멘토/멘티별 예약 목록 (bookings.py: eq(mentor_id|mentee_id).order(created_at desc))
create index if not exists idx_coffee_chats_mentor_created
    on coffee_chats (mentor_id, created_at desc);
create index if not exists idx_coffee_chats_mentee_created
    on coffee_chats (mentee_id, created_at desc);

-- 멘토별 가능 시간 조회 (availability.py: eq(mentor_id))
create index if not exists idx_mentor_availability_mentor_start
    on mentor_availability (mentor_id, start_time);

-- 반경 검색 (nearby_mentors: ST_DWithin) 은 GiST 인덱스가 있어야 인덱스를 탄다
create index if not exists idx_mentor_profiles_location
    on mentor_profiles using gist (location);
create index if not exists idx_mentee_profiles_location
    on mentee_profiles using gist (location);

-- 벡터 인덱스는 차원이 고정된 컬럼에만 만들 수 있다 → vector(1024) 로 변환 후 HNSW 생성
-- vector_cosine_ops: 코드가 코사인 거리(<=>)를 쓰므로 같은 연산자 클래스를 사용
alter table mentor_profiles alter column embedding type vector(1024);
alter table mentee_profiles alter column embedding type vector(1024);
create index if not exists idx_mentor_profiles_embedding
    on mentor_profiles using hnsw (embedding vector_cosine_ops);
create index if not exists idx_mentee_profiles_embedding
    on mentee_profiles using hnsw (embedding vector_cosine_ops);

-- chat_rooms.coffee_chat_id 는 UNIQUE 제약이 이미 인덱스를 만들므로 중복 인덱스 제거
drop index if exists idx_chat_rooms_coffee_chat;

-- ---------------------------------------------------------------------
-- 5. 정리
--    update_connection_weights 는 어떤 테이블에도 트리거로 연결돼 있지 않고,
--    연결하면 users.id 를 profile.id 컬럼에 넣어 FK 위반이 나는 함수라 제거한다.
-- ---------------------------------------------------------------------
drop function if exists public.update_connection_weights();

-- ---------------------------------------------------------------------
-- 6. 매칭 후보 검색 함수
--    기존: 상대 역할 프로필 "전체"를 API 서버로 가져와 파이썬에서 유사도 계산
--    변경: DB에서 코사인 거리 순으로 상위 match_count 명만 반환 (HNSW 인덱스 사용)
--    ORDER BY 에 거리 식을 그대로 써야 인덱스를 탄다.
-- ---------------------------------------------------------------------
create or replace function public.match_candidates(
    query_embedding  vector,
    target_role      text,          -- 'mentor' | 'mentee' : 찾을 상대의 역할
    exclude_user_id  uuid,
    match_count      integer default 200
)
returns table (
    id           uuid,
    user_id      uuid,
    full_name    text,
    profile_text text,
    embedding    vector,
    location     geography,
    similarity   double precision
)
language sql stable
as $$
    (
        select mp.id, mp.user_id, u.full_name, mp.career_info,
               mp.embedding, mp.location,
               1 - (mp.embedding <=> query_embedding)
        from mentor_profiles mp
        join users u on u.id = mp.user_id
        where target_role = 'mentor'
          and mp.embedding is not null
          and mp.location  is not null
          and mp.user_id <> exclude_user_id
        order by mp.embedding <=> query_embedding
        limit match_count
    )
    union all
    (
        select me.id, me.user_id, u.full_name, me.current_situation,
               me.embedding, me.location,
               1 - (me.embedding <=> query_embedding)
        from mentee_profiles me
        join users u on u.id = me.user_id
        where target_role = 'mentee'
          and me.embedding is not null
          and me.location  is not null
          and me.user_id <> exclude_user_id
        order by me.embedding <=> query_embedding
        limit match_count
    );
$$;

commit;
