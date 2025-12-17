<template>
  <div class="menu-board-container">
    <div class="menu-header">
      <h1>☕ COFFEE CHAT MENU</h1>
      <p class="subtitle">나만의 멘토를 주문하세요</p>
    </div>

    <div class="filter-paper">
      <div class="filter-row">
        <span>취향 선택 (필터):</span>
        <input 
          type="text" 
          v-model="filters.searchKeyword" 
          placeholder="관심 분야 (예: 개발, 마케팅)"
          class="underline-input"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>☕ 메뉴 준비 중...</p>
    </div>

    <div v-else class="menu-sheet">
      
      <div class="menu-section" v-if="likedMentorsList.length > 0">
        <h2 class="section-title signature-title">
          🔖 Signature Blends (My Pick)
        </h2>
        <div class="menu-items">
          <div 
            v-for="mentor in likedMentorsList" 
            :key="'liked-'+mentor.id"
            class="menu-row signature-row"
            @click="selectMentor(mentor)"
          >
            <div class="menu-main">
              <span class="mentor-name">
                {{ mentor.name }}
                <span class="heart-mark">🤎</span>
              </span>
              <div class="dots"></div>
              <span class="mentor-company">{{ mentor.company }}</span>
            </div>
            <div class="menu-desc">
              {{ mentor.introduction?.slice(0, 60) }}...
            </div>
          </div>
        </div>
      </div>

      <div class="menu-section" v-if="filteredMentors.length > 0">
        <h2 class="section-title best-title">
          🏆 Today's Best (AI 추천)
        </h2>
        <div class="menu-items">
          <div 
            v-for="(mentor, index) in filteredMentors.slice(0, 3)" 
            :key="'top-'+mentor.id"
            class="menu-row highlight"
            @click="selectMentor(mentor)"
          >
            <div class="menu-main">
              <span class="mentor-name">
                {{ mentor.name }} 
                <span class="badge">BEST</span>
              </span>
              <div class="dots"></div>
              <span class="mentor-company">{{ mentor.company }} / {{ mentor.team }}</span>
            </div>
            <div class="menu-sub-info">
              <span>Fit {{ Math.round(mentor.final_score || 0) }}%</span>
              <span class="divider">|</span>
              <span>{{ mentor.topics?.split(',')[0] || '전문가' }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h2 class="section-title regular-title">
          ☕ Regular Beans (전체 멘토)
        </h2>
        <div class="menu-items">
          <div 
            v-for="mentor in filteredMentors.slice(3)" 
            :key="mentor.id"
            class="menu-row"
            @click="selectMentor(mentor)"
          >
            <div class="menu-main">
              <span class="mentor-name">
                {{ mentor.name }}
                <span v-if="isLiked(mentor.id)" class="heart-mark-small">🤎</span>
              </span>
              <div class="dots"></div>
              <span class="mentor-company">{{ mentor.company }}</span>
            </div>
            <div class="menu-sub-info">
              <span>경력 {{ mentor.experienceYears }}년</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  mentors: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  likedMentorIds: { type: Array, default: () => [] } 
});

const emit = defineEmits(['view-profile', 'open-booking']);

const filters = ref({ searchKeyword: '' });

// 찜한 멘토 목록
const likedMentorsList = computed(() => {
  if (!props.likedMentorIds || props.likedMentorIds.length === 0) return [];
  return props.mentors.filter(m => props.likedMentorIds.includes(m.id || m.user_id));
});

function isLiked(mentorId) {
  return props.likedMentorIds.includes(mentorId);
}

// 검색 필터 및 정렬 (매칭도 순)
const filteredMentors = computed(() => {
  let result = props.mentors;
  if (filters.value.searchKeyword) {
    const key = filters.value.searchKeyword.toLowerCase();
    result = result.filter(m => 
      (m.name + m.company + m.team).toLowerCase().includes(key)
    );
  }
  return [...result].sort((a, b) => (b.final_score || 0) - (a.final_score || 0));
});

