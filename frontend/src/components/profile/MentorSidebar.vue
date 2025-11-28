<!-- MentorSidebar.vue (수정본) -->
<template>
  <aside v-if="mentor" class="sidebar-container">
    <button @click="$emit('close')" class="close-button" aria-label="닫기">X</button>
    
    <div class="profile-header">
      <span class="mentor-badge">멘토</span>
      <h2>{{ mentor.name }}</h2>
      <p class="mentor-company">{{ mentor.company }}</p>
    </div>

    <!-- 🔥 수정된 부분: 실시간 매칭도 표시 -->
    <div class="matching-score">
      <span>AI 매칭도</span>
      <strong v-if="!loadingScore">{{ realMatchScore }}%</strong>
      <strong v-else style="color: #999;">계산 중...</strong>
      <div class="progress-bar">
        <div class="progress" :style="{ width: realMatchScore + '%' }"></div>
      </div>
      
      <!-- 🆕 상세 정보 표시 (선택사항) -->
      <div v-if="matchDetails && !loadingScore" class="match-details">
        <small style="color: #666;">
          텍스트 유사도: {{ matchDetails.text_similarity }}% / 
          거리: {{ matchDetails.distance_km }}km
        </small>
      </div>
    </div>

    <div class="mentor-details">
      <h3>소속</h3>
      <p>{{ mentor.team || '정보 없음' }}</p>

      <h3>경력</h3>
      <p>{{ mentor.experienceYears || '정보 없음' }}년</p>

      <h3>전문 분야</h3>
      <div class="tags" v-if="mentor.tags && mentor.tags.length > 0">
        <span v-for="tag in mentor.tags" :key="tag" class="tag">{{ tag }}</span>
      </div>
      <p v-else>정보 없음</p>

      <h3>소개</h3>
      <p class="intro-text">{{ mentor.introduction || '소개 정보가 없습니다.' }}</p>
    </div>
    
    <button @click="$emit('book', mentor)" class="book-button">
      커피챗 예약하기
    </button>
  </aside>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '@/services/api'; // ✅ api.js 사용

const props = defineProps({
  mentor: {
    type: Object,
    default: null,
  },
  // 🆕 현재 로그인한 사용자 ID (멘티)
  currentUserId: {
    type: String,
    required: true
  }
});

defineEmits(['close', 'book']);

// 🔥 실시간 매칭도 계산
const realMatchScore = ref(0);
const loadingScore = ref(true);
const matchDetails = ref(null);

// ✅ API 호출 함수 (async 추가 및 에러 처리 강화)
async function fetchMatchingScore() {
  if (!props.mentor || !props.currentUserId) {
    realMatchScore.value = 0;
    loadingScore.value = false;
    return;
  }

  loadingScore.value = true;

  try {
    // ✅ api.js 사용으로 변경 (axios 기반)
    const response = await api.get('/matching/find-matches', {
      params: {
        user_id: props.currentUserId,
        role: 'mentee',
        limit: 50
      }
    });

    // axios는 자동으로 response.data를 제공
    const data = response.data;

    // 현재 멘토의 매칭 점수 찾기
    const matchedMentor = data.matches.find(
      m => m.user_id === props.mentor.user_id || m.user_id === props.mentor.id
    );

    if (matchedMentor) {
      realMatchScore.value = Math.round(matchedMentor.final_score || 0);
      matchDetails.value = {
        text_similarity: Math.round(matchedMentor.text_similarity || 0),
        distance_km: (matchedMentor.distance_km || 0).toFixed(1),
        distance_score: Math.round(matchedMentor.distance_score || 0)
      };
    } else {
      // 매칭 안됨
      realMatchScore.value = 0;
      matchDetails.value = null;
      console.warn('이 멘토의 매칭 점수를 찾을 수 없습니다.');
    }
  } catch (error) {
    console.error('매칭 점수 조회 실패:', error);
    realMatchScore.value = 0;
    matchDetails.value = null;
    
    // ✅ 에러 메시지 상세화
    if (error.response && error.response.status === 401) {
      console.warn('인증 세션이 만료되었습니다. 다시 로그인해주세요.');
      // 필요하다면 여기서 로그아웃 함수를 호출하거나 로그인 페이지로 이동시킬 수 있습니다.
      // 예: router.push('/login');
    }
  } finally {
    loadingScore.value = false;
  }
}

// 멘토가 변경될 때마다 매칭도 계산
watch(() => props.mentor, () => {
  if (props.mentor) {
    fetchMatchingScore();
  }
}, { immediate: true });

// 컴포넌트 마운트 시 실행
onMounted(() => {
  fetchMatchingScore();
});
</script>

<style scoped>
.sidebar-container {
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e0e0e0;
  padding: 24px;
  color: #333;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-y: auto;
  box-shadow: -2px 0 5px rgba(0,0,0,0.05);
}
.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  font-size: 20px;
  font-weight: bold;
  color: #999;
  cursor: pointer;
}
.profile-header .mentor-badge {
  background-color: #f0ebff;
  color: #6d28d9;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}
.profile-header h2 {
  font-size: 24px;
  font-weight: bold;
  margin: 8px 0 4px;
}
.profile-header .mentor-company {
  color: #666;
  font-size: 14px;
  margin: 0;
}
.matching-score {
  margin: 20px 0;
}
.matching-score strong {
  color: #6d28d9;
  font-size: 20px;
  margin-left: 8px;
}
.progress-bar {
  background-color: #e0e0e0;
  border-radius: 4px;
  height: 8px;
  overflow: hidden;
  margin-top: 8px;
}
.progress {
  background-color: #6d28d9;
  height: 100%;
  transition: width 0.3s ease;
}
/* 🆕 상세 정보 스타일 */
.match-details {
  margin-top: 8px;
  font-size: 12px;
}
.mentor-details h3 {
  font-size: 14px;
  font-weight: bold;
  color: #888;
  margin-top: 16px;
  margin-bottom: 4px;
  text-transform: uppercase;
}
.mentor-details p {
  font-size: 15px;
  margin: 0;
  line-height: 1.5;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.tags .tag {
  background-color: #f3f4f6;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
}
.book-button {
  width: 100%;
  background-color: #6d28d9;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 24px;
  transition: background-color 0.2s;
}
.book-button:hover {
  background-color: #5b21b6;
}
</style>