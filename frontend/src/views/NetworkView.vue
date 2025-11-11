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
    </div>

    <!-- 2. 그래프 뷰 (v-show로 제어) -->
    <div v-show="currentView === 'graph'" class="graph-panel-wrapper">
      <NetworkGraph
        :nodes="networkStore.nodes"
        :edges="networkStore.edges"
        @node-click="handleNodeClick"
        class="graph-panel"
      />
    </div>

    <!-- 3. 지도 뷰 (v-show로 제어) -->
    <div v-show="currentView === 'map'" class="map-panel-wrapper">
      <MentorMap />
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
import { ref, onMounted } from 'vue';
import { useNetworkStore } from '@/store/network';
import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';

// 🔥 Supabase Auth에서 현재 사용자 정보 가져오기
import { supabase } from '@/supabaseClient'; // 경로는 프로젝트에 맞게 수정

const networkStore = useNetworkStore();
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);
const currentView = ref('graph');

// 🔥 신규: 현재 로그인한 사용자 ID
const currentUserId = ref('');

onMounted(async () => {
  // 그래프 데이터 로드
  networkStore.fetchNetworkData();

  // 🔥 현재 로그인한 사용자 정보 가져오기
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error('사용자 정보 조회 실패:', error);
      return;
    }

    if (user) {
      currentUserId.value = user.id;
      console.log('✅ 현재 사용자 ID:', user.id);
    } else {
      console.warn('⚠️ 로그인된 사용자가 없습니다.');
    }
  } catch (err) {
    console.error('Auth 에러:', err);
  }
});

const handleNodeClick = (node) => {
  if (node.data?.type === 'mentor') {
    selectedMentor.value = node.data;
  } else {
    selectedMentor.value = null;
  }
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
.map-panel-wrapper {
  flex-grow: 1;
  height: 100%;
  position: relative;
}

.graph-panel,
.map-panel-wrapper {
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
</style>