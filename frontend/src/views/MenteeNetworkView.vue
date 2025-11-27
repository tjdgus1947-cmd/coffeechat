<template>
  <div class="network-view-container">

    <!-- 탭 메뉴 -->
    <div class="view-switcher">
      <button @click="currentView = 'graph'" :class="{ active: currentView === 'graph' }">
        네트워크 뷰
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

      <!-- 🔥 채팅 탭 추가 -->
      <button @click="currentView = 'chat'" :class="{ active: currentView === 'chat' }">
        💬 채팅
      </button>
    </div>

    <!-- 각 탭의 내용 -->
    <div v-show="currentView === 'graph'" class="graph-panel-wrapper">
      <NetworkGraph
        :nodes="networkStore.nodes"
        :edges="networkStore.edges"
        @node-click="handleNodeClick"
        class="graph-panel"
      />
      <TopMentorsPanel
        :mentors="topMentorsList"
        :loading="isLoadingTopMentors"
        @select-mentor="handleTopMentorClick"
        class="top-mentors-floating"
      />
    </div>

    <div v-if="currentView === 'map'" class="map-panel-wrapper">
      <MentorMap />
    </div>

    <div v-show="currentView === 'list'" class="list-panel-wrapper">
      <MentorListPanel
        :mentors="topMentorsList"
        :loading="isLoadingTopMentors"
        :currentUserId="currentUserId"
        @view-profile="handleTopMentorClick"
        @open-booking="openBookingModal"
      />
    </div>

    <div v-if="currentView === 'management'" class="management-panel">
      <section class="manage-section completed-section">
        <div class="section-header">
          <h3>🎉 완료된 커피챗</h3>
          <span class="desc">종료된 세션입니다. 멘토님에게 후기를 남겨보세요!</span>
        </div>

        <div v-if="completedChats.length > 0" class="chat-list">
          <div v-for="chat in completedChats" :key="chat.id" class="chat-card completed">
            <div class="chat-info">
              <span class="mentor-name">{{ chat.mentor?.full_name || '멘토' }}님</span>
              <span class="chat-time">{{ formatSchedule(chat.start_time, chat.end_time) }}</span>
            </div>

            <button 
              class="review-btn" 
              :class="{ 'reviewed': chat.has_review }"
              @click="openReviewModal(chat)"
            >
              {{ chat.has_review ? '📖 내가 쓴 후기' : '✍️ 후기 작성' }}
            </button>
          </div>
        </div>

        <div v-else class="empty-state-box">
          완료된 커피챗이 아직 없습니다.
        </div>
      </section>

      <section class="manage-section active-section">
        <div class="section-header">
          <h3>📨 신청 현황</h3>
          <span class="desc">승인 대기 중이거나 예정된 일정입니다.</span>
        </div>

        <div v-if="activeChats.length > 0" class="chat-list">
          <div v-for="chat in activeChats" :key="chat.id" class="chat-card">
            <div class="chat-top">
              <span class="mentor-name">{{ chat.mentor?.full_name || '멘토' }}님</span>
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
          신청 내역이 없습니다.
        </div>
      </section>
    </div>

    <!-- 🔥 채팅 뷰 추가 -->
    <div v-if="currentView === 'chat'" class="chat-view-wrapper">
      <div class="chat-layout">
        <ChatRoomList 
          @select-room="handleSelectRoom" 
          ref="chatRoomListRef"
          class="chat-room-list"
        />
        <ChatRoom 
          :selected-room="selectedChatRoom"
          class="chat-room"
        />
      </div>
    </div>

    <!-- 사이드 패널 및 모달 -->
    <MentorSidebar
      v-if="(currentView === 'graph' || currentView === 'list') && selectedMentor"
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

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { supabase } from '@/supabaseClient';
import { useRoute } from 'vue-router';

import { useNetworkStore } from '@/store/network';
import { useBookingStore } from '@/store/bookingstore'; 

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';
import ReviewModal from '@/components/review/ReviewModal.vue';

// 🔥 채팅 컴포넌트 import
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

const route = useRoute();
const networkStore = useNetworkStore();
const bookingStore = useBookingStore();

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

// 🔥 채팅 관련 state
const selectedChatRoom = ref(null);
const chatRoomListRef = ref(null);

onMounted(async () => {
  if (route.query.tab === 'list') {
    currentView.value = 'list';
  }

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

// 🔥 채팅방 선택 핸들러
function handleSelectRoom(room) {
  selectedChatRoom.value = room;
}
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

.graph-panel,
.map-panel-wrapper,
.list-panel-wrapper {
  width: 100%;
  height: 100%;
}

.sidebar-panel {
  position: absolute;
  right: 0;
  top: 48px;
  bottom: 0;
  height: auto;
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e0e0e0;
  z-index: 10;
  box-shadow: -2px 0 5px rgba(0,0,0,0.05);
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

/* 🔥 채팅 뷰 스타일 */
.chat-view-wrapper {
  flex: 1;
  height: 100%;
  overflow: hidden;
  padding: 20px;
  box-sizing: border-box;
}

.chat-layout {
  display: grid;
  grid-template-columns: 350px 1fr;
  height: 100%;
  gap: 0;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.chat-room-list {
  border-right: 1px solid #e5e7eb;
}

/* 반응형 */
@media (max-width: 768px) {
  .chat-layout {
    grid-template-columns: 1fr;
  }
  
  .chat-room-list {
    display: none;
  }
}

/* 스크롤바 숨기기 */
.graph-panel-wrapper::-webkit-scrollbar,
.map-panel-wrapper::-webkit-scrollbar,
.list-panel-wrapper::-webkit-scrollbar,
.management-panel::-webkit-scrollbar,
.sidebar-panel::-webkit-scrollbar,
.top-mentors-floating::-webkit-scrollbar {
  display: none;
}
.graph-panel-wrapper,
.map-panel-wrapper,
.list-panel-wrapper,
.management-panel,
.sidebar-panel,
.top-mentors-floating {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>