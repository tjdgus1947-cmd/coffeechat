<template>
  <div class="mentor-list-container">
    <div class="list-header">
      <h1>🎯 추천 멘토 목록</h1>
      <p class="subtitle">AI가 분석한 나와 가장 잘 맞는 멘토들을 만나보세요</p>
    </div>

    <div class="filter-section">
      <div class="filter-group">
        <label>
          <span class="filter-icon">📊</span>
          <span class="filter-label">매칭도</span>
        </label>
        <div class="filter-controls">
          <input
            type="range"
            v-model="filters.minMatchScore"
            min="0"
            max="100"
            class="slider"
          />
          <span class="filter-value">{{ filters.minMatchScore }}% 이상</span>
        </div>
      </div>

      <div class="filter-group">
        <label>
          <span class="filter-icon">📍</span>
          <span class="filter-label">거리</span>
        </label>
        <div class="filter-controls">
          <input
            type="range"
            v-model="filters.maxDistance"
            min="1"
            max="100"
            class="slider"
          />
          <span class="filter-value">{{ filters.maxDistance }}km 이내</span>
        </div>
      </div>

      <div class="filter-group">
        <label>
          <span class="filter-icon">🏢</span>
          <span class="filter-label">전문 분야</span>
        </label>
        <input
          type="text"
          v-model="filters.searchKeyword"
          placeholder="예: 법무, 개발, 디자인..."
          class="search-input"
        />
      </div>

      <button @click="resetFilters" class="reset-button">
        🔄 필터 초기화
      </button>
    </div>

    <div class="sort-section">
      <span class="result-count">{{ filteredMentors.length }}명의 멘토</span>
      <div class="sort-controls">
        <label>정렬:</label>
        <select v-model="sortBy" class="sort-select">
          <option value="matchScore">매칭도 높은 순</option>
          <option value="distance">가까운 순</option>
          <option value="experience">경력 많은 순</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="spinner"></div>
      <p>멘토 목록을 불러오는 중...</p>
    </div>

    <div v-else-if="mentors.length > 0 && filteredMentors.length > 0" class="mentor-list">
      <div
        v-for="(mentor, index) in filteredMentors"
        :key="mentor.id"
        class="mentor-card"
        @click="selectMentor(mentor)"
      >
        <div class="rank-badge" v-if="index < 3">
          <span v-if="index === 0">🥇</span>
          <span v-else-if="index === 1">🥈</span>
          <span v-else>🥉</span>
        </div>

        <div class="mentor-avatar">
          {{ (mentor.name || 'M').charAt(0) }}
        </div>

        <div class="mentor-info">
          <div class="mentor-header">
            <h3>{{ mentor.name || '멘토' }}</h3>
            <span class="mentor-company">{{ mentor.company || '정보 없음' }}</span>
          </div>

          <div class="mentor-details">
            <span class="detail-item">
              <span class="detail-icon">💼</span>
              {{ mentor.team || '정보 없음' }}
            </span>
            <span class="detail-item">
              <span class="detail-icon">📅</span>
              {{ mentor.experienceYears || 0 }}년 경력
            </span>
          </div>

          <div class="tags" v-if="mentor.tags && mentor.tags.length > 0">
            <span
              v-for="tag in mentor.tags.slice(0, 3)"
              :key="tag"
              class="tag"
            >
              {{ tag }}
            </span>
          </div>

          <p class="mentor-intro">{{ mentor.introduction || '소개 정보가 없습니다.' }}</p>
        </div>

        <div class="mentor-scores">
          <div class="score-item primary">
            <span class="score-label">AI 매칭도</span>
            <div class="score-bar">
              <div
                class="score-fill"
                :style="{ width: (mentor.final_score || mentor.matchingScore || 0) + '%' }"
              ></div>
            </div>
            <span class="score-value">{{ (mentor.final_score || mentor.matchingScore || 0) }}%</span>
          </div>

          <div class="score-item" v-if="mentor.distanceKm !== undefined">
            <span class="score-label">거리</span>
            <span class="distance-badge">
              📍 {{ formatDistance(mentor.distanceKm) }}
            </span>
          </div>

          <div class="score-breakdown" v-if="mentor.textSimilarity">
            <small>텍스트 {{ mentor.textSimilarity }}%</small>
            <small v-if="mentor.distanceKm !== undefined">
              • 거리 {{ calculateDistanceScore(mentor.distanceKm) }}%
            </small>
          </div>
        </div>

        <div class="card-actions">
          <button class="action-button primary" @click.stop="openBooking(mentor)">
            ☕ 커피챗 신청
          </button>
          <button class="action-button secondary" @click.stop="viewProfile(mentor)">
            👤 프로필 보기
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p class="empty-icon">🔍</p>
      <p class="empty-text">조건에 맞는 멘토가 없습니다.</p>
      <p class="empty-hint">필터를 조정해보세요!</p>
      <button @click="resetFilters" class="empty-button">
        필터 초기화
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  mentors: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  currentUserId: {
    type: String,
    required: false
  }
});

// ⭐️ 부모에게 이벤트를 보낼 수 있도록 defineEmits를 선언합니다.
const emit = defineEmits(['view-profile', 'open-booking']);

// 필터
const filters = ref({
  minMatchScore: 0,
  maxDistance: 100,
  searchKeyword: ''
});

// 정렬
const sortBy = ref('matchScore');

