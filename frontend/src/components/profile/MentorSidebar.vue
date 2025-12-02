<template>
  <aside v-if="mentor" class="sidebar-container">
    <button @click="$emit('close')" class="close-button" aria-label="닫기">✕</button>
    
    <div class="profile-header">
      <span class="mentor-badge">MENTOR</span>
      <h2>{{ mentor.full_name || mentor.name || '멘토' }}</h2>
      <p class="mentor-company">
        {{ mentor.company || mentor.career_info || '소속 정보 없음' }}
      </p>
    </div>

    <div class="matching-score">
      <div class="score-header">
        <span>{{ isMentorView ? '성향 일치도' : 'AI 매칭 점수' }}</span>
        <strong class="score-text">{{ displayScore }}%</strong>
      </div>
      
      <div class="progress-bar">
        <div class="progress" :style="{ width: displayScore + '%' }"></div>
      </div>

      <div class="score-desc">
        <small v-if="isMentorView">
          관심사 및 커리어 벡터 유사도 분석 결과입니다.
        </small>
        <small v-else>
          자기소개 유사도와 물리적 거리를 종합한 점수입니다.
        </small>
      </div>
    </div>

    <div class="mentor-details">
      <div class="detail-item">
        <h3>소속 및 직무</h3>
        <p>{{ mentor.team || '정보 없음' }}</p>
      </div>

      <div class="detail-item">
        <h3>경력</h3>
        <p>{{ mentor.experienceYears ? mentor.experienceYears + '년' : '정보 없음' }}</p>
      </div>

      <div class="detail-item">
        <h3>전문 분야</h3>
        <div class="tags" v-if="mentor.tags && mentor.tags.length > 0">
          <span v-for="tag in mentor.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
        <p v-else style="color: #999; font-size: 13px;">등록된 태그가 없습니다.</p>
      </div>

      <div class="detail-item">
        <h3>멘토 소개</h3>
        <p class="intro-text">{{ mentor.introduction || mentor.career_info || '소개글이 없습니다.' }}</p>
      </div>
    </div>
    
    <div class="footer-actions">
      <button @click="$emit('book', mentor)" class="book-button">
        커피챗 요청하기
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  mentor: {
    type: Object,
    default: null,
  },
  currentUserId: {
    type: String,
    required: true
  },
  // 부모 컴포넌트(MentorNetworkView)에서 true로 전달
  isMentorView: {
    type: Boolean,
    default: false
  }
});

defineEmits(['close', 'book']);

// ⭐️ 점수 계산 로직
// 디자인은 같지만, 점수는 'isMentorView'에 따라 다른 필드를 참조합니다.
const displayScore = computed(() => {
  if (!props.mentor) return 0;

  // 1. 멘토-멘토 뷰일 때 (벡터 유사도 우선)
  if (props.isMentorView) {
    // MentorNetworkView에서 넘겨준 matchingScore 혹은 similarity 사용
    if (props.mentor.matchingScore !== undefined) return parseFloat(props.mentor.matchingScore);
    if (props.mentor.similarity !== undefined) return (props.mentor.similarity * 100).toFixed(1);
  } 
  
  // 2. 멘티-멘토 뷰일 때 (AI 매칭 점수 우선)
  // MenteeNetworkView에서 넘겨준 final_score 사용
  if (props.mentor.final_score !== undefined) {
    return parseFloat(props.mentor.final_score).toFixed(1);
  }
  
  return 0;
});
</script>

<style scoped>
.sidebar-container {
  width: 320px;
  background-color: #ffffff;
  border-left: 1px solid #e5e7eb;
  padding: 0; 
  color: #1f2937;
  display: flex;
  flex-direction: column;
  position: relative;
  box-shadow: -4px 0 20px rgba(0,0,0,0.08);
  height: 100%;
  z-index: 50;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  font-size: 18px;
  color: #9ca3af;
  cursor: pointer;
  z-index: 10;
}
.close-button:hover { color: #4b5563; }

/* 헤더 */
.profile-header {
  padding: 40px 24px 20px;
  text-align: center;
  border-bottom: 1px solid #f3f4f6;
  background: #fff;
}
.mentor-badge {
  background-color: #f5f3ff;
  color: #7c3aed;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.5px;
  display: inline-block;
  margin-bottom: 12px;
}
.profile-header h2 {
  font-size: 22px;
  font-weight: 400;
  margin: 0 0 8px;
  color: #111827;
}
.mentor-company {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
  font-weight: 500;
}

/* 매칭 스코어 */
.matching-score {
  padding: 24px;
  background: #fafafa;
  border-bottom: 1px solid #f3f4f6;
}
.score-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.score-header span { font-size: 13px; font-weight: 600; color: #4b5563; }
.score-text { color: #7c3aed; font-size: 20px; font-weight: 800; }

.progress-bar {
  background-color: #e5e7eb;
  border-radius: 6px;
  height: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}
.progress {
  background-color: #7c3aed;
  height: 100%;
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.score-desc {
  text-align: right;
  font-size: 11px;
  color: #9ca3af;
}

/* 상세 정보 (스크롤 영역) */
.mentor-details {
  padding: 24px;
  flex: 1;
  overflow-y: auto; /* 내용이 길면 스크롤 */
}
.detail-item { margin-bottom: 24px; }
.detail-item h3 {
  font-size: 12px;
  font-weight: 700;
  color: #9ca3af;
  margin: 0 0 8px;
  text-transform: uppercase;
}
.detail-item p {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}
.intro-text { white-space: pre-wrap; }

.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  background-color: #f3f4f6;
  color: #4b5563;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 500;
}

/* 하단 버튼 */
.footer-actions {
  padding: 20px 24px;
  border-top: 1px solid #f3f4f6;
  background: #fff;
}
.book-button {
  width: 100%;
  background-color: #7c3aed;
  color: white;
  padding: 14px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(124, 58, 237, 0.1);
}
.book-button:hover {
  background-color: #6d28d9;
  transform: translateY(-1px);
  box-shadow: 0 6px 12px -1px rgba(124, 58, 237, 0.2);
}
</style>