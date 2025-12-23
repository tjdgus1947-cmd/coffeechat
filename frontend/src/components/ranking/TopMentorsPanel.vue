<template>
  <div class="top-mentors-panel">
    <!-- 패널 헤더: 카페 메뉴판 제목 느낌 -->
    <div class="panel-header">
      <h3>☕ 오늘의 추천 바리스타</h3>
      <p class="subtitle">나와 취향(Fit)이 맞는 파트너 TOP 5</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>최적의 원두를 고르는 중...</p>
    </div>

    <!-- TOP 5 리스트 -->
    <div v-else-if="topMentors.length > 0" class="mentors-list">
      <div
        v-for="(mentor, index) in topMentors"
        :key="mentor.id"
        class="mentor-card"
        :class="{ 'rank-1': index === 0 }"
        @click="$emit('select-mentor', mentor)"
      >
        <!-- 순위 배지 (스탬프 느낌) -->
        <div class="rank-badge" :class="`rank-${index + 1}`">
          <span v-if="index === 0">👑</span>
          <span v-else>{{ index + 1 }}</span>
        </div>

        <!-- 멘토 정보 -->
        <div class="mentor-info">
          <div class="info-header">
            <h4>{{ mentor.name }}</h4>
            <span class="company">{{ mentor.company }}</span>
          </div>
          
          <!-- 매칭도 점수 (커피 농도 느낌) -->
          <div class="match-score">
            <span class="score-label">Fit</span>
            <div class="score-bar">
              <div 
                class="score-fill" 
                :style="{ width: mentor.matchingScore + '%' }"
              ></div>
            </div>
            <span class="score-text">{{ mentor.matchingScore }}%</span>
          </div>

          <!-- 거리 정보 -->
          <div v-if="mentor.distanceKm !== undefined" class="distance-info">
            <span class="icon">📍</span>
            {{ formatDistance(mentor.distanceKm) }}
            <span class="distance-detail" v-if="!mentor.breakdown">
              (거리 점수 {{ calculateDistanceScore(mentor.distanceKm) }}%)
            </span>
          </div>

          <!-- 전문 분야 태그 -->
          <div v-if="mentor.tags && mentor.tags.length > 0" class="tags">
            <span
              v-for="tag in mentor.tags.slice(0, 2)"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 데이터 없음 -->
    <div v-else class="empty-state">
      <p class="empty-icon">☕</p>
      <p>추천 바리스타가 없습니다.</p>
      <small>프로필을 더 자세히 작성해보세요!</small>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  mentors: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
});

defineEmits(['select-mentor']);

// 데이터 가공 로직 (기존 유지)
const topMentors = computed(() => {
  if (!props.mentors || props.mentors.length === 0) return [];
  
  return [...props.mentors]
    .sort((a, b) => {
      const scoreA = parseFloat(a.final_score) || parseFloat(a.matchingScore) || 0;
      const scoreB = parseFloat(b.final_score) || parseFloat(b.matchingScore) || 0;
      return scoreB - scoreA;
    })
    .slice(0, 5)
    .map(mentor => ({
      ...mentor,
      matchingScore: parseFloat(mentor.final_score || mentor.matchingScore || 0).toFixed(1),
      textSimilarity: mentor.textSimilarity ? parseFloat(mentor.textSimilarity).toFixed(1) : '0.0',
      distanceKm: mentor.distanceKm !== undefined ? parseFloat(mentor.distanceKm).toFixed(1) : undefined,
      breakdown: mentor.breakdown 
    }));
});

function formatDistance(km) {
  if (km === undefined || km === null) return '';
  const distance = parseFloat(km);
  if (distance < 1) {
    return `${Math.round(distance * 1000)}m`;
  } else if (distance < 10) {
    return `${distance.toFixed(1)}km`;
  } else {
    return `${Math.round(distance)}km`;
  }
}

function calculateDistanceScore(km) {
  if (km === undefined || km === null) return '0';
  const distance = parseFloat(km);
  const maxDistance = 50;
  if (distance >= maxDistance) return '0';
  const rawScore = 100 * (1 - distance / maxDistance);
  const weightedScore = rawScore * 0.3; 
  return weightedScore.toFixed(0);
}
</script>

<style scoped>
/* 패널 전체: 메모지/메뉴판 느낌 */
.top-mentors-panel {
  background: #d7c8bc; /* 연한 크림색 (메모지) */
  border: 2px solid #5d564d; /* 라떼색 테두리 */
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 15px rgba(54, 18, 5, 0.1);
  width: 280px; /* 적절한 너비 고정 */
  
  /* 종이 질감 패턴 (격자 무늬) */
  background-image: 
    linear-gradient(#d7c8bc 2px, transparent 2px), 
    linear-gradient(90deg, #d7c8bc 2px, transparent 2px);
  background-size: 20px 20px;
  background-position: -2px -2px;
}

.panel-header {
  margin-bottom: 12px;
  text-align: center;
  border-bottom: 2px dashed #100d08; /* 점선 구분선 */
  padding-bottom: 10px;
}

.panel-header h3 {
  font-size: 16px;
  font-weight: 800;
  color: #361205; /* 에스프레소 */
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 11px;
  color: #361205; /* 중간 브라운 */
  margin: 0;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  color: #8A5A34;
  font-size: 13px;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #E6DCCD;
  border-top-color: #DF8723; /* 포인트 컬러 */
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 멘토 리스트 */
.mentors-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mentor-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #FFFFFF; /* 흰색 카드 */
  border: 1px solid #E6DCCD;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.mentor-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(54, 18, 5, 0.08);
  border-color: #DF8723;
}

/* 1등 강조 스타일 (살짝 골드빛) */
.mentor-card.rank-1 {
  background: #FFFBF0; 
  border-color: #DF8723;
}

/* 순위 배지 */
.rank-badge {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 12px;
  background: #E6DCCD;
  color: #5D4037;
}

.rank-1 .rank-badge { background: #DF8723; color: white; }
.rank-2 .rank-badge { background: #D1A872; color: white; }
.rank-3 .rank-badge { background: #A1887F; color: white; }

.mentor-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.info-header h4 {
  font-size: 14px;
  font-weight: 700;
  color: #361205;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90px;
}

.company {
  font-size: 11px;
  color: #8A5A34;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 70px;
}

/* 매칭도 바 */
.match-score {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 4px 0;
}

.score-label {
  font-size: 10px;
  font-weight: 700;
  color: #DF8723;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #EFE5D9;
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  /* 카라멜 그라데이션 */
  background: linear-gradient(90deg, #DF8723 0%, #B15408 100%);
  border-radius: 3px;
}

.score-text {
  font-size: 11px;
  font-weight: 800;
  color: #B15408;
  min-width: 28px;
  text-align: right;
}

/* 거리 정보 */
.distance-info {
  font-size: 11px;
  color: #5D4037;
  display: flex;
  align-items: center;
  gap: 3px;
}

.distance-detail {
  font-size: 10px;
  color: #9CA3AF;
  margin-left: 2px;
}

/* 태그 스타일 */
.tags {
  display: flex;
  gap: 4px;
  margin-top: 4px;
}

.tag {
  padding: 2px 6px;
  background: #FFF3E0; /* 연한 오렌지 배경 */
  color: #E65100;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 600;
  white-space: nowrap;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 30px 10px;
  color: #8A5A34;
}
.empty-icon {
  font-size: 24px;
  margin-bottom: 8px;
}
</style>