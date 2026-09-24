<!-- MenteeNetworkView.vue -->
<template>
  <div class="network-view-container">

    <div class="cafe-tabs">
      <button @click="switchView('graph')" :class="{ active: currentView === 'graph' }">
        <span class="icon">☕</span> 네트워크
      </button>
      <button @click="switchView('map')" :class="{ active: currentView === 'map' }">
        <span class="icon">🗺️</span> 지도
      </button>
      <button @click="switchView('list')" :class="{ active: currentView === 'list' }">
        <span class="icon">📋</span> 파트너 목록
      </button>
      <button @click="switchView('management')" :class="{ active: currentView === 'management' }">
        <span class="icon">🧾</span> 약속 관리
      </button>
      <button @click="switchView('chat')" :class="{ active: currentView === 'chat' }">
        <span class="icon">💬</span> 채팅
        <span v-if="chatStore.unreadCount > 0" class="tab-badge">
          {{ chatStore.unreadCount }}
        </span>
      </button>
    </div>

    <div class="paper-panel">
      <div v-show="currentView === 'graph'" class="view-content graph-wrapper">
        
      <div class="info-strip">  
          <div class="tape-left"></div>
          <div class="info-text">
            <span class="highlight">Tip.</span> 바리스타(멘토)를 <strong> 클릭</strong>하여 찜(❤️) 목록에 담아보세요!
          </div>
          <div class="like-counter">
            내가 찜한 바리스타 <span class="badge">{{ likedMentors.length }}</span>명
          </div>
          <div class="tape-right"></div>
        </div>


        <div v-if="graphNodes.length === 0 && !isLoadingTopMentors" class="empty-graph-message">
          <p>☕ 아직 추천 파트너가 준비되지 않았습니다.</p>
          <p>잠시만 기다려주시거나, 프로필을 업데이트 해보세요!</p>
        </div>

        <NetworkGraph
          v-else
          :nodes="graphNodes"
          :edges="graphEdges"
          @node-click="handleNodeClick"
          @node-double-click="handleNodeDoubleClick"
          class="graph-component"
        />
        
        <TopMentorsPanel
          :mentors="topMentorsList"
          :loading="isLoadingTopMentors"
          @select-mentor="handleTopMentorClick"
          class="top-mentors-floating"
        />
      </div>

      <div v-show="currentView === 'map'" class="view-content map-wrapper">
        <MentorMap />
      </div>

     <div v-show="currentView === 'list'" class="view-content list-wrapper">
  <MentorListPanel
    :mentors="topMentorsList"
    :loading="isLoadingTopMentors"
    :currentUserId="currentUserId"
    
    :likedMentorIds="likedMentors"  @view-profile="handleTopMentorClick"
    @open-booking="openBookingModal"
  />
