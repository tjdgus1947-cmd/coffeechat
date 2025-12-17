<template>
  <div class="chat-room-list-container">
    <div class="list-header">
      <h3>📜 Today's Orders</h3>
      <span class="room-count">{{ chatRooms.length }} TABLES</span>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>주문 내역 확인 중...</p>
    </div>

    <div v-else-if="chatRooms.length > 0" class="room-list">
      <div
        v-for="room in chatRooms"
        :key="room.id"
        class="room-item"
        :class="{ active: selectedRoomId === room.id }"
        @click="selectRoom(room)"
      >
        <div class="room-avatar">
          <span class="latte-art">☕</span>
        </div>

        <div class="room-info">
          <div class="room-header">
            <span class="partner-name">{{ getPartnerName(room) }}</span>
            <span class="room-time">{{ formatTime(room.last_message_time) }}</span>
          </div>

          <div class="room-preview">
            <p class="last-message">
              {{ room.last_message || '대화를 시작해보세요!' }}
            </p>
            <span v-if="room.unread_count > 0" class="unread-badge">
              {{ room.unread_count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p class="empty-icon">📭</p>
      <p class="empty-text">아직 주문(채팅)이 없습니다</p>
      <p class="empty-hint">커피챗을 신청하고 승인받아보세요!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';
import { supabase } from '@/services/supabase';

const authStore = useAuthStore();
const chatRooms = ref([]);
const isLoading = ref(true);
const selectedRoomId = ref(null);
const listSubscription = ref(null);

const emit = defineEmits(['select-room']);

onMounted(async () => {
  await fetchChatRooms();
  subscribeToListUpdates(); // 목록 실시간 구독 시작
});

onUnmounted(() => {
  if (listSubscription.value) {
    supabase.removeChannel(listSubscription.value);
  }
});

function subscribeToListUpdates() {
  listSubscription.value = supabase
    .channel('room-list-updates')
    .on(
      'postgres_changes',
      {
        event: 'INSERT',
        schema: 'public',
        table: 'chat_messages'
      },
      (payload) => {
        const newMessage = payload.new;
        
        // 수신된 메시지가 현재 목록에 있는 방인지 확인
        const roomIndex = chatRooms.value.findIndex(room => room.id === newMessage.chat_room_id);
        
        if (roomIndex !== -1) {
          const room = chatRooms.value[roomIndex];
          
          // 1. 마지막 메시지와 시간 업데이트
          room.last_message = newMessage.message;
          room.last_message_time = newMessage.created_at;
          
          // 2. 안 읽은 메시지 카운트 증가
          // (내가 보낸 게 아니고, 현재 선택된 방이 아닐 때만)
          if (newMessage.sender_id !== authStore.userId && selectedRoomId.value !== room.id) {
            room.unread_count = (room.unread_count || 0) + 1;
          }
          
          // 3. 업데이트된 방을 목록 최상단으로 이동 (Sort)
          chatRooms.value.splice(roomIndex, 1);
          chatRooms.value.unshift(room);
        } else {
            // 새로운 방이 생겼을 수도 있으므로 목록을 다시 불러오는 것도 방법
            // fetchChatRooms(); 
        }
      }
    )
    .subscribe();
}

async function fetchChatRooms() {
  isLoading.value = true;
  try {
    const response = await api.get('/chat/rooms');
    chatRooms.value = response.data;
  } catch (error) {
    console.error('채팅방 목록 조회 실패:', error);
    chatRooms.value = [];
  } finally {
    isLoading.value = false;
  }
}

function getPartnerName(room) {
  if (authStore.userRole === 'mentor') {
    return room.mentee_name || '멘티';
  } else {
    return room.mentor_name || '멘토';
  }
}

function selectRoom(room) {
  selectedRoomId.value = room.id;
  // 선택 시 뱃지 초기화 (UI 상에서만 먼저 반영)
  room.unread_count = 0; 
  emit('select-room', room);
}

function formatTime(dateString) {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return '방금 전';
  if (diffMins < 60) return `${diffMins}분 전`;
  if (diffHours < 24) return `${diffHours}시간 전`;
  if (diffDays < 7) return `${diffDays}일 전`;
  
  return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
}

defineExpose({ fetchChatRooms });
</script>

<style scoped>
/* 🎨 카페 테마 적용 스타일 */
.chat-room-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fffbf7; /* 아주 연한 크림색 배경 */
  border-right: 1px dashed var(--border-color, #D1A872); /* 우측 점선 테두리 */
}

/* 헤더 스타일 */
.list-header {
  padding: 20px;
  border-bottom: 2px solid var(--primary-color, #361205); /* 헤더 구분선은 진하게 */
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fcf9f2;
}

.list-header h3 {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--primary-color, #361205);
  margin: 0;
  font-family: 'Courier New', monospace; /* 영수증 폰트 느낌 */
  letter-spacing: -0.5px;
}

.room-count {
  font-size: 0.8rem;
  color: #fff;
  background-color: var(--point-color, #DF8723);
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
}

/* 로딩 상태 */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #8A5A34;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: var(--point-color, #DF8723);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 채팅방 리스트 */
.room-list {
  flex: 1;
  overflow-y: auto;
}

.room-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all 0.2s;
  border-bottom: 1px solid #efe5d9; /* 연한 갈색 구분선 */
}

.room-item:hover {
  background-color: #f2ebe0; /* 호버 시 베이지색 */
}

/* 🔥 선택된 방 스타일 변경 */
.room-item.active {
  background-color: #fff;
  border-left: 5px solid var(--primary-color, #361205); /* 진한 갈색 포인트바 */
  box-shadow: 0 4px 12px rgba(54, 18, 5, 0.1);
}

.room-item.active .partner-name {
  color: var(--point-color, #DF8723);
  font-weight: 900;
}

/* 라떼 아트 아바타 */
.room-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #eaddcf; /* 라떼 거품 색 */
  border: 2px solid #d1bfa8;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.latte-art {
  font-size: 20px;
  filter: grayscale(0.2);
}

.room-info {
  flex: 1;
  min-width: 0;
}

.room-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.partner-name {
  font-size: 15px;
  font-weight: 700;
  color: #4e342e;
}

.room-time {
  font-size: 11px;
  color: #a1887f;
}

.room-preview {
  display: flex;
  align-items: center;
  gap: 8px;
}

.last-message {
  flex: 1;
  font-size: 13px;
  color: #8d6e63;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}

/* 뱃지: 커피 체리(레드) 색상 */
.unread-badge {
  background-color: #b71c1c; 
  color: white;
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 50%;
  min-width: 18px;
  text-align: center;
}

/* 빈 상태 */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #8A5A34;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  margin: 0;
  opacity: 0.8;
}
</style>