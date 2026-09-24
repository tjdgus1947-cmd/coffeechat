<!-- MentorProfileModal.vue (커피챗 테마) -->

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card">
      <button class="close-btn" @click="$emit('close')">✕</button>

      <!-- 헤더 -->
      <div class="modal-header">
        <div class="header-top">
          <button
            class="like-btn"
            :class="{ liked: isLiked }"
            @click="$emit('toggle-like', mentor.id || mentor.user_id)"
            title="찜하기"
          >
            {{ isLiked ? '❤️' : '🤍' }}
          </button>
          <div class="mentor-badge">☕ 멘토</div>
          <div style="width: 44px;"></div>
        </div>

        <div class="mentor-avatar">
          {{ (mentor.name || 'M').charAt(0) }}
        </div>

        <h2 class="mentor-name">{{ mentor.name }}</h2>
        <p class="mentor-company">{{ mentor.company }}</p>
      </div>

      <!-- 매칭도 -->
      <div class="matching-score-section">
        <div class="score-display">
          <span class="label">AI 매칭도</span>
          <div class="score-main">
            <span class="score-value">{{ mentor.matchingScore || 0 }}%</span>
            <div class="score-bar">
              <div class="score-fill" :style="{ width: (mentor.matchingScore || 0) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- 상세 정보 -->
      <div class="modal-body">
        <div class="info-section">
          <h3>💼 경력</h3>
          <p>{{ mentor.team || '정보 없음' }} · {{ mentor.experienceYears || 0 }}년</p>
        </div>

        <div class="info-section">
          <h3>🎯 전문 분야</h3>
          <div class="tags" v-if="mentor.tags && mentor.tags.length > 0">
            <span v-for="tag in mentor.tags" :key="tag" class="tag">{{ tag }}</span>
          </div>
          <p v-else>정보 없음</p>
        </div>

        <div class="info-section">
          <h3>📍 거리</h3>
          <p v-if="mentor.distanceKm !== undefined">
            {{ formatDistance(mentor.distanceKm) }}
          </p>
          <p v-else>정보 없음</p>
        </div>

        <div class="info-section">
          <h3>📝 소개</h3>
          <p class="intro-text">{{ mentor.introduction || '소개 정보가 없습니다.' }}</p>
        </div>
      </div>

      <!-- 버튼 -->
      <div class="modal-footer">
        <button class="btn-secondary" @click="$emit('close')">닫기</button>
        <button class="btn-primary" @click="$emit('book', mentor)">
          ☕ 커피챗 신청
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  mentor: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: String,
    required: true
  },
  isLiked: {
    type: Boolean,
    default: false
  }
});

defineEmits(['close', 'book', 'toggle-like']);

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
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(95, 74, 58, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-card {
  background: linear-gradient(135deg, #fffbf7 0%, #fef8f3 100%);
  border-radius: 24px;
  width: 90%;
  max-width: 520px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(95, 74, 58, 0.25);
  position: relative;
  animation: slideUp 0.3s ease-out;
  border: 2px solid #f0e4d4;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f5e8d8;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 22px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 5;
  transition: all 0.2s;
  color: #a8846f;
}

.close-btn:hover {
  background: #e8d7c3;
  transform: rotate(90deg);
}

/* 헤더 */
.modal-header {
  background: linear-gradient(135deg, #f5e4cc 0%, #f0d9c1 100%);
  padding: 24px 24px 16px;
  text-align: center;
  border-radius: 24px 24px 0 0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.mentor-badge {
  background: linear-gradient(135deg, #f5e4cc 0%, #ead4b8 100%);
  color: #8b6f47;
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid #e8d7c3;
}

.like-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  transition: transform 0.2s;
  padding: 8px;
  position: relative;
  z-index: 20;
  touch-action: manipulation;
}

.like-btn:hover {
  transform: scale(1.15);
}

.like-btn.liked {
  animation: heartBeat 0.3s ease-out;
}

@keyframes heartBeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.35); }
}

.mentor-avatar {
  width: 90px;
  height: 90px;
  background: linear-gradient(135deg, #a8846f 0%, #9a7967 100%);
  color: #fff5e6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  margin: 0 auto 16px;
  box-shadow: 0 8px 24px rgba(168, 132, 111, 0.3);
  border: 3px solid #fff5e6;
}

.mentor-name {
  font-size: 26px;
  font-weight: 800;
  color: #5d4a3a;
  margin: 0 0 6px 0;
}

.mentor-company {
  font-size: 15px;
  color: #8b7355;
  margin: 0;
  font-weight: 500;
}

/* 매칭도 섹션 */
.matching-score-section {
  padding: 18px 24px;
  background: linear-gradient(135deg, #faf5f0 0%, #f7f0ea 100%);
  border-bottom: 2px solid #f0e4d4;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 14px;
}

.label {
  font-size: 13px;
  font-weight: 700;
  color: #8b7355;
  min-width: 80px;
}

.score-main {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-value {
  font-size: 22px;
  font-weight: 900;
  color: #a8846f;
  min-width: 50px;
}

.score-bar {
  flex: 1;
  height: 10px;
  background: #e8d7c3;
  border-radius: 6px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: linear-gradient(90deg, #c9956f 0%, #d4a574 100%);
  transition: width 0.3s ease;
  border-radius: 6px;
}

/* 본문 */
.modal-body {
  padding: 28px 24px;
}

.info-section {
  margin-bottom: 26px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.info-section h3 {
  font-size: 13px;
  font-weight: 800;
  color: #6f5a47;
  margin: 0 0 10px 0;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.info-section p {
  font-size: 15px;
  color: #5d4a3a;
  margin: 0;
  line-height: 1.6;
  font-weight: 500;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  background: linear-gradient(135deg, #f5e4cc 0%, #ead4b8 100%);
  color: #8b6f47;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid #e8d7c3;
}

.intro-text {
  background: linear-gradient(135deg, #faf5f0 0%, #f7f0ea 100%);
  padding: 14px;
  border-radius: 10px;
  border-left: 4px solid #a8846f;
}

/* 푸터 */
.modal-footer {
  padding: 18px 24px 26px;
  display: flex;
  gap: 12px;
  border-top: 2px solid #f0e4d4;
  /* 내용이 길어도 예약/닫기 버튼은 항상 보이게 카드 하단에 고정 */
  position: sticky;
  bottom: 0;
  background: #fffaf5;
  z-index: 2;
}

@media (max-width: 560px) {
  .modal-card { width: calc(100% - 24px); max-height: 88vh; max-height: 88dvh; border-radius: 18px; }
  .modal-footer { padding: 14px 16px 18px; }
}

.btn-secondary,
.btn-primary {
  flex: 1;
  padding: 14px 16px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary {
  background: #f5e8d8;
  color: #8b7355;
  border: 1px solid #e8d7c3;
}

.btn-secondary:hover {
  background: #e8d7c3;
  transform: translateY(-2px);
}

.btn-primary {
  background: linear-gradient(135deg, #a8846f 0%, #9a7967 100%);
  color: #fff5e6;
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #9a7967 0%, #8c6f59 100%);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(168, 132, 111, 0.3);
}

/* 스크롤바 */
.modal-card::-webkit-scrollbar {
  width: 8px;
}

.modal-card::-webkit-scrollbar-track {
  background: #f5e8d8;
  border-radius: 10px;
}

.modal-card::-webkit-scrollbar-thumb {
  background: #d4a574;
  border-radius: 10px;
}

.modal-card::-webkit-scrollbar-thumb:hover {
  background: #c9956f;
}
</style>