</div>

      <div v-if="currentView === 'management'" class="view-content management-wrapper">
        <div class="receipt-style-container">
          <div v-if="bookingStore.isLoading" class="loading-state">
            <p>🧾 주문 내역을 불러오는 중...</p>
          </div>

          <div v-else>
            <section class="manage-section completed-section">
              <div class="section-header">
                <h3>🎉 지난 만남 (완료)</h3>
                <span class="desc">종료된 세션입니다. 후기를 남겨주세요.</span>
              </div>
              <div v-if="completedChats.length > 0" class="chat-list">
                <div v-for="chat in completedChats" :key="chat.id" class="chat-card completed">
                  <div class="chat-info">
                    <span class="mentor-name">{{ chat.mentor?.full_name || '바리스타' }}님</span>
                    <span class="chat-time">{{ formatSchedule(chat.start_time, chat.end_time) }}</span>
                  </div>
                  <button class="review-btn" :class="{ 'reviewed': chat.has_review }" @click="openReviewModal(chat)">
                    {{ chat.has_review ? '📖 후기 확인' : '✍️ 후기 작성' }}
                  </button>
                </div>
              </div>
              <div v-else class="empty-state-box">아직 완료된 만남이 없습니다.</div>
            </section>

            <section class="manage-section active-section">
              <div class="section-header">
                <h3>📨 약속 현황 (진행 중)</h3>
                <span class="desc">승인 대기 중이거나 예정된 일정입니다.</span>
              </div>
              <div v-if="activeChats.length > 0" class="chat-list">
                <div v-for="chat in activeChats" :key="chat.id" class="chat-card">
                  <div class="chat-top">
                    <span class="mentor-name">{{ chat.mentor?.full_name || '바리스타' }}님</span>
                    <span :class="['status-badge', chat.status]">
                      {{ getStatusLabel(chat.status) }}
                    </span>
                  </div>
                  <div class="chat-details">
                    <p v-if="chat.start_time">📅 {{ formatSchedule(chat.start_time, chat.end_time) }}</p>
                    <p v-else class="no-time">시간 정보 없음</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state-box">
                <p>현재 진행 중인 약속이 없습니다.</p>
                <button class="link-btn" @click="currentView = 'list'">👉 파트너 찾으러 가기</button>
              </div>
            </section>
          </div>
        </div>
      </div>

      <div v-show="currentView === 'chat'" class="view-content chat-view-wrapper">
        <div class="chat-layout">
          
          <div class="list-pane" :class="{ 'hidden-mobile': selectedChatRoom }">
            <ChatRoomList 
              @select-room="handleSelectRoom" 
              class="chat-room-list"
            />
          </div>

          <div class="room-pane" :class="{ 'hidden-mobile': !selectedChatRoom }">
            <div v-if="selectedChatRoom" class="mobile-back-header">
              <button @click="selectedChatRoom = null" class="back-btn">
                ← 목록으로
              </button>
            </div>
            
            <ChatRoom 
              :selected-room="selectedChatRoom"
              class="chat-room"
            />
          </div>

        </div>
      </div>

    </div>

    <MentorProfileModal
      v-if="selectedMentor"
      :mentor="selectedMentor"
      :currentUserId="currentUserId"
      :isLiked="isLiked(selectedMentor.id || selectedMentor.user_id)"
      @close="closeSidebar"
      @book="openBookingModal"
      @toggle-like="toggleLike"
    />

    <BookingModal
      v-if="isModalOpen"
      :show="isModalOpen"
      :mentor-id="mentorForBooking?.id"
      :mentor-name="mentorForBooking?.name"
      @close="closeBookingModal"
      @booking-confirmed="closeBookingModal"
    />

    <ReviewModal
      :show="isReviewModalOpen"
      :chat="selectedChatForReview"
      :mentee-id="currentUserId"
      @close="closeReviewModal"
      @review-submitted="handleReviewSubmitted"
    />

    <button
      v-if="currentView === 'graph'"
      class="floating-chat-btn"
      @click="goToChat"
      title="채팅하기"
    >
      💬
      <span v-if="chatStore.unreadCount > 0" class="chat-badge">
        {{ chatStore.unreadCount > 9 ? '9+' : chatStore.unreadCount }}
      </span>
    </button>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue';
import api from '@/services/api';
import { supabase } from '@/supabaseClient';
import { useRoute, useRouter } from 'vue-router';

import { useNetworkStore } from '@/store/network';
import { useBookingStore } from '@/store/bookingstore'; 
import { useChatStore } from '@/store/chatStore';

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';
import MentorProfileModal from '@/components/profile/MentorProfileModal.vue';
import ReviewModal from '@/components/review/ReviewModal.vue';
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

const route = useRoute();
const router = useRouter();
const networkStore = useNetworkStore();
const bookingStore = useBookingStore();
const chatStore = useChatStore();

const currentView = ref('graph');
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);
const currentUserId = ref('');
const topMentorsList = ref([]);
const isLoadingTopMentors = ref(false);
const isReviewModalOpen = ref(false);
const selectedChatForReview = ref(null);
const reviewStatusMap = ref({});
const likedMentors = ref([]);

// 🔥 채팅 관련 상태
const selectedChatRoom = ref(null);

