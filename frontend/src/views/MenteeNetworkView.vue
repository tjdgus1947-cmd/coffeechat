<template>
  <div class="network-view-container">

    <div class="cafe-tabs">
      <button 
        @click="currentView = 'graph'" 
        :class="{ active: currentView === 'graph' }"
      >
        <span class="icon">☕</span> 네트워크
      </button>

      <button @click="currentView = 'map'" :class="{ active: currentView === 'map' }">
        지도 뷰
      </button>

      <button @click="currentView = 'list'" :class="{ active: currentView === 'list' }">
        멘토 목록
      </button>

      <button @click="currentView = 'management'" :class="{ active: currentView === 'management' }">
        커피챗 관리
      </button>
      <button 
        @click="currentView = 'chat'" 
        :class="{ active: currentView === 'chat' }"
      >
        <span class="icon">💬</span> 채팅
      </button>
    </div>

    <div class="paper-panel">
      
      <div v-show="currentView === 'graph'" class="view-content graph-wrapper">
        
        <div class="info-strip">
          <div class="tape-left"></div>
          <div class="info-text">
            <span class="highlight">Tip.</span> 바리스타(멘토)를 <strong>더블 클릭</strong>하여 찜(❤️) 목록에 담아보세요!
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
          @view-profile="handleTopMentorClick"
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

      <div v-if="currentView === 'chat'" class="view-content chat-view-wrapper">
        <div class="chat-layout">
          <ChatRoomList 
            @select-room="handleSelectRoom" 
            class="chat-room-list"
          />
          <ChatRoom 
            :selected-room="selectedChatRoom"
            class="chat-room"
          />
        </div>
      </div>

    </div>

    <MentorProfileModal
      v-if="selectedMentor"
      :mentor="selectedMentor"
      :currentUserId="currentUserId"
      @close="closeSidebar"
      @book="openBookingModal"
      class="sidebar-panel"
    />

    <BookingModal
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

    <!-- 💬 네트워크 그래프 화면 왼쪽 아래 플로팅 채팅 버튼 -->
    <button
      v-if="currentView === 'graph'"
      class="floating-chat-btn"
      @click="goToChat"
    >
      💬
      <span
        v-if="chatStore.unreadCount > 0"
        class="chat-badge"
      >
        {{ chatStore.unreadCount > 9 ? '9+' : chatStore.unreadCount }}
      </span>
    </button>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { supabase } from '@/supabaseClient';
import { useRoute } from 'vue-router';

import { useNetworkStore } from '@/store/network';
import { useBookingStore } from '@/store/bookingstore'; 
import { useChatStore } from '@/store/chatStore';

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';
import ReviewModal from '@/components/review/ReviewModal.vue';
import MentorProfileModal from '@/components/profile/MentorSidebar.vue';

// 채팅 컴포넌트
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

const route = useRoute();
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

// 채팅 관련 상태
const selectedChatRoom = ref(null);
function handleSelectRoom(room) { selectedChatRoom.value = room; }

// 그래프 데이터
const graphNodes = computed(() => networkStore.nodes || []);
const graphEdges = computed(() => networkStore.edges || []);

onMounted(async () => {
  // 🔥 [수정] 쿼리 파라미터 확인 후 뷰 전환
  if (route.query.tab === 'list') currentView.value = 'list';
  if (route.query.view === 'chat') currentView.value = 'chat'; 

  networkStore.fetchNetworkData();

  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error('사용자 정보 조회 실패:', error);
      return;
    }

    if (user) {
      currentUserId.value = user.id;
      await fetchTopMentorsWithRealScore();
      await bookingStore.fetchBookings();
      await fetchReviewStatus();
    }
  } catch (err) {
    console.error('Auth 에러:', err);
  }
});

// 플로팅 버튼 → 채팅 탭으로 전환
function goToChat() {
  currentView.value = 'chat';
}

// 후기 상태 조회
async function fetchReviewStatus() {
  try {
    const { data, error } = await supabase
      .from('reviews')
      .select('coffee_chat_id')
      .eq('mentee_id', currentUserId.value);

    if (error) throw error;

    reviewStatusMap.value = {};
    data.forEach(review => {
      reviewStatusMap.value[review.coffee_chat_id] = true;
    });
  } catch (error) {
    console.error('후기 상태 조회 실패:', error);
  }
}

