# backend/app/api/chat.py

"""
채팅 API
- 채팅방 목록 조회
- 채팅 메시지 조회
- 메시지 전송
- 🔥 안 읽은 메시지 개수 조회 (신규 추가)
"""

from fastapi import APIRouter, HTTPException, Depends
from app.core.config import supabase
from typing import List, Optional
from pydantic import BaseModel
from .auth import get_current_user_id
from datetime import datetime

router = APIRouter()

# --- Pydantic 모델 ---

class ChatRoomInfo(BaseModel):
    id: str
    coffee_chat_id: str
    mentor_id: str
    mentee_id: str
    mentor_name: Optional[str] = None
    mentee_name: Optional[str] = None
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0
    created_at: datetime

class ChatMessage(BaseModel):
    id: str
    chat_room_id: str
    sender_id: str
    sender_name: Optional[str] = None
    message: str
    created_at: datetime
    is_read: bool

class SendMessageRequest(BaseModel):
    chat_room_id: str
    message: str


# ----------------------------------------------------
# 📌 1) 전체 채팅방 목록 조회
# ----------------------------------------------------

@router.get("/api/chat/rooms", response_model=List[ChatRoomInfo])
def get_my_chat_rooms(current_user_id: str = Depends(get_current_user_id)):
    """내 채팅방 목록 조회"""
    try:
        # 1. 내가 속한 채팅방 조회
        response = supabase.table('chat_rooms') \
            .select('*') \
            .or_(f'mentor_id.eq.{current_user_id},mentee_id.eq.{current_user_id}') \
            .order('updated_at', desc=True) \
            .execute()
        
        if not response.data:
            return []
        
        # 방 참여자 이름은 IN 조회 1번으로 가져온다 (이전: 방마다 users 조회 3번)
        user_ids = list({uid for room in response.data for uid in (room['mentor_id'], room['mentee_id'])})
        users_response = supabase.table('users').select('id, full_name').in_('id', user_ids).execute()
        name_by_id = {u['id']: u.get('full_name') for u in (users_response.data or [])}

        chat_rooms = []

        for room in response.data:
            # 마지막 메시지 (idx_chat_messages_room 인덱스 사용)
            last_msg = supabase.table('chat_messages') \
                .select('message, created_at') \
                .eq('chat_room_id', room['id']) \
                .order('created_at', desc=True) \
                .limit(1) \
                .execute()

            # 읽지 않은 메시지 수
            unread_count = supabase.table('chat_messages') \
                .select('id', count='exact') \
                .eq('chat_room_id', room['id']) \
                .eq('is_read', False) \
                .neq('sender_id', current_user_id) \
                .execute()

            chat_rooms.append(ChatRoomInfo(
                id=room['id'],
                coffee_chat_id=room['coffee_chat_id'],
                mentor_id=room['mentor_id'],
                mentee_id=room['mentee_id'],
                mentor_name=name_by_id.get(room['mentor_id']),
                mentee_name=name_by_id.get(room['mentee_id']),
                last_message=last_msg.data[0]['message'] if last_msg.data else None,
                last_message_time=last_msg.data[0]['created_at'] if last_msg.data else None,
                unread_count=unread_count.count or 0,
                created_at=room['created_at']
            ))
        
        return chat_rooms
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 채팅방 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ----------------------------------------------------
# 📌 2) 채팅방 메시지 조회 + 읽음 처리
# ----------------------------------------------------

