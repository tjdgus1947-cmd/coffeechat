<template>
  <div class="network-view-container">
    
    <NetworkGraph
      :nodes="networkStore.nodes"
      :edges="networkStore.edges"
      @node-click="handleNodeClick"
      class="graph-panel"
    />

    <MentorSidebar
      :mentor="selectedMentor"
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
import { ref, onMounted } from 'vue';
import { useNetworkStore } from '@/store/network'; // 1, 3-5단계

// 4. 컴포넌트 3개 모두 임포트
import NetworkGraph from '@/components/graph/NetworkGraph.vue'; // 2단계
import MentorSidebar from '@/components/profile/MentorSidebar.vue'; // 4-1단계
import BookingModal from '@/components/calendar/BookingModal.vue'; // 4-2단계

// 5. Pinia 스토어 사용
const networkStore = useNetworkStore();

// 6. ⭐️ 사이드바와 모달을 제어할 내부 상태(ref) ⭐️
const selectedMentor = ref(null); // 사이드바에 보여줄 멘토 정보 (null이면 닫힘)
const mentorForBooking = ref(null); // 예약 모달에 넘겨줄 멘토 정보
const isModalOpen = ref(false); // 모달 열림/닫힘 상태

// 7. (기존) 페이지 로드 시 가짜 그래프 데이터 불러오기
onMounted(() => {
  networkStore.fetchNetworkData();
});

// 8. ⭐️ (수정) 노드 클릭 이벤트 핸들러 ⭐️
const handleNodeClick = (node) => {
  // 3-5단계 network.js의 가짜 데이터(data.type)를 확인합니다.
  if (node.data?.type === 'mentor') {
    // 클릭된 노드가 '멘토' 타입이면,
    // selectedMentor에 멘토 데이터(node.data)를 저장합니다.
    // 이로 인해 MentorSidebar가 '짠'하고 나타납니다.
    selectedMentor.value = node.data;
    console.log('멘토 노드 클릭:', node.data);
  } else {
    // 멘토 외 다른 노드(키워드, 멘티)를 클릭하면,
    // selectedMentor를 null로 만들어 사이드바를 닫습니다.
    selectedMentor.value = null;
    console.log('비-멘토 노드 클릭:', node.label);
  }
};

// 9. ⭐️ (신규) 사이드바 닫기 버튼 핸들러 ⭐️
const closeSidebar = () => {
  selectedMentor.value = null;
};

// 10. ⭐️ (신규) '커피챗 예약하기' 버튼 핸들러 ⭐️
const openBookingModal = (mentorData) => {
  // MentorSidebar가 @book 이벤트와 함께 멘토 객체를 전달해줍니다.
  mentorForBooking.value = mentorData; // 예약할 멘토 정보 저장
  isModalOpen.value = true; // BookingModal을 '짠'하고 띄웁니다.
  console.log('예약 모달 열기:', mentorData.name);
};

// 11. ⭐️ (신규) 모달 닫기 핸들러 ⭐️
const closeBookingModal = () => {
  isModalOpen.value = false;
  mentorForBooking.value = null;
  console.log('예약 모달 닫기');
};
</script>

<style scoped>
.network-view-container {
  display: flex; /* 그래프와 사이드바를 가로로 배치 */
  width: 100%;
  /* App.vue의 padding(20px * 2)을 뺀 높이 */
  height: calc(100vh - 40px); 
  position: relative;
  overflow: hidden; /* 페이지 스크롤 방지 */
}
.graph-panel {
  flex-grow: 1; /* 남은 공간을 모두 차지 */
  height: 100%;
}
.sidebar-panel {
  flex-shrink: 0; /* 사이드바 크기 고정 (300px) */
  height: 100%;
  /* v-if로 컴포넌트가 사라질 때 부드러운 효과를 원한다면
    transform: translateX(100%) 와 transition을 사용합니다.
    (지금은 v-if로 간단하게 구현)
  */
}
</style>