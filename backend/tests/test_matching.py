"""매칭 파이프라인·점수 로직 테스트"""
from fake_supabase import FakeSupabase, vec_str, wkt_point

from app.services.hybrid_search_service import BM25, tokenize
from app.services.matching_service import calculate_distance_km, distance_to_score
from app.services.reranking_service import rerank_candidates, to_probability


# ---------- 순수 함수 ----------

def test_한글은_bigram으로_쪼개_조사_차이를_흡수한다():
    assert "데이" in tokenize("데이터를") and "데이" in tokenize("데이터")
    assert tokenize("Python SQL") == ["python", "sql"]


def test_BM25는_키워드가_겹치는_문서를_더_높게_본다():
    bm25 = BM25(["데이터 엔지니어 경력 5년", "프론트엔드 개발자", "마케팅 기획"])
    scores = bm25.get_scores("데이터 엔지니어를 꿈꿉니다")
    assert scores[0] > scores[1] and scores[0] > scores[2]


def test_BM25는_빈_말뭉치에서도_에러가_나지_않는다():
    assert BM25([]).get_scores("아무거나") == []


def test_거리_점수는_가까울수록_높고_최대거리_밖은_0():
    daejeon, sejong, busan = (36.35, 127.38), (36.48, 127.29), (35.18, 129.08)
    near = calculate_distance_km(*daejeon, *sejong)
    far = calculate_distance_km(*daejeon, *busan)
    assert near < far
    assert distance_to_score(near) > distance_to_score(far) == 0.0


def test_리랭커_점수는_0에서_100_사이로_정규화된다():
    assert 0 <= to_probability(-50) < 0.01
    assert 0.99 < to_probability(50) <= 1
    assert to_probability(0) == 0.5
    assert to_probability(-1000) == 0.0                 # 큰 음수에서도 오버플로 없음


def test_리랭킹은_final_score를_갱신해_다음_단계로_넘긴다():
    cands = [
        {"id": "a", "text": "마케팅 기획자", "final_score": 60.0},
        {"id": "b", "text": "데이터 엔지니어 파이프라인", "final_score": 58.0},
    ]
    out = rerank_candidates("데이터 엔지니어 파이프라인 경험", cands, top_k=2)
    assert out[0]["id"] == "b"                          # 리랭커가 순위를 뒤집음
    assert out[0]["final_score"] != 58.0                # final_score 자체가 갱신됨
    assert all(0 <= c["rerank_score"] <= 100 for c in out)


# ---------- API ----------

MY_ID = "u-mentee"
EMB = [0.1] * 8


def matching_fake(extra_bookings=0):
    candidates = [
        {"id": f"p{i}", "user_id": f"u{i}", "full_name": f"멘토{i}",
         "profile_text": text, "embedding": vec_str(EMB), "location": wkt_point(lon, 36.35),
         "similarity": 0.9}
        for i, (text, lon) in enumerate([
            ("회사: 네이버, 데이터 엔지니어, Spark Airflow", 127.38),
            ("회사: 카카오, 프론트엔드 개발자", 127.39),
            ("회사: 쿠팡, 마케팅 기획", 127.40),
        ])
    ]
    tables = {
        "mentee_profiles": [{
            "user_id": MY_ID, "embedding": vec_str(EMB), "location": wkt_point(127.38, 36.35),
            "current_situation": "데이터 엔지니어를 준비 중입니다. Spark 공부 중",
        }],
        "coffee_chats": [],
    }
    return FakeSupabase(tables, rpc_results={"match_candidates": candidates})


def test_매칭은_토큰_사용자의_프로필로_DB_후보검색을_호출한다(make_client):
    fake = matching_fake()
    res = make_client(fake, MY_ID).get(
        "/api/matching/find-matches", params={"role": "mentee", "limit": 2, "user_id": "someone-else"}
    )

    assert res.status_code == 200
    name, params = fake.rpc_calls[0]
    assert name == "match_candidates"
    assert params["target_role"] == "mentor"
    assert params["exclude_user_id"] == MY_ID            # 쿼리의 user_id 가 아니라 토큰 사용자
    matches = res.json()["matches"]
    assert len(matches) == 2
    assert matches[0]["name"] == "멘토0"                 # 키워드가 가장 많이 겹치는 멘토
    assert {"final_score", "distance_km", "text_similarity"} <= set(matches[0])


def test_프로필이_없으면_404(make_client):
    fake = matching_fake()
    fake.tables["mentee_profiles"] = []
    res = make_client(fake, MY_ID).get("/api/matching/find-matches", params={"role": "mentee"})
    assert res.status_code == 404                        # 이전 코드에서는 500


def test_잘못된_역할은_422(make_client):
    res = make_client(matching_fake(), MY_ID).get("/api/matching/find-matches", params={"role": "admin"})
    assert res.status_code == 422


def test_내_프로필은_전체_스캔이_아니라_1건만_조회한다(make_client):
    fake = matching_fake()
    make_client(fake, MY_ID).get("/api/matching/find-matches", params={"role": "mentee"})
    profile_reads = [c for c in fake.calls if c == ("mentee_profiles", "select")]
    assert len(profile_reads) == 1