@router.get("/api/chat/rooms/{room_id}/messages", response_model=List[ChatMessage])
def get_chat_messages(
    room_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """채팅방 메시지 조회"""
    try:
        # 1. 권한 확인
        room_check = supabase.table('chat_rooms') \
            .select('*') \
            .eq('id', room_id) \
            .or_(f'mentor_id.eq.{current_user_id},mentee_id.eq.{current_user_id}') \
            .execute()
        
        if not room_check.data:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        
        # 2. 메시지 조회
        messages_response = supabase.table('chat_messages') \
            .select('*') \
            .eq('chat_room_id', room_id) \
            .order('created_at', desc=False) \
            .execute()
        
        if not messages_response.data:
            return []
        
        # 3. 발신자 이름 매핑
        #    (이전: 메시지마다 users 조회 → 메시지 N개면 쿼리 N번, N+1 문제)
        #    (변경: 발신자 id 를 모아 IN 조회 1번 → dict 로 매핑)
        sender_ids = list({msg['sender_id'] for msg in messages_response.data})
        users_response = supabase.table('users') \
            .select('id, full_name') \
            .in_('id', sender_ids) \
            .execute()
        name_by_id = {u['id']: u.get('full_name') for u in (users_response.data or [])}

        messages = []
        for msg in messages_response.data:
            messages.append(ChatMessage(
                id=msg['id'],
                chat_room_id=msg['chat_room_id'],
                sender_id=msg['sender_id'],
                sender_name=name_by_id.get(msg['sender_id']),
                message=msg['message'],
                created_at=msg['created_at'],
                is_read=msg['is_read']
            ))
        
        # 4. 읽음 처리 (상대가 보낸 메시지)
        supabase.table('chat_messages') \
            .update({'is_read': True}) \
            .eq('chat_room_id', room_id) \
            .neq('sender_id', current_user_id) \
            .eq('is_read', False) \
            .execute()
        
        return messages
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 메시지 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ----------------------------------------------------
# 📌 3) 메시지 전송
# ----------------------------------------------------

@router.post("/api/chat/messages")
def send_message(
    request: SendMessageRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """메시지 전송"""
    try:
        # 1. 권한 확인
        room_check = supabase.table('chat_rooms') \
            .select('*') \
            .eq('id', request.chat_room_id) \
            .or_(f'mentor_id.eq.{current_user_id},mentee_id.eq.{current_user_id}') \
            .execute()
        
        if not room_check.data:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")
        
        # 2. 메시지 저장
        message_response = supabase.table('chat_messages').insert({
            'chat_room_id': request.chat_room_id,
            'sender_id': current_user_id,
            'message': request.message,
            'is_read': False
        }).execute()
        
        # 3. 채팅방 updated_at 갱신
        supabase.table('chat_rooms') \
            .update({'updated_at': datetime.utcnow().isoformat()}) \
            .eq('id', request.chat_room_id) \
            .execute()
        
        return {"message": "전송 완료", "data": message_response.data[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 메시지 전송 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))



# ----------------------------------------------------
# 📌 3-1) 메시지 1건 읽음 처리 (프론트 ChatRoom.vue 가 실시간 수신 시 호출)
# ----------------------------------------------------

@router.post("/api/chat/messages/{message_id}/read")
def mark_message_read(
    message_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """내가 참여한 방의, 상대가 보낸 메시지만 읽음 처리한다."""
    try:
        msg = supabase.table('chat_messages') \
            .select('id, chat_room_id, sender_id') \
            .eq('id', message_id) \
            .limit(1) \
            .execute()
        if not msg.data:
            raise HTTPException(status_code=404, detail="메시지를 찾을 수 없습니다.")

        room_check = supabase.table('chat_rooms') \
            .select('id') \
            .eq('id', msg.data[0]['chat_room_id']) \
            .or_(f'mentor_id.eq.{current_user_id},mentee_id.eq.{current_user_id}') \
            .execute()
        if not room_check.data:
            raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

        if msg.data[0]['sender_id'] != current_user_id:
            supabase.table('chat_messages') \
                .update({'is_read': True}) \
                .eq('id', message_id) \
                .execute()

        return {"message": "읽음 처리 완료"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 읽음 처리 실패: {e}")
        raise HTTPException(status_code=500, detail="읽음 처리 중 오류가 발생했습니다.")



# ----------------------------------------------------
# 📌 4) 🔥 추가: 전체 안 읽은 메시지 개수 반환
# ----------------------------------------------------

@router.get("/api/chat/unread-count")
def get_unread_chat_count(current_user_id: str = Depends(get_current_user_id)):
    """
    현재 로그인한 유저의 '안 읽은 메시지 개수' 반환
    """
    try:
        # 1) 내가 속한 채팅방 가져오기
        rooms_resp = (
            supabase.table("chat_rooms")
            .select("id")
            .or_(f"mentor_id.eq.{current_user_id},mentee_id.eq.{current_user_id}")
            .execute()
        )

        room_ids = [r["id"] for r in (rooms_resp.data or [])]

        if not room_ids:
            return {"unread_count": 0}

        # 2) 그 방들의 읽지 않은 메시지 개수
        msgs_resp = (
            supabase.table("chat_messages")
            .select("id", count="exact")
            .in_("chat_room_id", room_ids)
            .eq("is_read", False)
            .neq("sender_id", current_user_id)
            .execute()
        )

        unread_count = msgs_resp.count or 0
        return {"unread_count": unread_count}

    except HTTPException:
        raise
    except Exception as e:
        print("❌ unread-count 조회 실패:", e)
        raise HTTPException(status_code=500, detail="unread-count 조회 실패")