const completedChats = computed(() => {
  const now = new Date();
  return bookingStore.bookings
    .filter(chat => {
      if (chat.status !== 'approved') return false;
      if (!chat.end_time) return false;
      return new Date(chat.end_time) < now; 
    })
    .map(chat => ({
      ...chat,
      has_review: !!reviewStatusMap.value[chat.id]
    }));
});

const activeChats = computed(() => {
  const now = new Date();
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return true;
    if (!chat.end_time) return true; 
    return new Date(chat.end_time) >= now;
  });
});

function getStatusLabel(status) {
  if (status === 'approved') return '승인됨';
  if (status === 'rejected') return '거절됨';
  return '승인 대기';
}

function formatSchedule(start, end) {
  if (!start) return '일정 미정';
  const d = new Date(start);
  return `${d.getMonth()+1}/${d.getDate()} ${d.toLocaleTimeString('ko-KR', {hour:'2-digit', minute:'2-digit', hour12: false})}`;
}

function openReviewModal(chat) {
  selectedChatForReview.value = chat;
  isReviewModalOpen.value = true;
}

function closeReviewModal() {
  isReviewModalOpen.value = false;
  selectedChatForReview.value = null;
}

async function handleReviewSubmitted() {
  await fetchReviewStatus();
  await bookingStore.fetchBookings();
}

// TOP 멘토 / 매칭도 조회
async function fetchTopMentorsWithRealScore() {
  if (!currentUserId.value) {
    topMentorsList.value = networkStore.nodes
      .filter(node => node.data?.type === 'mentor')
      .map(node => node.data)
      .filter(Boolean);
    return;
  }
  
  isLoadingTopMentors.value = true;
  
  try {
    const response = await axios.get(
      `http://localhost:8000/api/matching/find-matches`,
      {
        params: {
          user_id: currentUserId.value,
          role: 'mentee',
          limit: 100
        }
      }
    );
    
    const matches = response.data.matches || [];
    
    const mentorsWithScore = matches.map(match => {
      const node = networkStore.nodes.find(n => n.data?.user_id === match.user_id);
      
      if (node && node.data) {
        return {
          ...node.data,
          final_score: match.final_score,
          matchingScore: match.final_score,
          textSimilarity: match.text_similarity,
          distanceKm: match.distance_km
        };
      }
      return null;
    }).filter(Boolean);
    
    topMentorsList.value = mentorsWithScore;
  } catch (error) {
    console.error('❌ TOP 멘토 매칭도 계산 실패:', error);
    topMentorsList.value = networkStore.nodes
      .filter(node => node.data?.type === 'mentor')
      .map(node => node.data)
      .filter(Boolean);
  } finally {
    isLoadingTopMentors.value = false;
  }
}

const handleNodeClick = (node) => {
  if (node.data?.type === 'mentor') {
    selectedMentor.value = node.data;
  } else {
    selectedMentor.value = null;
  }
};

const handleNodeDoubleClick = async (node) => {
  if (node.data?.type === 'mentor') {
    const mentorId = node.data.id || node.data.user_id;
    if (!mentorId) return;
    
    try {
      const { data, error } = await supabase
        .from('user_likes')
        .select('id')
        .eq('user_id', currentUserId.value)
        .eq('liked_mentor_id', mentorId)
        .single();
      
      if (error && error.code !== 'PGRST116') {
        console.error('찜 상태 확인 실패:', error);
        return;
      }
      
      if (data) {
        await supabase.from('user_likes').delete().eq('id', data.id);
        likedMentors.value = likedMentors.value.filter(id => id !== mentorId);
      } else {
        await supabase.from('user_likes').insert({
          user_id: currentUserId.value,
          liked_mentor_id: mentorId
        });
        likedMentors.value.push(mentorId);
      }
    } catch (error) {
      console.error('찜하기 오류:', error);
    }
  }
};

const handleTopMentorClick = (mentor) => {
  selectedMentor.value = mentor;
};

const closeSidebar = () => {
  selectedMentor.value = null;
};

const openBookingModal = (mentorData) => {
  mentorForBooking.value = mentorData;
  isModalOpen.value = true;
};

const closeBookingModal = () => {
  isModalOpen.value = false;
  mentorForBooking.value = null;
};
</script>

<style scoped>
.network-view-container {
  display: flex;
  width: 100%;
  height: calc(100vh - 100px);
  position: relative;
  flex-direction: column;
}

