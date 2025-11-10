<template>
  <!-- 모달 오버레이 -->
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="mentor" class="modal-overlay" @click="$emit('close')">
        <div class="modal-container" @click.stop>
          <!-- 닫기 버튼 -->
          <button @click="$emit('close')" class="close-button" aria-label="닫기">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          <!-- 프로필 헤더 -->
          <div class="profile-header">
            <div class="profile-image">
              <img 
                :src="mentor.profileImage || 'https://via.placeholder.com/80'" 
                :alt="mentor.name"
                class="avatar"
              />
            </div>
            <h2 class="mentor-name">{{ mentor.name }}</h2>
            <p class="mentor-role">{{ mentor.role || 'Senior Developer' }}</p>
          </div>

          <!-- AI 매칭도 -->
          <div class="matching-section">
            <div class="matching-label">AI 매칭도</div>
            <div class="matching-value">{{ mentor.matchingScore || 92 }}%</div>
            <div class="progress-bar">
              <div class="progress" :style="{ width: (mentor.matchingScore || 92) + '%' }"></div>
            </div>
          </div>

          <!-- 소속 정보 -->
          <div class="info-section">
            <h3 class="section-title">소속</h3>
            <p class="section-content company">{{ mentor.company || mentor.team || '네이버' }}</p>
          </div>

          <!-- 위치 정보 -->
          <div class="info-section">
            <div class="location-row">
              <svg class="location-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <span class="location-text">{{ mentor.location || '서울 강남' }}</span>
            </div>
          </div>

          <!-- 평점 -->
          <div class="info-section">
            <div class="rating-row">
              <svg class="star-icon" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
              </svg>
              <span class="rating-value">{{ mentor.rating || 4.8 }}</span>
              <span class="rating-count">({{ mentor.reviewCount || 98 }} 리뷰)</span>
            </div>
          </div>

          <!-- 전문 분야 -->
          <div class="info-section">
            <h3 class="section-title">전문 분야</h3>
            <div class="tags">
              <span v-for="tag in (mentor.tags || ['풀스택 개발', '시스템 설계', '멘토링'])" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 커피챗 비용 -->
          <div class="info-section">
            <h3 class="section-title">커피챗 비용</h3>
            <p class="price">₩{{ (mentor.price || 40000).toLocaleString() }}</p>
          </div>

          <!-- 소개 -->
          <div class="info-section">
            <h3 class="section-title">소개</h3>
            <p class="intro-text">
              {{ mentor.introduction || '네이버에서 Senior Developer로 근무하고 있으며, 풀스택 개발, 시스템 설계, 멘토링 분야의 전문가입니다. 함께 성장하는 커피챗을 기대합니다.' }}
            </p>
          </div>

          <!-- 커피챗 예약 버튼 -->
          <button @click="$emit('book', mentor)" class="book-button">
            <svg class="calendar-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            커피챗 예약하기
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
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
/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

/* 모달 컨테이너 */
.modal-container {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: 32px;
}

/* 닫기 버튼 */
.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #9ca3af;
  transition: color 0.2s;
  z-index: 10;
}

.close-button:hover {
  color: #374151;
}

.close-button svg {
  width: 24px;
  height: 24px;
}

/* 프로필 헤더 */
.profile-header {
  text-align: center;
  margin-bottom: 24px;
}

.profile-image {
  margin-bottom: 16px;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #f3f4f6;
}

.mentor-name {
  font-size: 24px;
  font-weight: bold;
  color: #111827;
  margin: 0 0 4px 0;
}

.mentor-role {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

/* AI 매칭도 섹션 */
.matching-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  text-align: center;
}

.matching-label {
  font-size: 14px;
  color: white;
  margin-bottom: 4px;
  opacity: 0.9;
}

.matching-value {
  font-size: 32px;
  font-weight: bold;
  color: white;
  margin-bottom: 12px;
}

.progress-bar {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 9999px;
  height: 8px;
  overflow: hidden;
}

.progress {
  background-color: white;
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}

/* 정보 섹션 */
.info-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 8px 0;
}

.section-content {
  font-size: 16px;
  color: #111827;
  margin: 0;
}

.company {
  color: #7c3aed;
  font-weight: 500;
}

/* 위치 정보 */
.location-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.location-icon {
  width: 20px;
  height: 20px;
  color: #6b7280;
}

.location-text {
  font-size: 15px;
  color: #374151;
}

/* 평점 */
.rating-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.star-icon {
  width: 20px;
  height: 20px;
  color: #fbbf24;
}

.rating-value {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.rating-count {
  font-size: 14px;
  color: #6b7280;
}

/* 태그 */
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background-color: #dbeafe;
  color: #1e40af;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
}

/* 가격 */
.price {
  font-size: 20px;
  font-weight: bold;
  color: #7c3aed;
  margin: 0;
}

/* 소개 텍스트 */
.intro-text {
  font-size: 14px;
  line-height: 1.6;
  color: #374151;
  margin: 0;
}

/* 커피챗 예약 버튼 */
.book-button {
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.book-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
}

.book-button:active {
  transform: translateY(0);
}

.calendar-icon {
  width: 20px;
  height: 20px;
}

/* 모달 트랜지션 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.9);
}

/* 스크롤바 스타일 */
.modal-container::-webkit-scrollbar {
  width: 6px;
}

.modal-container::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 10px;
}

.modal-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 10px;
}

.modal-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}
</style>