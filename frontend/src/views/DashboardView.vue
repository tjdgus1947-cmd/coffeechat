<template>
  <MentorDashboardView v-if="authStore.userRole === 'mentor'" />
  <div v-else class="min-h-screen bg-gray-50">
    <main class="container mx-auto px-4 py-8">
      <!-- Welcome Section -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">안녕하세요, {{ authStore.userName }}님! 👋</h1>
        <p class="text-gray-600">
          오늘도 성장을 향한 여정을 함께해요
        </p>
      </div>


      <!-- Main Content -->
      <div class="mb-8">
        <!-- GIS 지도: 주변 멘토 찾기 (전체 너비) -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div class="p-6 pb-0">
            <h2 class="text-xl font-bold mb-2">주변 멘토 찾기 📍</h2>
            <p class="text-sm text-gray-600 mb-4">카카오맵으로 가까운 멘토를 확인하세요</p>
          </div>
          
          <!-- 카카오맵 컴포넌트 -->
          <div style="height: 500px;">
            <MentorMap />
          </div>
        </div>

      </div>

      <!-- 추천 멘토 목록 (스크린샷 UI) -->
      <div class="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
        <div class="text-center mb-8">
          <h2 class="text-3xl font-bold mb-2 flex items-center justify-center gap-2">
            <span>🎯</span> 추천 멘토 목록
          </h2>
          <p class="text-gray-500">AI가 분석한 나와 가장 잘 맞는 멘토들을 만나보세요</p>
        </div>

        <div class="bg-gray-50 rounded-xl p-6 mb-8 flex flex-col md:flex-row gap-6 items-center justify-between">
          <div class="flex flex-col md:flex-row gap-6 flex-1">
            <div class="flex flex-col min-w-[200px]">
              <label class="text-sm font-semibold text-gray-700 mb-2">매칭도</label>
              <input type="range" min="0" max="100" v-model="filter.matchingScore" class="w-full accent-purple-600 h-2" />
              <span class="text-purple-600 text-sm font-medium mt-1">{{ filter.matchingScore }}% 이상</span>
            </div>
            <div class="flex flex-col min-w-[200px]">
              <label class="text-sm font-semibold text-gray-700 mb-2">거리</label>
              <input type="range" min="1" max="100" v-model="filter.distance" class="w-full accent-purple-600 h-2" />
              <span class="text-purple-600 text-sm font-medium mt-1">{{ filter.distance }}km 이내</span>
            </div>
            <div class="flex flex-col min-w-[200px]">
              <label class="text-sm font-semibold text-gray-700 mb-2">전문 분야</label>
              <input type="text" v-model="filter.expertise" placeholder="예: 법무, 개발, 디자인..." class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500" />
            </div>
            <div class="flex items-end">
              <button @click="resetFilter" class="px-4 py-2 border-2 border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-100 transition flex items-center gap-2">
                <span>🔄</span> 필터 초기화
              </button>
            </div>
          </div>
          <div class="flex items-center gap-3 bg-white rounded-lg px-4 py-2 border border-gray-200">
            <label class="text-sm font-semibold text-gray-700">정렬:</label>
            <select v-model="sortOrder" class="text-sm font-medium text-gray-700 focus:outline-none cursor-pointer">
              <option value="score">매칭도 높은 순</option>
              <option value="distance">거리 가까운 순</option>
            </select>
          </div>
        </div>

        <div class="flex items-center justify-between mb-6">
          <p class="text-gray-600 font-medium">{{ filteredMentors.length }}명의 멘토</p>
        </div>

        <div v-if="isLoading" class="text-center py-16">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-purple-600 mx-auto mb-4"></div>
          <p class="text-gray-600 font-medium">멘토를 불러오는 중...</p>
        </div>

        <div v-else-if="error" class="text-center py-16">
          <p class="text-red-600 font-medium text-lg">{{ error }}</p>
        </div>

        <div v-else-if="filteredMentors.length === 0" class="text-center py-16">
          <p class="text-gray-500 text-lg font-medium">추천 멘토가 없습니다.</p>
        </div>

        <div v-else class="space-y-4">
          <div 
            v-for="(mentor, idx) in filteredMentors" 
            :key="mentor.id || idx"
            class="flex flex-col md:flex-row items-start gap-6 p-6 bg-white rounded-xl border-2 border-gray-200 hover:border-purple-300 hover:shadow-lg transition-all duration-200"
          >
            <div class="relative">
              <div class="w-20 h-20 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold text-3xl shadow-md">
                {{ mentor.full_name?.charAt(0)?.toUpperCase() || '멘' }}
              </div>
              <div v-if="idx < 3" class="absolute -top-2 -right-2 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-md">
                <span class="text-xl">{{ idx === 0 ? '🥇' : idx === 1 ? '🥈' : '🥉' }}</span>
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-3">
                <h3 class="text-xl font-bold text-gray-900">{{ mentor.full_name || '멘토' }}</h3>
                <span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                  {{ mentor.company || 'H건설팅' }}
                </span>
              </div>
              <div class="flex flex-wrap gap-2 mb-3">
                <span class="px-3 py-1 bg-purple-50 text-purple-700 rounded-full text-xs font-semibold">
                  {{ mentor.career_info || '전공 컨설팅 (전략/오퍼레이션)' }}
                </span>
                <span class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-semibold">
                  📅 {{ mentor.experience || '16년 경력' }}
                </span>
                <span v-if="mentor.industry" class="px-3 py-1 bg-pink-50 text-pink-700 rounded-full text-xs font-semibold">
                  산업 분석
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-4 line-clamp-2">
                {{ mentor.description || '16년 동안 다양한 산업군의 기업들로 대상으로 전략 및 오퍼레이션 컨설팅을 제공했습니다. 컨설팅 면접 (케이스 인터뷰) 준비 노하우, 기업의 핵심 문제를 진단하고 논리적으로 해결책을 도출하는 방법을 코칭합니다. PPT 보고서 작성 및 구두 발표 스킬도 함께 코칭합니다.' }}
              </p>
              <div class="flex flex-col sm:flex-row gap-6">
                <div class="flex-1">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-semibold text-gray-500">AI 매칭도</span>
                    <span class="text-sm font-bold text-purple-700">{{ (mentor.final_score || mentor.similarity || 79.94).toFixed(2) }}%</span>
                  </div>
                  <div class="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      class="h-3 bg-gradient-to-r from-purple-500 to-purple-600 rounded-full transition-all duration-500"
                      :style="{ width: (mentor.final_score || mentor.similarity || 79.94) + '%' }"
                    ></div>
                  </div>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-xl">📍</span>
                  <div>
                    <p class="text-xs font-semibold text-gray-500">거리</p>
                    <p class="text-sm font-bold text-pink-600">{{ formatDistance(mentor.distance_km) }}</p>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-3 min-w-[140px]">
              <button class="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center gap-2">
                <span>☕</span> 커피챗 신청
              </button>
              <button class="px-6 py-3 bg-gray-100 hover:bg-gray-200 text-gray-800 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2">
                <span>👤</span> 프로필 보기
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import MentorMap from '@/components/map/MentorMap.vue';
import axios from 'axios';
import MentorDashboardView from '@/views/MentorDashboardView.vue';

