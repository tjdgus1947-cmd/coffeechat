<template>
  <div class="min-h-screen bg-gray-50">
    <main class="container mx-auto px-4 py-8">

      <!-- 상단 통계 박스 제거, 네트워크 그래프 내부에 연결된 멘토 박스 배치 -->

      <!-- 네트워크 그래프 + 멘토 카드 분할 레이아웃 -->
      <div class="flex bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" style="min-height:600px;">
        <!-- 네트워크 그래프: 넓게 확장, 내부 오른쪽 상단에 연결된 멘토 박스 배치 -->
        <div class="graph-container" style="width:75vw; height:80vh; min-width:0; display:flex; flex-direction:column; position:relative;">
          <div style="position:absolute; top:24px; right:24px; z-index:10;">
            <div class="bg-white rounded-xl p-4 shadow-md border border-gray-200 flex items-center gap-3" style="min-width:160px;">
              <div>
                <p class="text-gray-600 text-sm font-medium">연결된 멘토</p>
                <p class="text-2xl font-bold text-blue-700 mt-1">{{ connectedMentorsCount }}</p>
              </div>
              <div class="bg-blue-100 p-2 rounded-lg">
                <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>
          <div style="flex:1; min-height:0;">
            <NetworkGraph
              :nodes="networkStore.nodes"
              :edges="networkStore.edges"
              @node-click="handleNodeClick"
            />
          </div>
        </div>
        <!-- 멘토 카드: 1/3, 세로 스크롤 가능 -->
  <div style="width:400px; min-width:300px; border-left:1px solid #eee; height:80vh; overflow-y:auto; display:flex; align-items:flex-start; justify-content:center; padding-top:24px;">
          <TopMentorsPanel
            :mentors="networkStore.nodes.filter(n => n.data?.type === 'mentor').map(n => n.data)"
            :loading="networkStore.isLoading"
            @select-mentor="handleMentorCardClick"
          />
        </div>
      </div>
    </main>

    <!-- 멘토 사이드바 -->
    <MentorSidebar
      :mentor="selectedMentor"
      @close="closeSidebar"
      @book="openBookingModal"
    />

    <!-- 예약 모달 -->
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
import { ref, computed, onMounted } from 'vue';
import { useNetworkStore } from '@/store/network.mjs';

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';

const networkStore = useNetworkStore();

const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);

// 통계 계산
const connectedMentorsCount = computed(() => {
  return networkStore.nodes.filter(node => node.data?.type === 'mentor').length;
});

const totalNodesCount = computed(() => {
  return networkStore.nodes.length;
});

const totalEdgesCount = computed(() => {
  return networkStore.edges.length;
});

onMounted(() => {
  networkStore.fetchNetworkData();
});

const handleNodeClick = (node) => {
  if (node.data?.type === 'mentor') {
    selectedMentor.value = node.data;
    console.log('멘토 노드 클릭:', node.data);
  } else {
    selectedMentor.value = null;
    console.log('비-멘토 노드 클릭:', node.label);
  }
};

// 멘토 카드 클릭 시 상세 정보 표시
const handleMentorCardClick = (mentor) => {
  selectedMentor.value = mentor;
  console.log('멘토 카드 클릭:', mentor);
};

const closeSidebar = () => {
  selectedMentor.value = null;
};

const openBookingModal = (mentorData) => {
  // 상세보기 모달 먼저 닫기
  selectedMentor.value = null;
  
  // 예약 모달 열기
  mentorForBooking.value = mentorData;
  isModalOpen.value = true;
  console.log('예약 모달 열기:', mentorData.name);
};

const closeBookingModal = () => {
  isModalOpen.value = false;
  mentorForBooking.value = null;
  console.log('예약 모달 닫기');
};
</script>

<style scoped>
.graph-container {
  height: 600px;
  width: 100%;
  background: linear-gradient(to bottom, #f8fafc, #ffffff);
}
</style>