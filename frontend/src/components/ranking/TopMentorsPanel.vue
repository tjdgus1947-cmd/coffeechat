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
          <h4>{{ mentor.name }}</h4>
          <p class="company">{{ mentor.company }}</p>
          
          <!-- 매칭도 점수 -->
          <div class="match-score">
            <div class="score-bar">
              <div 
                class="score-fill" 
                :style="{ width: mentor.matchingScore + '%' }"
              ></div>
            </div>
            <!-- ⭐️ 템플릿은 수정할 필요 없습니다. computed가 'matchingScore'를 올바르게 채워줍니다. -->
            <span class="score-text">{{ mentor.matchingScore }}%</span>
          </div>

          <!-- 🔥 거리 정보 -->
          <div v-if="mentor.distanceKm !== undefined" class="distance-info">
            <span class="distance-icon">📍</span>
            <span class="distance-text">{{ formatDistance(mentor.distanceKm) }}</span>
            
            <!-- ⭐️ [수정] 백엔드의 breakdown 값을 사용합니다. -->
            <span class="distance-detail" v-if="mentor.breakdown">
              (텍스트 {{ mentor.breakdown.text_contribution.toFixed(1) }}% + 거리 {{ mentor.breakdown.distance_contribution.toFixed(1) }}%)
            </span>
            <!-- ⭐️ [수정] breakdown이 없을 경우를 대비한 텍스트 -->
            <span class="distance-detail" v-else>
              (텍스트 {{ mentor.textSimilarity }}% + 거리 {{ calculateDistanceScore(mentor.distanceKm) }}%)
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

// ⭐️⭐️⭐️ [핵심 수정] ⭐️⭐️⭐️
// 매칭도 순으로 정렬하여 TOP 5 추출
const topMentors = computed(() => {
  if (!props.mentors || props.mentors.length === 0) return [];
  
  return [...props.mentors]
    .sort((a, b) => {
      // ⭐️ 수정: 'matchingScore' 대신 'final_score'로 정렬합니다.
      const scoreA = parseFloat(a.final_score) || 0;
      const scoreB = parseFloat(b.final_score) || 0;
      return scoreB - scoreA;
    })
    .slice(0, 5)
    .map(mentor => ({
      ...mentor,
      // ⭐️ 수정: 템플릿에서 사용할 'matchingScore' 값을
      // ⭐️ 백엔드의 'final_score' 값으로 덮어씁니다.
      matchingScore: parseFloat(mentor.final_score || 0).toFixed(1),
      
      textSimilarity: mentor.textSimilarity ? parseFloat(mentor.textSimilarity).toFixed(1) : '0.0',
      distanceKm: mentor.distanceKm !== undefined ? parseFloat(mentor.distanceKm).toFixed(1) : undefined,
      
      // ⭐️ breakdown 객체도 그대로 전달
      breakdown: mentor.breakdown 
    }));
});

// 🔥 신규: 거리를 읽기 쉬운 형식으로 변환
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

// 🔥 신규: 거리 점수 계산 (30% 가중치 반영)
function calculateDistanceScore(km) {
  if (km === undefined || km === null) return '0.0';
  const distance = parseFloat(km);
  const maxDistance = 50; // 최대 거리 기준
  
  if (distance >= maxDistance) return '0.0';
  
  const rawScore = 100 * (1 - distance / maxDistance);
  // ⭐️ 수정: breakdown이 없을 때를 대비한 계산이므로 30% 가중치 적용
  const weightedScore = rawScore * 0.3; 
  
  return weightedScore.toFixed(1);
}
</script>

<style scoped>
.top-mentors-panel {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  max-width: 400px;
  min-height: 500px;
}

.panel-header {
  margin-bottom: 20px;
}

.panel-header h3 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 0 0 4px 0;
}

.subtitle {
  font-size: 13px;
  color: #666;
  margin: 0;
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e0e0e0;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 멘토 리스트 */
.mentors-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mentor-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.mentor-card:hover {
  background: #f3f4f6;
  border-color: #6d28d9;
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.1);
}

.mentor-card.rank-1 {
  background: linear-gradient(135deg, #fff9e6 0%, #ffffff 100%);
  border-color: #fbbf24;
  box-shadow: 0 4px 16px rgba(251, 191, 36, 0.15);
}

/* 순위 배지 */
.rank-badge {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 16px;
  background: #e5e7eb;
  color: #4b5563;
}

.rank-badge.rank-1 {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
  font-size: 18px;
}

.rank-badge.rank-2 {
  background: linear-gradient(135deg, #d1d5db 0%, #9ca3af 100%);
  color: white;
}

.rank-badge.rank-3 {
  background: linear-gradient(135deg, #f87171 0%, #dc2626 100%);
  color: white;
}

/* 멘토 정보 */
.mentor-info {
  flex: 1;
  min-width: 0;
}

.mentor-info h4 {
  font-size: 16px;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.company {
  font-size: 13px;
  color: #6b7280;
  margin: 0 0 8px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 매칭도 점수 */
.match-score {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d28d9 0%, #a78bfa 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.score-text {
  font-size: 14px;
  font-weight: bold;
  color: #6d28d9;
  min-width: 45px;
  text-align: right;
}

/* 태그 */
.tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.tag {
  display: inline-block;
  padding: 4px 8px;
  background: #ddd6fe;
  color: #6d28d9;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

/* 🔥 신규: 거리 정보 스타일 */
.distance-info {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 6px;
  padding: 6px 8px;
  background: #f0fdf4;
  border-radius: 8px;
  font-size: 12px;
}

.distance-icon {
  font-size: 14px;
}

.distance-text {
  font-weight: 700;
  color: #16a34a;
}

.distance-detail {
  color: #6b7280;
  font-size: 10px;
  margin-left: auto;
  white-space: nowrap;
}

/* 화살표 아이콘 */
.arrow-icon {
  flex-shrink: 0;
  font-size: 20px;
  color: #9ca3af;
  transition: transform 0.2s;
}

.mentor-card:hover .arrow-icon {
  transform: translateX(4px);
  color: #6d28d9;
}

/* 빈 상태 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-state p:first-child {
  font-size: 48px;
  margin: 0 0 12px 0;
}

.empty-state p:nth-child(2) {
  font-size: 16px;
  font-weight: 600;
  color: #4b5563;
  margin: 0 0 8px 0;
}

.empty-state small {
  font-size: 13px;
  color: #9ca3af;
}
</style>