onMounted(async () => {
  if (route.query.tab === 'list') currentView.value = 'list';
  if (route.query.view === 'chat') currentView.value = 'chat'; 

  networkStore.fetchNetworkData();
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (user) {
      currentUserId.value = user.id;
      await fetchTopMentorsWithRealScore();
      await bookingStore.fetchBookings();
      await loadLikedMentors();
      await fetchReviewStatus();
      chatStore.fetchUnreadCount();
    }
  } catch (err) { console.error('Auth 에러:', err); }
});

// 뷰 전환 함수
function switchView(viewName) {
  currentView.value = viewName;
  // 채팅 탭을 나갔다 들어오면 선택된 방 초기화 (선택 사항)
  // if (viewName !== 'chat') selectedChatRoom.value = null;
}

// 🔥 채팅방 선택 핸들러 (연결 핵심)
function handleSelectRoom(room) {
  console.log('채팅방 선택됨:', room); // 디버깅용 로그
  selectedChatRoom.value = room;
}

function goToChat() {
  currentView.value = 'chat';
}

// --- 기타 로직들 (기존 유지) ---
async function loadLikedMentors() {
  try {
    const { data } = await supabase.from('user_likes').select('liked_mentor_id').eq('user_id', currentUserId.value);
    likedMentors.value = (data || []).map(item => item.liked_mentor_id);
  } catch (error) { likedMentors.value = []; }
}

async function toggleLike(mentorId) {
  const isCurrentlyLiked = isLiked(mentorId);
  try {
    if (isCurrentlyLiked) {
      await supabase.from('user_likes').delete().eq('user_id', currentUserId.value).eq('liked_mentor_id', mentorId);
      likedMentors.value = likedMentors.value.filter(id => id !== mentorId);
    } else {
      await supabase.from('user_likes').insert({ user_id: currentUserId.value, liked_mentor_id: mentorId });
      likedMentors.value.push(mentorId);
    }
  } catch (error) { console.error('찜 변경 실패:', error); }
}

function isLiked(mentorId) { return likedMentors.value.includes(mentorId); }

const graphNodes = computed(() => {
  return networkStore.nodes.map(node => {
    if (node.data?.type === 'mentor') {
      const mentorId = node.data.id || node.data.user_id;
      return { ...node, data: { ...node.data, isLiked: isLiked(mentorId) } };
    }
    return node;
  });
});
const graphEdges = computed(() => networkStore.edges);

async function fetchTopMentorsWithRealScore() {
  if (!currentUserId.value) {
    topMentorsList.value = networkStore.nodes.filter(n => n.data?.type === 'mentor').map(n => n.data);
    return;
  }
  isLoadingTopMentors.value = true;
  try {
    const response = await api.get('/matching/find-matches', {
      params: { user_id: currentUserId.value, role: 'mentee', limit: 100 }
    });
    topMentorsList.value = response.data.matches.map(match => {
      const node = networkStore.nodes.find(n => n.data?.user_id === match.user_id);
      return node ? { ...node.data, ...match, isLiked: isLiked(match.user_id) } : null;
    }).filter(Boolean);
  } catch (e) { console.error(e); } 
  finally { isLoadingTopMentors.value = false; }
}

const completedChats = computed(() => {
  const now = new Date();
  if (!bookingStore.bookings) return []; 
  return bookingStore.bookings
    .filter(chat => {
      if (chat.status !== 'approved') return false;
      if (!chat.end_time) return false;
      return new Date(chat.end_time) < now; 
    })
    .map(chat => ({ ...chat, has_review: !!reviewStatusMap.value[chat.id] }));
});

const activeChats = computed(() => {
  const now = new Date();
  if (!bookingStore.bookings) return []; 
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return true;
    if (!chat.end_time) return true; 
    return new Date(chat.end_time) >= now;
  });
});

