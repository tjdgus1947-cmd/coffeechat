<template>

  <div class="network-view-container">

    <div class="view-switcher">

      <button @click="currentView = 'graph'" :class="{ active: currentView === 'graph' }">
        네트워크 뷰
      </button>

      <button @click="currentView = 'map'" :class="{ active: currentView === 'map' }">
        지도 뷰 (WBS 5.2)
      </button>

      <button @click="currentView = 'list'" :class="{ active: currentView === 'list' }">
        멘토 목록
      </button>

      <button @click="currentView = 'management'" :class="{ active: currentView === 'management' }">
        커피챗 관리
      </button>

    </div>

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

    <div v-show="currentView === 'map'" class="map-panel-wrapper">
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

              <button class="review-btn" @click="openReviewModal(chat)">
                ✍️ 후기 작성
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

  </div>

</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { supabase } from '@/supabaseClient';
import { useRoute } from 'vue-router'; // 🔥 추가: 라우터 정보 가져오기

import { useNetworkStore } from '@/store/network';
import { useBookingStore } from '@/store/bookingstore'; 

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';

const route = useRoute(); // 🔥 추가: 현재 URL 정보
const networkStore = useNetworkStore();
const bookingStore = useBookingStore();

const currentView = ref('graph'); // 기본값: 그래프 뷰
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);
const currentUserId = ref('');
const topMentorsList = ref([]);
const isLoadingTopMentors = ref(false);


onMounted(async () => {
  // 🔥 핵심 기능: URL에 '?tab=list'가 있으면 '멘토 목록' 탭으로 자동 전환
  if (route.query.tab === 'list') {
    currentView.value = 'list';
  }

  // 그래프 데이터 로드
  networkStore.fetchNetworkData();

  // 현재 로그인한 사용자 정보 가져오기
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error('사용자 정보 조회 실패:', error);
      return;
    }

    if (user) {
      currentUserId.value = user.id;
      console.log('✅ 현재 사용자 ID:', user.id);
      
      // 실시간 매칭도 계산
      await fetchTopMentorsWithRealScore();

      await bookingStore.fetchBookings();
    } else {
      console.warn('⚠️ 로그인된 사용자가 없습니다.');
    }
  } catch (err) {
    console.error('Auth 에러:', err);
  }
});

// 1. 완료된 커피챗
const completedChats = computed(() => {
  const now = new Date();
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return false;
    if (!chat.end_time) return false;
    return new Date(chat.end_time) < now; 
  });
});

// 2. 진행 중인 커피챗
const activeChats = computed(() => {
  const now = new Date();
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return true;
    if (!chat.end_time) return true; 
    return new Date(chat.end_time) >= now;
  });
});

// 헬퍼 함수들
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
  alert(`${chat.mentor?.full_name} 멘토님에 대한 후기 작성 (준비 중)`);
}

// TOP 멘토 매칭도 계산
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
</script>

<style scoped>
/* 스타일은 기존과 동일합니다 */
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
}
.review-btn:hover {
  background-color: #5b21b6;
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
</style>