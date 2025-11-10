<template>
  <div class="min-h-screen bg-gray-50">
    <main class="container mx-auto px-4 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">안녕하세요, {{ authStore.userName }}님! 👋</h1>
        <p class="text-gray-600">
          오늘도 성장을 향한 여정을 함께해요
        </p>
      </div>

      <!-- Stats Overview -->
      <div class="mb-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-medium">총 커피챗</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.totalChats }}</p>
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
                <p class="text-gray-600 text-sm font-medium">만난 멘토</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.totalMentors }}</p>
              </div>
              <div class="bg-green-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-gray-600 text-sm font-medium">예정된 일정</p>
                <p class="text-3xl font-bold text-gray-900 mt-2">{{ stats.upcomingChats }}</p>
              </div>
              <div class="bg-purple-100 p-3 rounded-lg">
                <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="grid lg:grid-cols-3 gap-8 mb-8">
        <!-- GIS 지도: 주변 멘토 찾기 (2/3 너비) -->
        <div class="lg:col-span-2 bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="p-6 pb-0">
            <h2 class="text-xl font-bold mb-2">주변 멘토 찾기 📍</h2>
            <p class="text-sm text-gray-600 mb-4">카카오맵으로 가까운 멘토를 확인하세요</p>
          </div>
          
          <!-- 카카오맵 컴포넌트 -->
          <div style="height: 500px;">
            <MentorMap />
          </div>
        </div>

        <!-- 예정된 커피챗 (1/3 너비) -->
        <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
          <h2 class="text-xl font-bold mb-6">예정된 커피챗</h2>
          <div class="space-y-4">
            <div class="p-6 bg-blue-50 rounded-lg border border-blue-200">
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-gray-900 text-lg">아직 예약된 커피챗이 없습니다</p>
                  <p class="text-sm text-gray-600 mt-2">멘토를 찾아 커피챗을 예약해보세요!</p>
                  <p class="text-xs text-gray-500 mt-4">지도에서 멘토를 확인하거나, AI 추천 멘토를 확인해보세요.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 추천 멘토 -->
      <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold">AI 추천 멘토</h2>
          <span class="text-sm text-gray-500">당신의 커리어 목표에 맞춰 추천드려요</span>
        </div>
        
        <div v-if="isLoading" class="text-center py-12">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">멘토를 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="text-center py-12">
          <p class="text-red-600">{{ error }}</p>
        </div>

        <div v-else-if="mentors.length === 0" class="text-center py-12">
          <p class="text-gray-600">추천 멘토가 없습니다.</p>
        </div>

        <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div 
            v-for="mentor in mentors" 
            :key="mentor.id"
            class="flex items-center gap-4 p-4 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition cursor-pointer"
          >
            <div class="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-xl shrink-0">
              {{ mentor.full_name?.charAt(0) || 'M' }}
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-lg truncate">{{ mentor.full_name || '이름 없음' }}</h3>
              <p class="text-sm text-gray-600 line-clamp-2">{{ mentor.mentor_profiles?.[0]?.career_info || '정보 없음' }}</p>
              <button class="mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm font-medium transition w-full">
                연결하기
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import MentorMap from '@/components/map/MentorMap.vue';
import axios from 'axios';

const authStore = useAuthStore();

const stats = ref({
  totalChats: 0,      // 총 커피챗 신청 수
  totalMentors: 0,    // 실제로 만난 멘토 수 (완료된 커피챗)
  upcomingChats: 0    // 예정된 커피챗 수 (승인된 상태)
});

const mentors = ref([]);
const isLoading = ref(false);
const error = ref(null);

// 멘티의 커피챗 통계 가져오기
const fetchBookingStats = async () => {
  if (!authStore.userId || authStore.userRole !== 'mentee') {
    return;
  }

  try {
    const response = await axios.get('http://localhost:8000/api/bookings/me', {
      headers: {
        'Authorization': `Bearer ${authStore.accessToken}`
      }
    });
    
    const bookings = response.data || [];
    
    // 통계 계산
    stats.value.totalChats = bookings.length; // 총 신청 수
    
    // 완료된 커피챗 수 (만난 멘토)
    const completedMentors = new Set(
      bookings
        .filter(b => b.status === 'completed')
        .map(b => b.mentor?.full_name)
    );
    stats.value.totalMentors = completedMentors.size;
    
    // 승인된 커피챗 수 (예정된 일정)
    stats.value.upcomingChats = bookings.filter(
      b => b.status === 'confirmed' || b.status === 'approved'
    ).length;
    
    console.log('커피챗 통계:', stats.value);
  } catch (err) {
    console.error('커피챗 통계 조회 오류:', err);
    // 에러 발생 시 0으로 유지
  }
};

const fetchRecommendedMentors = async () => {
  if (!authStore.userId) {
    error.value = '로그인 정보가 없습니다.';
    return;
  }

  isLoading.value = true;
  error.value = null;

  try {
    const response = await axios.get(`http://localhost:8000/api/mentors/recommended/${authStore.userId}`);
    mentors.value = response.data || [];
  } catch (err) {
    console.error('멘토 추천 API 오류:', err);
    error.value = err.response?.data?.detail || '멘토를 불러오는데 실패했습니다.';
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchBookingStats();      // 통계 먼저 로드
  fetchRecommendedMentors(); // 추천 멘토 로드
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