const handleNodeClick = (node) => { selectedMentor.value = node.data?.type === 'mentor' ? node.data : null; };
const handleNodeDoubleClick = (node) => { if (node.data?.type === 'mentor') toggleLike(node.data.id || node.data.user_id); };
const handleTopMentorClick = (mentor) => { selectedMentor.value = mentor; };
const closeSidebar = () => { selectedMentor.value = null; };
const openBookingModal = (mentor) => {
  // 1) 프로필 모달 닫기
  selectedMentor.value = null;

  // 2) 예약용 멘토 정보 세팅
  mentorForBooking.value = {
    id: mentor.id || mentor.user_id,
    name: mentor.full_name || mentor.name,
  };

  // 3) 예약 모달(캘린더) 열기
  isModalOpen.value = true;
};

const closeBookingModal = () => { isModalOpen.value = false; mentorForBooking.value = null; bookingStore.fetchBookings(); }; 

async function fetchReviewStatus() {
  try {
    const { data } = await supabase.from('reviews').select('coffee_chat_id').eq('mentee_id', currentUserId.value);
    reviewStatusMap.value = {};
    (data || []).forEach(r => { reviewStatusMap.value[r.coffee_chat_id] = true; });
  } catch (error) { console.error(error); }
}

function getStatusLabel(status) { return status === 'approved' ? '승인됨' : (status === 'rejected' ? '거절됨' : '승인 대기'); }
function formatSchedule(start, end) { return start ? new Date(start).toLocaleDateString() : '미정'; }
function openReviewModal(chat) { selectedChatForReview.value = chat; isReviewModalOpen.value = true; }
function closeReviewModal() { isReviewModalOpen.value = false; selectedChatForReview.value = null; }
async function handleReviewSubmitted() { await bookingStore.fetchBookings(); await fetchReviewStatus(); }
</script>

<style scoped>
/* ☕ 배경 및 레이아웃 */
.network-view-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100vh - 70px); /* 네비바 제외 */
  position: relative;
  background-color: #E5DCC8;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden; 
}

/* 탭 메뉴 */
.cafe-tabs {
  display: flex;
  gap: 8px;
  padding-left: 10px;
  margin-bottom: -1px;
  z-index: 10;
  flex-shrink: 0;
}

.cafe-tabs button {
  padding: 12px 20px;
  border: 1px solid #D1A872;
  border-bottom: none;
  background-color: #FFFFFF ;
  color: #8A5A34;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s ease;
  position: relative;
}

.cafe-tabs button.active {
  background-color: #FFFFFF;
  color: #1a0a03;
  padding-bottom: 14px;
  transform: translateY(-2px);
  box-shadow: 0 -4px 6px rgba(54, 18, 5, 0.1);
  font-weight: 800;
  border-top: 4px solid #B85C00;
}

.tab-badge {
  background-color: #ef4444;
  color: white;
  font-size: 10px;
  padding: 2px 5px;
  border-radius: 50%;
  margin-left: 4px;
  vertical-align: top;
}

.cafe-tabs .icon { margin-right: 6px; }

/* 메인 패널 */
.paper-panel {
  flex-grow: 1;
  background-color: #e3d0bcc0;
  border: 2px solid #B8935A;
  border-radius: 0 16px 16px 16px;
  box-shadow: 0 10px 30px rgba(54, 18, 5, 0.08);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

.view-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow-y: auto; 
}

/* 🔥 채팅 뷰 스타일 */
.chat-view-wrapper {
  padding: 0;
  height: 100%;
}

.chat-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: 100%;
}

.list-pane {
  height: 100%;
  border-right: 1px solid #e5e7eb;
  overflow: hidden;
}

