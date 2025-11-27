
import uuid
from datetime import datetime, timedelta
from app.core.config import supabase
import traceback

try:
    # 테스트용 멘토 user_id (실제 멘티 계정에서 사용하는 멘토 UUID로 교체 필요)
    test_mentor_user_id = "11111111-1111-1111-1111-111111111111"  # 예시 UUID

    # 1. mentor_profiles에 멘토 프로필 생성
    profile_payload = {
        "user_id": test_mentor_user_id,
        "full_name": "테스트 멘토",
        "career_info": "테스트 경력",
        "company": "테스트 회사",
        "description": "테스트 멘토 설명"
    }
    profile_res = supabase.table("mentor_profiles").insert(profile_payload).execute()
    mentor_profile_id = profile_res.data[0]["id"]
    print(f"멘토 프로필 생성: {mentor_profile_id}")

    # 2. mentor_availability에 예약 가능 슬롯 생성
    now = datetime.now()
    slot_payload = {
        "mentor_id": str(mentor_profile_id),
        "start_time": (now + timedelta(days=1)).isoformat(),
        "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
        "is_booked": False
    }
    slot_res = supabase.table("mentor_availability").insert(slot_payload).execute()
    print(f"예약 가능 슬롯 생성: {slot_res.data}")
except Exception as e:
    print("[오류 발생]")
    traceback.print_exc()
