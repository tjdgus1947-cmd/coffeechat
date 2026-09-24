"""요청 본문의 user_id 가 아니라 토큰의 사용자만 수정할 수 있는지 검증"""
from fake_supabase import FakeSupabase

from app.api import profile


def test_자기소개_수정은_토큰_사용자에게만_적용된다(make_client, monkeypatch):
    monkeypatch.setattr(profile, "generate_embedding", lambda text: [0.0] * 8)
    fake = FakeSupabase({"mentee_profiles": [
        {"user_id": "me", "current_situation": "old"},
        {"user_id": "victim", "current_situation": "victim-old"},
    ]})

    res = make_client(fake, "me").post("/api/profile/update-introduction", json={
        "user_id": "victim", "role": "mentee", "introduction_text": "new",
    })

    assert res.status_code == 200
    rows = {r["user_id"]: r["current_situation"] for r in fake.tables["mentee_profiles"]}
    assert rows == {"me": "new", "victim": "victim-old"}


def test_위치_수정도_토큰_사용자에게만_적용된다(make_client):
    fake = FakeSupabase({"mentor_profiles": [
        {"user_id": "me", "location": None},
        {"user_id": "victim", "location": None},
    ]})

    res = make_client(fake, "me").post("/api/location/update", json={
        "user_id": "victim", "role": "mentor", "lon": 127.38, "lat": 36.35,
    })

    assert res.status_code == 200
    rows = {r["user_id"]: r["location"] for r in fake.tables["mentor_profiles"]}
    assert rows == {"me": "POINT(127.38 36.35)", "victim": None}


def test_슬롯_생성은_토큰_사용자의_멘토_프로필로_만들어진다(make_client):
    fake = FakeSupabase({
        "mentor_profiles": [{"id": "p-me", "user_id": "me"}, {"id": "p-victim", "user_id": "victim"}],
        "mentor_availability": [],
    })
    res = make_client(fake, "me").post("/api/availability/", json={
        "user_id": "victim", "start_time": "2026-10-01T10:00:00+09:00", "end_time": "2026-10-01T11:00:00+09:00",
    })

    assert res.status_code == 200
    assert fake.tables["mentor_availability"][0]["mentor_id"] == "p-me"


def test_종료가_시작보다_빠른_슬롯은_400(make_client):
    fake = FakeSupabase({"mentor_profiles": [{"id": "p-me", "user_id": "me"}], "mentor_availability": []})
    res = make_client(fake, "me").post("/api/availability/", json={
        "start_time": "2026-10-01T11:00:00+09:00", "end_time": "2026-10-01T10:00:00+09:00",
    })
    assert res.status_code == 400


def test_채팅_메시지_발신자_이름은_한번에_조회한다(make_client):
    fake = FakeSupabase({
        "chat_rooms": [{"id": "r1", "mentor_id": "a", "mentee_id": "b"}],
        "chat_messages": [
            {"id": f"m{i}", "chat_room_id": "r1", "sender_id": "a" if i % 2 else "b",
             "message": "hi", "created_at": f"2026-10-01T10:0{i}:00", "is_read": False}
            for i in range(6)
        ],
        "users": [{"id": "a", "full_name": "멘토"}, {"id": "b", "full_name": "멘티"}],
    })
    res = make_client(fake, "a").get("/api/chat/rooms/r1/messages")

    assert res.status_code == 200
    assert {m["sender_name"] for m in res.json()} == {"멘토", "멘티"}
    assert fake.calls.count(("users", "select")) == 1  # 메시지 6개여도 users 조회는 1번