.room-pane {
  height: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mobile-back-header {
  display: none; /* PC에선 숨김 */
  padding: 10px;
  border-bottom: 1px solid #eee;
  background: #f9f9f9;
}

.back-btn {
  background: none;
  border: none;
  font-weight: bold;
  color: #361205;
  cursor: pointer;
}

/* 📱 모바일 반응형 (핵심 수정) */
@media (max-width: 768px) {
  .chat-layout {
    grid-template-columns: 1fr; /* 1열로 변경 */
  }

  .hidden-mobile {
    display: none; /* 상태에 따라 숨김 */
  }

  .mobile-back-header {
    display: block; /* 모바일에서만 뒤로가기 버튼 보임 */
  }
  
  .cafe-tabs button {
    padding: 10px 14px;
    font-size: 13px;
  }
}

/* --- ☕ 상단 안내바 디자인 (마스킹 테이프 스타일) --- */
.info-strip {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  background-color: #d7c8bc; /* 연한 종이 색 */
  border: 1px solid #e0d0b0;
  padding: 12px 24px;
  border-radius: 2px;
  box-shadow: 0 4px 10px rgba(54, 18, 5, 0.1);
  
  width: 90%;
  max-width: 600px;
  min-width: 320px;
}

/* 마스킹 테이프 효과 */
.tape-left, .tape-right {
  position: absolute;
  top: -8px;
  width: 40px;
  height: 12px;
  background-color: rgba(223, 135, 35, 0.5);
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  border-left: 1px dashed rgba(255,255,255,0.3);
  border-right: 1px dashed rgba(255,255,255,0.3);
}

.tape-left {
  left: -10px;
  transform: rotate(-25deg);
}

.tape-right {
  right: -10px;
  transform: rotate(25deg);
}

/* 텍스트 스타일 */
.info-text {
  font-size: 0.95rem;
  color: #5a4a42;
}

.highlight {
  color: #DF8723;
  font-weight: 800;
  margin-right: 4px;
}

/* 찜 개수 카운터 */
.like-counter {
  font-size: 0.9rem;
  color: #8A5A34;
  font-weight: 600;
  display: flex;
  align-items: center;
}

.badge {
  background-color: #E06C75;
  color: white;
  font-size: 0.8rem;
  padding: 2px 8px;
  border-radius: 12px;
  margin: 0 4px;
  font-weight: 800;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 기타 스타일 생략 (기존과 동일) */



.top-mentors-floating { position: absolute; top: 80px; right: 30px; z-index: 5; }
.floating-chat-btn { position: absolute; left: 30px; bottom: 30px; width: 60px; height: 60px; border-radius: 50%; background: #361205; color: white; border: 3px solid #D1A872; font-size: 26px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2); z-index: 20; }
.chat-badge { position: absolute; top: 0; right: 0; background: #E06C75; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px; border: 2px solid #361205; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50; }
.empty-graph-message { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; color: #8A5A34; font-size: 1.1rem; z-index: 5; }
.receipt-style-container { max-width: 800px; margin: 40px auto; padding: 0 20px 60px; }
.manage-section { margin-bottom: 40px; background-color: #FFFFFF; padding: 24px; border-radius: 8px; border: 2px solid #a87a56; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }
.section-header h3 { font-size: 1.2rem; color: #361205; border-bottom: 2px solid #361205; padding-bottom: 10px; margin-bottom: 10px; display: inline-block; }
.desc { display: block; color: #8A5A34; margin-bottom: 20px; font-size: 0.95rem; }
.chat-card { background: #FFFFFF; border: 1px solid #E6DCCD; border-radius: 8px; padding: 16px 20px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center; transition: transform 0.2s; }
.chat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(54, 18, 5, 0.08); border-color: #DF8723; }
.chat-card.completed { border-left: 4px solid #DF8723; }
.mentor-name { font-weight: 700; color: #361205; font-size: 1.1rem; }
.chat-time { font-size: 0.9rem; color: #8A5A34; margin-top: 4px; display: block; }
.review-btn { background-color: #fceccb; color: #361205; border: 1.5px solid #D1A872; padding: 8px 16px; border-radius: 20px; font-weight: 600; font-size: 0.9rem; cursor: pointer; }
.review-btn:hover { background-color: #DF8723; color: white; border-color: #DF8723; }
.link-btn { background: none; border: none; color: #DF8723; font-weight: bold; cursor: pointer; text-decoration: underline; margin-top: 10px; }
.empty-state-box { text-align: center; padding: 40px; color: #A67857; font-style: italic; background-color: #FDFBF7; border-radius: 8px; }
.loading-state { text-align: center; padding: 60px; color: #8A5A34; font-size: 1.1rem; }
</style>