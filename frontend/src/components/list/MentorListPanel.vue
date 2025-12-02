<template>
  <div class="menu-board-container">
    <div class="menu-header">
      <h1>☕ COFFEE CHAT MENU</h1>
      <p class="subtitle">오늘의 추천 멘토 & 스페셜 블렌드</p>
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
      <p>☕ 메뉴 준비 중...</p>
    </div>

    <div v-else class="menu-sheet">
      <div class="menu-section" v-if="filteredMentors.length > 0">
        <h2 class="section-title">🌟 Signature Blends (추천)</h2>
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
            <div class="menu-desc">{{ mentor.introduction?.slice(0, 50) }}...</div>
          </div>
        </div>
      </div>

      <div class="menu-section">
        <h2 class="section-title">☕ Regular Beans (전체)</h2>
        <div class="menu-items">
          <div 
            v-for="mentor in filteredMentors.slice(3)" 
            :key="mentor.id"
            class="menu-row"
            @click="selectMentor(mentor)"
          >
            <div class="menu-main">
              <span class="mentor-name">{{ mentor.name }}</span>
              <div class="dots"></div>
              <span class="mentor-company">{{ mentor.company }}</span>
            </div>
            <div class="menu-sub-info">
              <span>경력 {{ mentor.experienceYears }}년</span>
              <span class="divider">|</span>
              <span>매칭도 {{ Math.round(mentor.final_score || 0) }}%</span>
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
});

const emit = defineEmits(['view-profile', 'open-booking']);

const filters = ref({ searchKeyword: '' });

const filteredMentors = computed(() => {
  let result = props.mentors;
  if (filters.value.searchKeyword) {
    const key = filters.value.searchKeyword.toLowerCase();
    result = result.filter(m => 
      (m.name + m.company + m.team).toLowerCase().includes(key)
    );
  }
  // 매칭도 순 정렬
  return result.sort((a, b) => (b.final_score || 0) - (a.final_score || 0));
});

function selectMentor(mentor) {
  emit('view-profile', mentor);
}
</script>

<style scoped>
.menu-board-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 40px;
  background-color: #F7F4E8; /* 크림색 배경 */
  min-height: 80vh;
  font-family: 'Noto Sans KR', serif; /* 명조체 계열이 메뉴판 느낌에 좋음 */
  color: #361205;
}

.menu-header {
  text-align: center;
  margin-bottom: 40px;
  border-bottom: 3px double #361205; /* 이중선으로 클래식한 느낌 */
  padding-bottom: 20px;
}

.menu-header h1 {
  font-size: 2.5rem;
  font-weight: 900;
  letter-spacing: 2px;
  margin: 0;
  font-family: serif; /* 영문은 세리프 폰트 추천 */
}

.filter-paper {
  background: #fff;
  padding: 15px 20px;
  border: 1px dashed #D1A872; /* 점선 테두리 */
  margin-bottom: 30px;
  transform: rotate(-1deg); /* 살짝 비틀어서 종이 붙인 느낌 */
  box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
}

.underline-input {
  border: none;
  border-bottom: 2px solid #D1A872;
  background: transparent;
  padding: 5px;
  font-size: 1rem;
  outline: none;
  color: #361205;
  width: 200px;
}

.menu-sheet {
  background: #fff;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(54, 18, 5, 0.1);
  border-radius: 4px; /* 너무 둥글지 않게 (종이 느낌) */
}

.section-title {
  font-size: 1.4rem;
  color: #DF8723; /* 포인트 컬러 (카라멜) */
  margin-bottom: 20px;
  font-weight: bold;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 40px;
}

.menu-row {
  cursor: pointer;
  padding: 10px;
  transition: background 0.2s;
}

.menu-row:hover {
  background-color: #FDFBF7; /* 아주 연한 크림색 */
}

/* 🔥 핵심: 메뉴판 점선 효과 (Flex box + border-bottom) */
.menu-main {
  display: flex;
  align-items: baseline;
  width: 100%;
}

.mentor-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #361205;
}

.dots {
  flex-grow: 1;
  border-bottom: 2px dotted #D1A872; /* 점선 */
  margin: 0 15px;
  position: relative;
  top: -5px;
}

.mentor-company {
  font-size: 1.1rem;
  font-weight: 600;
  color: #361205;
}

.menu-desc {
  font-size: 0.9rem;
  color: #8A5A34;
  margin-top: 5px;
  padding-left: 5px;
  font-style: italic;
}

.menu-sub-info {
  font-size: 0.85rem;
  color: #D1A872;
  margin-top: 4px;
  text-align: right;
}

.badge {
  background: #DF8723;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
  vertical-align: middle;
  margin-left: 5px;
}
</style>