<template>
  <div class="chat-room-container">
    
    <div v-if="!selectedRoom" class="no-selection cafe-bg-pattern">
      <div class="empty-cup-illustration">
        <div class="steam">Hello!</div>
        <div class="cup">☕</div>
        <div class="plate"></div>
      </div>
      <h2 class="cafe-welcome">Welcome to CoffeeChat</h2>
      <p class="cafe-desc">
        왼쪽 메뉴에서 대화 상대를 선택하고,<br>
        따뜻한 이야기를 시작해보세요.
      </p>
    </div>

    <div v-else class="chat-room">
      <div class="chat-header">
        <div class="header-info">
          <div class="partner-avatar-small">{{ partnerName.charAt(0) }}</div>
          <div>
            <h3>{{ partnerName }}</h3>
            <p class="chat-subtitle">함께 성장하는 커피챗 타임 ☕</p>
          </div>
        </div>
      </div>

      <div class="messages-container" ref="messagesContainer">
        <div v-if="messages.length === 0" class="empty-messages">
          <span class="start-icon">✨</span>
          <p>첫 인사를 건네보세요!</p>
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

      <div class="input-container">
        <textarea
          v-model="newMessage"
          @keydown.enter.prevent="handleSend"
          placeholder="따뜻한 대화를 나눠보세요..."
          rows="1"
          class="message-input"
        ></textarea>
        <button
          @click="handleSend"
          :disabled="!newMessage.trim() || isSending"
          class="send-button"
        >
          📤
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
// ChatRoom.vue
import { ref, computed, watch, nextTick, onUnmounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';
import { supabase } from '@/services/supabase';

const authStore = useAuthStore();
const props = defineProps({
  selectedRoom: Object
});
const subscription = ref(null);

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
  if (subscription.value) {
    supabase.removeChannel(subscription.value); // 이전 방 구독 해제
    subscription.value = null;
  }

  if (newRoom) {
    await fetchMessages();
    subscribeToRealtime(newRoom.id); // ⭐️ 실시간 구독 시작
  }
}, { immediate: true });

onUnmounted(() => {
  if (subscription.value) {
    supabase.removeChannel(subscription.value);
  }
});

function subscribeToRealtime(roomId) {
  subscription.value = supabase
    .channel(`room-${roomId}`) // 채널 이름 (유니크하면 됨)
    .on(
      'postgres_changes',
      {
        event: 'INSERT', // 메시지가 추가될 때만 감지
        schema: 'public',
        table: 'chat_messages',
        filter: `chat_room_id=eq.${roomId}` // 현재 방의 메시지만 필터링
      },
      (payload) => {
        // payload.new에 새로 들어온 메시지 데이터가 있음
        const newMessage = payload.new;
        
        // 내 메시지는 handleSend에서 이미 추가했을 수도 있지만, 
        // 확실히 하기 위해 중복 방지 체크 후 추가하거나,
        // handleSend에서는 API 호출만 하고 여기서 UI 업데이트를 해도 됨.
        // 여기서는 중복 방지 로직을 추가함.
        const exists = messages.value.some(m => m.id === newMessage.id);
        if (!exists) {
          messages.value.push(newMessage);
          nextTick(() => scrollToBottom());
          
          // (선택 사항) 상대방이 보낸 메시지라면 '읽음 처리' API 호출 로직 추가 가능
          if (newMessage.sender_id !== currentUserId.value) {
             markAsRead(newMessage.id); 
          }
        }
      }
    )
    .subscribe();
}

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
async function markAsRead(messageId) {
  try {
    await api.post(`/chat/messages/${messageId}/read`);
  } catch (error) {
    console.error('메시지 읽음 처리 실패:', error);
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
/* ☕ 배경 패턴 (냅킨 질감) */
.cafe-bg-pattern {
  background-color: #fdfbf7;
  background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
  background-size: 20px 20px;
}

.chat-room-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #fcf9f2; /* 전체 배경 웜 화이트 */
}

/* 빈 상태 스타일링 */
.no-selection {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8d6e63;
  text-align: center;
}
.empty-cup-illustration { font-size: 60px; margin-bottom: 20px; position: relative; }
.steam { font-size: 14px; position: absolute; top: -20px; left: 50%; transform: translateX(-50%); animation: float 2s infinite ease-in-out; color: #d7ccc8; }
.cafe-welcome { font-family: serif; font-size: 24px; color: #4e342e; margin-bottom: 10px; }
.cafe-desc { color: #a1887f; line-height: 1.6; }

@keyframes float {
  0%, 100% { transform: translate(-50%, 0); opacity: 0.5; }
  50% { transform: translate(-50%, -10px); opacity: 1; }
}

/* 헤더 */
.chat-header {
  padding: 15px 25px;
  background-color: #fff;
  border-bottom: 1px solid #efe5d9;
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}
.chat-header h3 { margin: 0; color: #3e2723; font-size: 16px; font-weight: 700; }
.chat-subtitle { font-size: 12px; color: #a1887f; margin: 0; }
.header-info { display: flex; align-items: center; min-width: 0; }
.header-info > div:last-child { min-width: 0; }
.message-text { overflow-wrap: anywhere; white-space: pre-wrap; }
@media (max-width: 560px) {
  .chat-header { padding: 12px 16px; }
  .messages-container { padding: 14px 12px; }
  .message-bubble { max-width: 85%; padding: 10px 14px; }
}
.partner-avatar-small {
  width: 36px; height: 36px; background: #d7ccc8; color: #fff;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-weight: bold; margin-right: 10px;
}

/* 메시지 영역 */
.messages-container {
  flex: 1;
  padding: 20px;
  background-color: #d7c8bc; /* 옅은 크림색 */
  overflow-y: auto;
}

.message-wrapper {
  margin-bottom: 15px;
  display: flex;
}
.message-wrapper.mine { justify-content: flex-end; }

/* 🔥 말풍선 스타일 변경 */
.message-bubble {
  max-width: 70%;
  padding: 12px 18px;
  border-radius: 18px;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  font-size: 14px;
  line-height: 1.5;
}

/* 상대방 말풍선 (흰색 + 둥근 사각형) */
.message-wrapper:not(.mine) .message-bubble {
  background-color: #ffffff;
  color: #4e342e;
  border-top-left-radius: 2px; /* 말꼬리 효과 */
  border: 1px solid #eee;
}

/* 내 말풍선 (포인트 컬러 + 둥근 사각형) */
.message-wrapper.mine .message-bubble {
  background-color: var(--primary-color, #361205); /* 에스프레소 색 */
  color: #fdfbf7; /* 밝은 글씨 */
  border-top-right-radius: 2px;
}

.message-time {
  display: block;
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.7;
  text-align: right;
}

/* 입력창 */
.input-container {
  padding: 20px;
  background-color: #fff;
  border-top: 1px solid #efe5d9;
  display: flex;
  gap: 10px;
  align-items: center;
}

.message-input {
  flex: 1;
  background-color: #f9f9f990;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 100;
  resize: none;
  outline: none;
  transition: border 0.2s;
}
.message-input:focus { border-color: var(--point-color, #DF8723); background-color: #fff; }

.send-button {
  width: 45px; height: 45px;
  background-color: var(--point-color, #DF8723);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 3px 6px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}
.send-button:hover:not(:disabled) { transform: scale(1.1); background-color: #bf360c; }
.send-button:disabled { background-color: #d7ccc8; cursor: default; }
</style>