// 필터링된 멘토 목록
const filteredMentors = computed(() => {
  let result = props.mentors.filter(mentor => {
    // 매칭도 필터
    const score = parseFloat(mentor.final_score || mentor.matchingScore || 0);
    if (score < filters.value.minMatchScore) return false;
    
    // 거리 필터
    if (mentor.distanceKm !== undefined && 
        parseFloat(mentor.distanceKm) > filters.value.maxDistance) return false;
    
    // 키워드 검색
    if (filters.value.searchKeyword) {
      const keyword = filters.value.searchKeyword.toLowerCase();
      const searchText = `${mentor.name} ${mentor.company} ${mentor.team} ${(mentor.tags || []).join(' ')}`.toLowerCase();
      if (!searchText.includes(keyword)) return false;
    }
    
    return true;
  });

  // 정렬
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'matchScore':
        return parseFloat(b.final_score || b.matchingScore || 0) - parseFloat(a.final_score || a.matchingScore || 0);
      case 'distance':
        return (parseFloat(a.distanceKm) || 999) - (parseFloat(b.distanceKm) || 999);
      case 'experience':
        return parseInt(b.experienceYears || 0) - parseInt(a.experienceYears || 0);
      default:
        return 0;
    }
  });

  return result;
});

// 필터 초기화
function resetFilters() {
  filters.value = {
    minMatchScore: 0,
    maxDistance: 100,
    searchKeyword: ''
  };
  sortBy.value = 'matchScore';
}

// 거리 포맷
function formatDistance(km) {
  const distance = parseFloat(km);
  if (distance < 1) return `${Math.round(distance * 1000)}m`;
  if (distance < 10) return `${distance.toFixed(1)}km`;
  return `${Math.round(distance)}km`;
}

// 거리 점수 계산
function calculateDistanceScore(km) {
  const distance = parseFloat(km);
  const maxDistance = 50;
  if (distance >= maxDistance) return 0;
  const rawScore = 100 * (1 - distance / maxDistance);
  return (rawScore * 0.3).toFixed(1);
}

// ⭐️ 멘토 선택 (카드 전체 클릭)
function selectMentor(mentor) {
  // console.log('선택된 멘토:', mentor);
  emit('view-profile', mentor); // '프로필 보기'와 동일하게 동작
}

// ⭐️ 커피챗 신청 (버튼 클릭)
function openBooking(mentor) {
  // console.log('커피챗 신청:', mentor);
  emit('open-booking', mentor);
}

// ⭐️ 프로필 보기 (버튼 클릭)
function viewProfile(mentor) {
  // console.log('프로필 보기:', mentor);
  emit('view-profile', mentor);
}
</script>

<style scoped>
.mentor-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 20px;
}

.list-header {
  text-align: center;
  margin-bottom: 40px;
}

.list-header h1 {
  font-size: 32px;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

.filter-section {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 24px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
}

.filter-icon {
  font-size: 18px;
}

.filter-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  appearance: none;  
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #6d28d9;
  cursor: pointer;
}

.filter-value {
  min-width: 100px;
  font-size: 14px;
  font-weight: 600;
  color: #6d28d9;
}

.search-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #6d28d9;
}

.reset-button {
  padding: 10px 16px;
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.reset-button:hover {
  background: #e5e7eb;
  color: #374151;
}

.sort-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.result-count {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-select {
  padding: 8px 12px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e0e0;
  border-top-color: #6d28d9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.mentor-list {
  display: grid;
  gap: 20px;
}

.mentor-card {
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: grid;
  grid-template-columns: auto 1fr auto auto;
  gap: 20px;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.mentor-card:hover {
  box-shadow: 0 8px 24px rgba(109, 40, 217, 0.12);
  transform: translateY(-2px);
}

.rank-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  font-size: 24px;
}

.mentor-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6d28d9 0%, #a78bfa 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.mentor-info {
  flex: 1;
  min-width: 0;
}

.mentor-header h3 {
  font-size: 20px;
  font-weight: bold;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.mentor-company {
  font-size: 14px;
  color: #6b7280;
}

.mentor-details {
  display: flex;
  gap: 16px;
  margin: 8px 0;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #6b7280;
}

.tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin: 8px 0;
}

.tag {
  padding: 4px 10px;
  background: #ede9fe;
  color: #6d28d9;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.mentor-intro {
  font-size: 14px;
  color: #4b5563;
  margin: 8px 0 0 0;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.mentor-scores {
  min-width: 200px;
}

.score-item {
  margin-bottom: 12px;
}

.score-item.primary .score-value {
  font-size: 20px;
  font-weight: bold;
  color: #6d28d9;
}

.score-label {
  display: block;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.score-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d28d9 0%, #a78bfa 100%);
  transition: width 0.3s ease;
}

.distance-badge {
  display: inline-block;
  padding: 6px 12px;
  background: #f0fdf4;
  color: #16a34a;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.score-breakdown {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #9ca3af;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-button {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.action-button.primary {
  background: #6d28d9;
  color: white;
}

.action-button.primary:hover {
  background: #5b21b6;
}

.action-button.secondary {
  background: #f3f4f6;
  color: #374151;
}

.action-button.secondary:hover {
  background: #e5e7eb;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-text {
  font-size: 20px;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-hint {
  font-size: 14px;
  color: #9ca3af;
  margin: 0 0 24px 0;
}

.empty-button {
  padding: 12px 24px;
  background: #6d28d9;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.empty-button:hover {
  background: #5b21b6;
}

@media (max-width: 768px) {
  .mentor-card {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .mentor-avatar {
    margin: 0 auto;
  }
  
  .card-actions {
    flex-direction: row;
    justify-content: center;
  }
}
</style>