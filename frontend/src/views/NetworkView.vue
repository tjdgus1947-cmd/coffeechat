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
      <!-- 2단계에서 만든 맵 컴포넌트 -->
      <MentorMap />
    </div>

    <!-- 사이드바는 그래프 뷰일 때만 보이도록 수정 -->
    <MentorSidebar
      v-if="currentView === 'graph'"
      :mentor="selectedMentor"
      @close="closeSidebar"
      @book="openBookingModal"
      class="sidebar-panel"
    />

    <!-- 예약 모달은 공통 사용 -->
    <BookingModal
      :show="isModalOpen"
      
      :mentor-id="mentorForBooking?.user_id" 
      
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
// 4. (신규) 맵 컴포넌트 임포트
import MentorMap from '@/components/map/MentorMap.vue';

const networkStore = useNetworkStore();
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);

// 5. (신규) 현재 뷰 상태 (graph 또는 map)
const currentView = ref('graph'); // 기본값 'graph'

onMounted(() => {
  // 그래프 뷰에 필요한 데이터는 미리 로드
  networkStore.fetchNetworkData();
});

// (이하 핸들러 함수들은 동일)
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
/* (기존 스타일과 동일) */
.network-view-container {
  display: flex;
  width: 100%;
  height: calc(100vh - 100px); /* 탭 높이 등을 고려하여 조정 */
  position: relative;
  flex-direction: column; /* ⭐️ 탭 버튼을 위해 수직으로 변경 */
}

/* 6. (신규) 탭 버튼 스타일 */
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

/* 7. (신규) 뷰 래퍼 스타일 */
.graph-panel-wrapper,
.map-panel-wrapper {
  flex-grow: 1; /* 남은 공간을 모두 차지 */
  height: 100%;
  position: relative;
}

/* 8. (수정) 그래프/맵 패널 스타일 */
.graph-panel,
.map-panel-wrapper {
  width: 100%;
  height: 100%;
}

/* 사이드바는 이제 absolute 포지션을 사용해야
   그래프/맵 뷰 위에 겹쳐집니다.
*/
.sidebar-panel {
  position: absolute;
  right: 0;
  top: 48px; /* 탭 버튼 높이만큼 내리기 */
  bottom: 0;
  height: auto; /* 높이 100% 대신 auto */
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e0e0e0;
  z-index: 10;
  box-shadow: -2px 0 5px rgba(0,0,0,0.05);
}
</style>