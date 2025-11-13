<template>
  <div class="network-view-container">
    
    <!-- 1. 탭 버튼 UI -->
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
    </div>

    <!-- 2. 그래프 뷰 (v-show로 제어) -->
    <div v-show="currentView === 'graph'" class="graph-panel-wrapper">
      <NetworkGraph
        :nodes="networkStore.nodes"
        :edges="networkStore.edges"
        @node-click="handleNodeClick"
        class="graph-panel"
      />
      
      <!-- 🔥 신규: AI 매칭도 TOP 5 패널 -->
      <TopMentorsPanel
        :mentors="topMentorsList"
        :loading="isLoadingTopMentors"
        @select-mentor="handleTopMentorClick"
        class="top-mentors-floating"
      />
    </div>

    <!-- 3. 지도 뷰 (v-show로 제어) -->
    <div v-show="currentView === 'map'" class="map-panel-wrapper">
      <MentorMap />
    </div>

    <!-- 🔥 신규: 4. 목록 뷰 -->
    <div v-show="currentView === 'list'" class="list-panel-wrapper">
      <MentorListPanel 
        :mentors="topMentorsList"
        :loading="isLoadingTopMentors"
        :currentUserId="currentUserId"
      />
    </div>

    <!-- 🔥 수정: currentUserId props 추가 -->
    <MentorSidebar
      v-if="currentView === 'graph' && selectedMentor"
      :mentor="selectedMentor"
      :currentUserId="currentUserId"
      @close="closeSidebar"
      @book="openBookingModal"
      class="sidebar-panel"
    />

    <!-- 예약 모달은 공통 사용 -->
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
import { useNetworkStore } from '@/store/network';
import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';
import axios from 'axios';

// 🔥 Supabase Auth에서 현재 사용자 정보 가져오기
import { supabase } from '@/supabaseClient';

const networkStore = useNetworkStore();
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);
const currentView = ref('graph');

// 🔥 신규: 현재 로그인한 사용자 ID
const currentUserId = ref('');

// 🔥 수정: 실시간 매칭도가 계산된 멘토 리스트
const topMentorsList = ref([]);
const isLoadingTopMentors = ref(false);

onMounted(async () => {
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
      
      // 🔥 실시간 매칭도 계산
      await fetchTopMentorsWithRealScore();
    } else {
      console.warn('⚠️ 로그인된 사용자가 없습니다.');
    }
  } catch (err) {
    console.error('Auth 에러:', err);
  }
});

// 🔥 신규: 실시간 매칭도를 계산하여 TOP 5 가져오기
async function fetchTopMentorsWithRealScore() {
  if (!currentUserId.value) {
    console.warn('⚠️ userId가 없어서 TOP 멘토 계산을 건너뜁니다.');
    // 폴백: 네트워크 API의 similarity 사용
    topMentorsList.value = networkStore.nodes
      .filter(node => node.data?.type === 'mentor')
      .map(node => node.data)
      .filter(Boolean);
    return;
  }
  
  isLoadingTopMentors.value = true;
  
  try {
    // 1. 매칭 API 호출 (텍스트 70% + 거리 30%)
    console.log(`🔍 TOP 멘토 매칭도 계산 시작: user_id=${currentUserId.value}`);
    
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
    console.log(`✅ 매칭 API 응답: ${matches.length}명`);
    
    // 2. 네트워크 노드 데이터와 매칭
    const mentorsWithScore = matches.map(match => {
      const node = networkStore.nodes.find(n => n.data?.user_id === match.user_id);
      
      if (node && node.data) {
        return {
          ...node.data,
          final_score: match.final_score, // 🔥 수정: final_score로 통일
          matchingScore: match.final_score, // 🔥 추가: 호환성 유지
          textSimilarity: match.text_similarity,
          distanceKm: match.distance_km
        };
      }
      return null;
    }).filter(Boolean);
    
    topMentorsList.value = mentorsWithScore;
    console.log(`✅ TOP 멘토 매칭도 계산 완료: ${mentorsWithScore.length}명`);
  } catch (error) {
    console.error('❌ TOP 멘토 매칭도 계산 실패:', error);
    
    // 에러 상세 로그
    if (error.response) {
      console.error('에러 상태:', error.response.status);
      console.error('에러 메시지:', error.response.data);
    }
    
    // 🔥 실패 시 네트워크 API의 similarity 사용 (폴백)
    console.log('⚠️ 폴백: 네트워크 API의 similarity 점수 사용');
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

// 🔥 신규: TOP 5 패널에서 멘토 클릭 시
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
  overflow-y: auto; /* 🔥 스크롤 추가 */
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

/* 🔥 신규: TOP 5 패널 스타일 */
.top-mentors-floating {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 5;
  max-height: calc(100% - 40px);
  overflow-y: auto;
}
</style>