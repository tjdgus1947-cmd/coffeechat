<!-- frontend/src/components/chat/ChatRoom.vue -->
<template>
  <div class="chat-room-container">
    <div v-if="!selectedRoom" class="no-selection">
      <p class="no-selection-icon">💬</p>
      <p class="no-selection-text">채팅방을 선택해주세요</p>
    </div>

    <div v-else class="chat-room">
      <!-- 채팅방 헤더 -->
      <div class="chat-header">
        <div class="header-info">
          <div class="partner-avatar">
            {{ partnerName.charAt(0) }}
          </div>
          <div>
            <h3>{{ partnerName }}</h3>
            <p class="chat-subtitle">커피챗 약속 조율하기</p>
          </div>
        </div>
      </div>

      <!-- 메시지 영역 -->
      <div class="messages-container" ref="messagesContainer">
        <div v-if="isLoadingMessages" class="loading-messages">
          <div class="spinner-small"></div>
          <p>메시지를 불러오는 중...</p>
        </div>

        <div v-else-if="messages.length === 0" class="empty-messages">
          <p>아직 메시지가 없습니다.</p>
          <p>첫 메시지를 보내보세요! 👋</p>
        </div>

        <div v-else class="messages-list">
          <div
            v-for="message in messages"
            :key="message.id"
            class="message-wrapper"
            :class="{ mine: message.sender_id === currentUserId }"
          >
            <div class="message-bubble">
              <p class="message-text">{{ message.message }}</p>
              <span class="message-time">
                {{ formatMessageTime(message.created_at) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 입력 영역 -->
      <div class="input-container">
        <textarea
          v-model="newMessage"
          @keydown.enter.prevent="handleSend"
          placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
          rows="2"
          class="message-input"
        ></textarea>
        <button
          @click="handleSend"
          :disabled="!newMessage.trim() || isSending"
          class="send-button"
        >
          <span v-if="!isSending">📨</span>
          <span v-else>⏳</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';

const authStore = useAuthStore();
const props = defineProps({
  selectedRoom: Object
});

const messages = ref([]);
const newMessage = ref('');
const isLoadingMessages = ref(false);
const isSending = ref(false);
const messagesContainer = ref(null);

const currentUserId = computed(() => authStore.userId);

const partnerName = computed(() => {
  if (!props.selectedRoom) return '';
  if (authStore.userRole === 'mentor') {
    return props.selectedRoom.mentee_name || '멘티';
  } else {
    return props.selectedRoom.mentor_name || '멘토';
  }
});

watch(() => props.selectedRoom, async (newRoom) => {
  if (newRoom) {
    await fetchMessages();
  }
}, { immediate: true });

async function fetchMessages() {
  if (!props.selectedRoom) return;
  
  isLoadingMessages.value = true;
  try {
    const response = await api.get(`/chat/rooms/${props.selectedRoom.id}/messages`);
    messages.value = response.data;
    
    await nextTick();
    scrollToBottom();
  } catch (error) {
    console.error('메시지 조회 실패:', error);
    messages.value = [];
  } finally {
    isLoadingMessages.value = false;
  }
}

async function handleSend() {
  if (!newMessage.value.trim() || isSending.value) return;
  
  isSending.value = true;
  try {
    await api.post('/chat/messages', {
      chat_room_id: props.selectedRoom.id,
      message: newMessage.value.trim()
    });
    
    newMessage.value = '';
    await fetchMessages();
  } catch (error) {
    console.error('메시지 전송 실패:', error);
    alert('메시지 전송에 실패했습니다.');
  } finally {
    isSending.value = false;
  }
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
}

function formatMessageTime(dateString) {
  const date = new Date(dateString);
  const now = new Date();
  
  const isToday = date.toDateString() === now.toDateString();
  
  if (isToday) {
    return date.toLocaleTimeString('ko-KR', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false 
    });
  } else {
    return date.toLocaleDateString('ko-KR', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  }
}
</script>

<style scoped>
.chat-room-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
}

.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.no-selection-icon {
  font-size: 80px;
  margin-bottom: 20px;
  opacity: 0.3;
}

.no-selection-text {
  font-size: 18px;
  color: #9ca3af;
}

.chat-room {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.partner-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6d28d9, #a78bfa);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: bold;
}

.chat-header h3 {
  margin: 0 0 2px 0;
  font-size: 16px;
  font-weight: 700;
  color: #111827;
}

.chat-subtitle {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9fafb;
}

.loading-messages, .empty-messages {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.spinner-small {
  width: 30px;
  height: 30px;
  border: 3px solid #e5e7eb;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 12px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-wrapper {
  display: flex;
  justify-content: flex-start;
}

.message-wrapper.mine {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  background: white;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.message-wrapper.mine .message-bubble {
  background: #6d28d9;
  color: white;
}

.message-text {
  margin: 0 0 4px 0;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-time {
  font-size: 11px;
  color: #9ca3af;
}

.message-wrapper.mine .message-time {
  color: rgba(255, 255, 255, 0.7);
}

.input-container {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: white;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

.send-button {
  width: 48px;
  height: 48px;
  background: #6d28d9;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 20px;
  cursor: pointer;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
  background: #5b21b6;
}

.send-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
}
</style>