const authStore = useAuthStore();

const stats = ref({
  totalChats: 0,      // 총 커피챗 신청 수
  totalMentors: 0,    // 실제로 만난 멘토 수 (완료된 커피챗)
  upcomingChats: 0    // 예정된 커피챗 수 (승인된 상태)
});

const mentors = ref([]);
const isLoading = ref(false);
const error = ref(null);

// 필터 및 정렬 상태 (스크린샷 UI와 동일)
const filter = ref({
  matchingScore: 0,
  distance: 100,
  expertise: ''
});
const sortOrder = ref('score');

function resetFilter() {
  filter.value = { matchingScore: 0, distance: 100, expertise: '' };
}

function formatDistance(km) {
  if (!km || isNaN(km)) return '-';
  const distance = parseFloat(km);
  return `${distance.toFixed(1)}km`;
}

const filteredMentors = computed(() => {
  let arr = mentors.value.filter(m =>
    (m.matchingScore ?? m.final_score ?? m.similarity ?? 0) >= filter.value.matchingScore &&
    (m.distance_km ?? 100) <= filter.value.distance &&
    (filter.value.expertise === '' || (m.career_info ?? '').includes(filter.value.expertise))
  );
  if (sortOrder.value === 'score') {
    arr = arr.sort((a, b) => (b.matchingScore ?? b.final_score ?? b.similarity ?? 0) - (a.matchingScore ?? a.final_score ?? a.similarity ?? 0));
  } else {
    arr = arr.sort((a, b) => (a.distance_km ?? 100) - (b.distance_km ?? 100));
  }
  return arr;
});

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
