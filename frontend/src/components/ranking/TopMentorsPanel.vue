<template>
  <div class="top-mentors-panel">
    <div class="panel-header">
      <h3>🏆 AI 매칭도 TOP 5</h3>
      <p class="subtitle">나와 가장 잘 맞는 멘토들</p>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>매칭도 계산 중...</p>
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
        <!-- 순위 배지 -->
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
          
          <!-- 매칭도 점수 -->
          <div class="match-score">
            <div class="score-bar">
              <div 
                class="score-fill" 
                :style="{ width: mentor.matchingScore + '%' }"
              ></div>
            </div>
            <span class="score-text">{{ mentor.matchingScore }}%</span>
          </div>

          <!-- 🔥 거리 정보 (컴팩트하게) -->
          <div v-if="mentor.distanceKm !== undefined" class="distance-info">
            <span class="distance-main">
              <span class="icon">📍</span>
              <span class="val">{{ formatDistance(mentor.distanceKm) }}</span>
            </span>
            
            <!-- 상세 정보는 공간 절약을 위해 작은 글씨로 -->
            <span class="distance-detail" v-if="mentor.breakdown">
              (텍스트 {{ mentor.breakdown.text_contribution.toFixed(0) }}% + 거리 {{ mentor.breakdown.distance_contribution.toFixed(0) }}%)
            </span>
            <span class="distance-detail" v-else>
              (텍스트 {{ parseFloat(mentor.textSimilarity).toFixed(0) }}% + 거리 {{ calculateDistanceScore(mentor.distanceKm) }}%)
            </span>
          </div>

          <!-- 전문 분야 태그 (최대 2개, 작게) -->
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

        <!-- 화살표 아이콘 -->
        <div class="arrow-icon">→</div>
      </div>
    </div>

    <!-- 데이터 없음 -->
    <div v-else class="empty-state">
      <p>😔</p>
      <p>추천 멘토가 없습니다.</p>
      <small>프로필을 완성하면 더 정확한 추천을 받을 수 있어요!</small>
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

// TOP 5 데이터 가공 (로직 동일)
const topMentors = computed(() => {
  if (!props.mentors || props.mentors.length === 0) return [];
  
  return [...props.mentors]
    .sort((a, b) => {
      const scoreA = parseFloat(a.final_score) || 0;
      const scoreB = parseFloat(b.final_score) || 0;
      return scoreB - scoreA;
    })
    .slice(0, 5)
    .map(mentor => ({
      ...mentor,
      matchingScore: parseFloat(mentor.final_score || 0).toFixed(1),
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
  if (km === undefined || km === null) return '0'; // 소수점 제거하여 공간 확보
  const distance = parseFloat(km);
  const maxDistance = 50;
  
  if (distance >= maxDistance) return '0';
  
  const rawScore = 100 * (1 - distance / maxDistance);
  const weightedScore = rawScore * 0.3; 
  
  return weightedScore.toFixed(0); // 소수점 제거
}
</script>

<style scoped>
.top-mentors-panel {
  background: white;
  border-radius: 16px;
  /* ✅ 패딩을 줄여서 공간 확보 */
  padding: 16px; 
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-width: 400px;
  height: auto; /* 높이 자동 */
}

.panel-header {
  /* ✅ 헤더 여백 축소 */
  margin-bottom: 12px; 
}

.panel-header h3 {
  font-size: 18px; /* 폰트 약간 축소 */
  font-weight: bold;
  color: #333;
  margin: 0 0 2px 0;
}

.subtitle {
  font-size: 12px;
  color: #666;
  margin: 0;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e0e0e0;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 멘토 리스트 */
.mentors-list {
  display: flex;
  flex-direction: column;
  /* ✅ 카드 간 간격 축소 */
  gap: 8px; 
}

.mentor-card {
  display: flex;
  align-items: center;
  gap: 10px;
  /* ✅ 카드 내부 패딩 축소 */
  padding: 10px 12px; 
  background: #f9fafb;
  border: 1px solid #e5e7eb; /* 테두리 두께 축소 */
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.mentor-card:hover {
  background: #f3f4f6;
  border-color: #6d28d9;
  transform: translateX(2px);
  box-shadow: 0 2px 8px rgba(109, 40, 217, 0.1);
}

.mentor-card.rank-1 {
  background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
  border-color: #fbbf24;
}

/* 순위 배지 (크기 축소) */
.rank-badge {
  flex-shrink: 0;
  width: 28px; /* 36px -> 28px */
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 13px;
  background: #e5e7eb;
  color: #4b5563;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  font-size: 15px;
}
.rank-badge.rank-2 { background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%); color: white; }
.rank-badge.rank-3 { background: linear-gradient(135deg, #f87171 0%, #dc2626 100%); color: white; }

/* 멘토 정보 */
.mentor-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px; /* 요소 간 간격 최소화 */
}

.info-header {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.mentor-info h4 {
  font-size: 14px; /* 16px -> 14px */
  font-weight: bold;
  color: #1f2937;
  margin: 0;
  white-space: nowrap;
}

.company {
  font-size: 11px; /* 13px -> 11px */
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

/* 매칭도 점수 */
.match-score {
  display: flex;
  align-items: center;
  gap: 6px;
  margin: 2px 0;
}

.score-bar {
  flex: 1;
  height: 4px; /* 6px -> 4px */
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d28d9 0%, #a78bfa 100%);
  border-radius: 2px;
}

.score-text {
  font-size: 12px;
  font-weight: bold;
  color: #6d28d9;
  min-width: 36px;
  text-align: right;
}

/* 태그 (더 작게) */
.tags {
  display: flex;
  gap: 4px;
}
.tag {
  padding: 2px 6px;
  background: #ddd6fe;
  color: #6d28d9;
  border-radius: 4px;
  font-size: 10px; /* 11px -> 10px */
  font-weight: 600;
}

/* 거리 정보 (컴팩트) */
.distance-info {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px; /* 패딩 대폭 축소 */
  background: #f0fdf4;
  border-radius: 4px;
  font-size: 11px;
  width: fit-content;
}
.distance-main {
  display: flex;
  align-items: center;
  gap: 2px;
}
.distance-main .val {
  font-weight: 700;
  color: #16a34a;
}
.distance-detail {
  color: #6b7280;
  font-size: 10px;
  margin-left: 4px;
  opacity: 0.8;
}

/* 화살표 아이콘 */
.arrow-icon {
  font-size: 16px;
  color: #d1d5db;
}
.mentor-card:hover .arrow-icon {
  color: #6d28d9;
}

/* 빈 상태 */
.empty-state {
  padding: 40px 20px;
  text-align: center;
}
</style>