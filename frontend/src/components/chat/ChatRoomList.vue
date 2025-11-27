<!-- frontend/src/components/chat/ChatRoomList.vue -->
<template>
  <div class="chat-room-list-container">
    <div class="list-header">
      <h3>💬 채팅방 목록</h3>
      <span class="room-count">{{ chatRooms.length }}개</span>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>채팅방을 불러오는 중...</p>
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
          {{ getPartnerName(room).charAt(0) }}
        </div>

        <div class="room-info">
          <div class="room-header">
            <span class="partner-name">{{ getPartnerName(room) }}</span>
            <span class="room-time">{{ formatTime(room.last_message_time) }}</span>
          </div>

          <div class="room-preview">
            <p class="last-message">
              {{ room.last_message || '메시지가 없습니다.' }}
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
      <p class="empty-text">채팅방이 없습니다</p>
      <p class="empty-hint">승인된 커피챗이 있으면 채팅방이 생성됩니다.</p>
    </div>
  </div>
</template>

<script setup>
// 'onUnmounted'를 꼭 추가해야 합니다!
import { ref, onMounted, onUnmounted, computed } from 'vue';
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
  subscribeToListUpdates(); // ⭐️ 목록 실시간 구독 시작
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
.chat-room-list-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.list-header {
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.room-count {
  font-size: 14px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
}

.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

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
  transition: background-color 0.2s;
  border-bottom: 1px solid #f3f4f6;
}

.room-item:hover {
  background-color: #f9fafb;
}

.room-item.active {
  background-color: #ede9fe;
  border-left: 3px solid #6d28d9;
}

.room-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6d28d9, #a78bfa);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
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
  font-weight: 600;
  color: #111827;
}

.room-time {
  font-size: 12px;
  color: #9ca3af;
}

.room-preview {
  display: flex;
  align-items: center;
  gap: 8px;
}

.last-message {
  flex: 1;
  font-size: 14px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin: 0;
}

.unread-badge {
  background: #ef4444;
  color: white;
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #9ca3af;
  margin: 0;
}
</style>