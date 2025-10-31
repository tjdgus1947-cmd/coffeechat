<template>
  <aside v-if="mentor" class="sidebar-container">
    <button @click="$emit('close')" class="close-button" aria-label="닫기">X</button>
    
    <div class="profile-header">
      <span class="mentor-badge">멘토</span>
      <h2>{{ mentor.name }}</h2>
      <p class="mentor-company">{{ mentor.company }}</p>
    </div>

    <div class="matching-score">
      <span>AI 매칭도</span>
      <strong>{{ mentor.matchingScore }}%</strong>
      <div class="progress-bar">
        <div class="progress" :style="{ width: mentor.matchingScore + '%' }"></div>
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
// defineProps는 import할 필요 없습니다.
defineProps({
  mentor: {
    type: Object,
    default: null, // null이면 v-if="mentor"에 의해 숨겨짐
  },
});

// defineEmits도 import할 필요 없습니다.
defineEmits(['close', 'book']);
</script>

<style scoped>
/* 데모 이미지와 유사한 스타일 */
.sidebar-container {
  width: 300px;
  background-color: #ffffff;
  border-left: 1px solid #e0e0e0;
  padding: 24px;
  color: #333;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-y: auto; /* 내용이 길어지면 스크롤 */
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
  margin-top: 24px; /* 위쪽과 여백 */
  transition: background-color 0.2s;
}
.book-button:hover {
  background-color: #5b21b6;
}
</style>