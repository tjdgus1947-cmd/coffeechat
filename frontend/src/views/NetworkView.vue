<template>
  <div class="min-h-screen bg-gray-50">
    <main class="container mx-auto px-4 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">멘토 네트워크 🌐</h1>
        <p class="text-gray-600">
          나의 멘토 네트워크를 시각적으로 확인하고 새로운 연결을 만들어보세요
        </p>
      </div>

      <!-- Stats Overview -->
      <div class="mb-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-medium">연결된 멘토</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ connectedMentorsCount }}</p>
              </div>
              <div class="bg-blue-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-medium">총 노드</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ totalNodesCount }}</p>
              </div>
              <div class="bg-green-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-medium">네트워크 연결</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ totalEdgesCount }}</p>
              </div>
              <div class="bg-purple-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 네트워크 그래프 + 멘토 카드 분할 레이아웃 -->
      <div class="flex bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden" style="min-height:600px;">
        <!-- 네트워크 그래프: 2/3 -->
        <div class="graph-container" style="width:66.666%; min-width:0; display:flex; flex-direction:column;">
          <!-- 상단 제목 및 분리선 -->
          <div style="padding:0 24px 0 24px; border-bottom:1px solid #eee; background:#fff; display:flex; align-items:center; justify-content:space-between; min-height:60px;">
            <h2 class="text-xl font-bold">네트워크 그래프</h2>
            <div class="flex gap-2">
              <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">멘토</span>
              <span class="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full">키워드</span>
              <span class="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full">나</span>
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
        <div style="width:33.333%; min-width:300px; border-left:1px solid #eee; height:600px; overflow-y:auto; display:flex; align-items:flex-start; justify-content:center; padding-top:24px;">
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
import { useNetworkStore } from '@/store/network';

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