.view-switcher {
  display: flex;
  border-bottom: 1px solid #ccc;
  margin-bottom: 10px;
}
.view-switcher button {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 16px;
  border-bottom: 3px solid transparent;
}
.view-switcher button.active {
  border-bottom: 3px solid #6d28d9;
  font-weight: bold;
  color: #6d28d9;
}

.graph-panel-wrapper,
.map-panel-wrapper,
.list-panel-wrapper {
  flex-grow: 1;
  height: 100%;
  position: relative;
  overflow-y: auto;
}

/* 🌟 그래프 뷰 래퍼 스타일 */
.graph-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px;
}

.graph-component {
  flex-grow: 1;
  width: 100%;
  height: 100%;
  background-color: #FCF9F2;
}

.top-mentors-floating {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 5;
  max-height: calc(100% - 40px);
  overflow-y: auto;
}

.management-panel {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 30px;
  box-sizing: border-box;
  max-width: 800px;
  margin: 0 auto;
}
.manage-section {
  margin-bottom: 40px;
}
.section-header {
  margin-bottom: 15px;
}
.section-header h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  color: #111827;
}
.desc {
  font-size: 14px;
  color: #6b7280;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.chat-card.completed {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-left: 4px solid #6d28d9;
}
.mentor-name {
  font-weight: 700;
  font-size: 16px;
  margin-right: 10px;
}
.chat-time {
  color: #6b7280;
  font-size: 14px;
}
.review-btn {
  background-color: #6d28d9;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}
.review-btn:hover {
  background-color: #5b21b6;
}

.review-btn.reviewed {
  background-color: #059669;
}
.review-btn.reviewed:hover {
  background-color: #047857;
}

.chat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.status-badge {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  font-weight: 600;
}
.status-badge.pending { background: #fefce8; color: #b45309; }
.status-badge.approved { background: #f0fdf4; color: #15803d; }
.status-badge.rejected { background: #fef2f2; color: #b91c1c; }

.chat-details p {
  margin: 0;
  color: #4b5563;
}
.no-time {
  color: #9ca3af;
  font-size: 13px;
}

.empty-state-box {
  text-align: center;
  padding: 40px;
  background: #f3f4f6;
  border-radius: 12px;
  color: #9ca3af;
  font-size: 14px;
}

/* 🔥 [추가] 채팅 뷰 스타일 */
.chat-view-wrapper {
  height: 100%;
  padding: 20px;
}

.chat-layout {
  display: grid;
  grid-template-columns: 320px 1fr;
  height: 100%;
  border: 1px solid #D1A872;
  border-radius: 12px;
  overflow: hidden;
  background: white;
  box-shadow: 0 4px 12px rgba(54, 18, 5, 0.05);
}

.chat-room-list {
  border-right: 1px solid #e5e7eb;
}

/* 반응형 채팅 */
@media (max-width: 768px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }
  .chat-room-list {
    display: none; /* 모바일에선 목록/방 전환 필요 */
  }
}

/* 기타 스타일 (그래프 등) */
.graph-info-bar { display: flex; justify-content: space-between; padding: 10px 20px; background: #FFF8E7; border-bottom: 1px dashed #D1A872; }
.info-strip { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10; background: #FFF8E7; padding: 8px 30px; border: 1px dashed #DF8723; border-radius: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; gap: 20px; align-items: center; }
.tape-left { position: absolute; left: -20px; top: -8px; width: 60px; height: 20px; background: rgba(223, 135, 35, 0.4); transform: rotate(-3deg); }
.tape-right { position: absolute; right: -20px; bottom: -8px; width: 60px; height: 20px; background: rgba(223, 135, 35, 0.4); transform: rotate(3deg); }
.info-text strong { color: #DF8723; }
.like-counter { border-left: 2px solid #E6DCCD; padding-left: 20px; font-weight: 600; }
.badge { background: #E06C75; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-left: 4px; }
.top-mentors-floating { position: absolute; top: 80px; right: 30px; z-index: 5; }
.floating-chat-btn { position: absolute; left: 30px; bottom: 30px; width: 60px; height: 60px; border-radius: 50%; background: #361205; color: white; border: 3px solid #D1A872; font-size: 26px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2); z-index: 20; }
.chat-badge { position: absolute; top: 0; right: 0; background: #E06C75; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px; border: 2px solid #361205; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50; }
</style>