function selectMentor(mentor) {
  emit('view-profile', mentor);
}
</script>

<style scoped>
/* 전체 배경: 크림색 메뉴판 */
.menu-board-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #F7F4E8;
  min-height: 80vh;
  font-family: 'Noto Sans KR', serif; /* 명조체로 메뉴판 느낌 살리기 */
  color: #3e2723;
}

/* 헤더 */
.menu-header {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 3px double #3e2723;
  padding-bottom: 20px;
}

.menu-header h1 {
  font-size: 2.2rem;
  font-weight: 900;
  letter-spacing: 2px;
  margin: 0;
  color: #3e2723;
  font-family: serif;
}

.subtitle {
  color: #8d6e63;
  margin-top: 8px;
  font-size: 0.95rem;
  letter-spacing: 1px;
}

/* 필터 영역 (찢어진 종이 느낌) */
.filter-paper {
  background: #fff;
  padding: 15px 20px;
  border: 1px dashed #d7ccc8;
  margin-bottom: 30px;
  transform: rotate(-0.5deg);
  box-shadow: 2px 2px 5px rgba(0,0,0,0.03);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  color: #5d4037;
}

.underline-input {
  border: none;
  border-bottom: 2px solid #8d6e63;
  background: transparent;
  padding: 5px;
  font-size: 1rem;
  outline: none;
  color: #3e2723;
  width: 220px;
  font-family: inherit;
}

/* 메뉴판 본문 (흰색 종이) */
.menu-sheet {
  background: #fff;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(62, 39, 35, 0.08);
  border-radius: 2px;
  position: relative;
}

/* 각 섹션 */
.menu-section {
  margin-bottom: 50px;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid #efebe9;
  font-family: serif;
}

.signature-title { color: #bf360c; /* 진한 오렌지/갈색 */ }
.best-title { color: #f57f17; /* 골드/오렌지 */ }
.regular-title { color: #5d4037; /* 에스프레소 */ }

/* 메뉴 아이템 리스트 */
.menu-items {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* 개별 메뉴 행 (Row) */
.menu-row {
  cursor: pointer;
  padding: 8px 10px;
  transition: background 0.2s;
  border-radius: 4px;
}

.menu-row:hover {
  background-color: #fff8e1; /* 연한 노란빛 */
}

/* 🔖 시그니처(찜) 강조 스타일 */
.signature-row {
  background-color: #fff3e0; /* 연한 살구색 배경으로 강조 */
  border: 1px solid #ffe0b2;
}
.signature-row:hover {
  background-color: #ffe0b2;
}

/* 메뉴 메인 정보 (이름 ...... 회사) */
.menu-main {
  display: flex;
  align-items: baseline;
  width: 100%;
}

.mentor-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: #3e2723;
  white-space: nowrap;
}

/* 점선 (Leader dots) */
.dots {
  flex-grow: 1;
  border-bottom: 2px dotted #bcaaa4;
  margin: 0 12px;
  position: relative;
  top: -5px;
  opacity: 0.6;
}

.mentor-company {
  font-size: 1rem;
  font-weight: 600;
  color: #3e2723;
  white-space: nowrap;
}

/* 설명 및 서브 정보 */
.menu-desc {
  font-size: 0.9rem;
  color: #795548;
  margin-top: 4px;
  padding-left: 4px;
  font-style: italic;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.menu-sub-info {
  font-size: 0.85rem;
  color: #a1887f;
  margin-top: 4px;
  text-align: right;
}

.badge {
  background: #f57f17;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  vertical-align: middle;
  margin-left: 6px;
}

.heart-mark {
  font-size: 1rem;
  margin-left: 6px;
}
.heart-mark-small {
  font-size: 0.9rem;
  margin-left: 6px;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #8d6e63;
}
.spinner {
  border: 4px solid #efebe9;
  border-top: 4px solid #8d6e63;
  border-radius: 50%;
  width: 40px; height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>