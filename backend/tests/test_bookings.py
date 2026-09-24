"""예약 생성·상태 변경 API 테스트"""
from fake_supabase import FakeSupabase

MENTEE = "u-mentee"
MENTOR_USER = "u-mentor"
MENTOR_PROFILE = "p-mentor"
SLOT = "slot-1"


def base_tables(is_booked=False):
    return {
        "mentor_profiles": [{"id": MENTOR_PROFILE, "user_id": MENTOR_USER}],
        "mentor_availability": [{
            "id": SLOT, "mentor_id": MENTOR_PROFILE, "is_booked": is_booked,
            "start_time": "2026-10-01T10:00:00+09:00", "end_time": "2026-10-01T11:00:00+09:00",
        }],
        "coffee_chats": [],
        "chat_rooms": [],
    }


def book(client, mentor_id=MENTOR_PROFILE, slot=SLOT):
    return client.post("/api/bookings/create", json={
        "mentor_id": mentor_id, "availability_slot_id": slot, "concern": "진로 고민",
    })


def test_예약_성공시_슬롯이_선점되고_예약이_생성된다(make_client):
    fake = FakeSupabase(base_tables())
    res = book(make_client(fake, MENTEE))

    assert res.status_code == 200
    assert fake.tables["mentor_availability"][0]["is_booked"] is True
    chat = fake.tables["coffee_chats"][0]
    assert chat["mentee_id"] == MENTEE
    assert chat["mentor_id"] == MENTOR_USER          # coffee_chats 는 users.id 를 저장
    assert chat["status"] == "pending"


def test_이미_예약된_슬롯은_409(make_client):
    fake = FakeSupabase(base_tables(is_booked=True))
    res = book(make_client(fake, MENTEE))

    assert res.status_code == 409                     # 이전 코드에서는 500 으로 바뀌던 응답
    assert fake.tables["coffee_chats"] == []


def test_없는_슬롯은_404(make_client):
    fake = FakeSupabase(base_tables())
    res = book(make_client(fake, MENTEE), slot="no-such-slot")
    assert res.status_code == 404


def test_다른_멘토의_슬롯으로는_예약할_수_없다(make_client):
    tables = base_tables()
    tables["mentor_profiles"].append({"id": "p-other", "user_id": "u-other"})
    fake = FakeSupabase(tables)
    res = book(make_client(fake, MENTEE), mentor_id="p-other")

    assert res.status_code == 400
    assert fake.tables["mentor_availability"][0]["is_booked"] is False


def test_예약_INSERT가_실패하면_선점한_슬롯을_되돌린다(make_client):
    fake = FakeSupabase(base_tables())

    def fail(_payload):
        raise RuntimeError("duplicate key value violates unique constraint")
    fake.insert_hooks["coffee_chats"] = fail

    res = book(make_client(fake, MENTEE))

    assert res.status_code == 500
    assert fake.tables["mentor_availability"][0]["is_booked"] is False


def test_두번째_동시_요청은_선점에_실패한다(make_client):
    """두 요청이 모두 슬롯 조회를 통과해도, 조건부 UPDATE 때문에 한 명만 예약된다."""
    fake = FakeSupabase(base_tables())
    client = make_client(fake, MENTEE)

    first = book(client)
    second = book(client)

    assert first.status_code == 200
    assert second.status_code == 409
    assert len(fake.tables["coffee_chats"]) == 1


def pending_booking_tables():
    tables = base_tables(is_booked=True)
    tables["coffee_chats"].append({
        "id": "b-1", "status": "pending", "availability_id": SLOT,
        "mentor_id": MENTOR_USER, "mentee_id": MENTEE,
    })
    return tables


def test_승인하면_채팅방이_생기고_슬롯은_삭제된다(make_client):
    fake = FakeSupabase(pending_booking_tables())
    res = make_client(fake, MENTOR_USER).put("/api/bookings/b-1/status", json={"status": "approved"})

    assert res.status_code == 200
    assert fake.tables["coffee_chats"][0]["status"] == "approved"
    assert fake.tables["coffee_chats"][0]["availability_id"] is None
    assert len(fake.tables["chat_rooms"]) == 1
    assert fake.tables["mentor_availability"] == []


def test_거절하면_슬롯이_다시_예약_가능해진다(make_client):
    fake = FakeSupabase(pending_booking_tables())
    res = make_client(fake, MENTOR_USER).put("/api/bookings/b-1/status", json={"status": "rejected"})

    assert res.status_code == 200
    assert fake.tables["mentor_availability"][0]["is_booked"] is False
    assert fake.tables["chat_rooms"] == []


def test_이미_처리된_예약은_다시_처리할_수_없다(make_client):
    fake = FakeSupabase(pending_booking_tables())
    client = make_client(fake, MENTOR_USER)

    assert client.put("/api/bookings/b-1/status", json={"status": "approved"}).status_code == 200
    again = client.put("/api/bookings/b-1/status", json={"status": "approved"})

    assert again.status_code == 409
    assert len(fake.tables["chat_rooms"]) == 1       # 채팅방 중복 생성 없음


def test_허용되지_않은_상태값은_422(make_client):
    fake = FakeSupabase(pending_booking_tables())
    res = make_client(fake, MENTOR_USER).put("/api/bookings/b-1/status", json={"status": "done"})
    assert res.status_code == 422


def test_다른_멘토의_예약은_처리할_수_없다(make_client):
    fake = FakeSupabase(pending_booking_tables())
    res = make_client(fake, "u-someone-else").put("/api/bookings/b-1/status", json={"status": "approved"})
    assert res.status_code == 404
    assert fake.tables["coffee_chats"][0]["status"] == "pending"
