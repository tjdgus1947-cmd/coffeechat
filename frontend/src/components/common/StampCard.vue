<template>
  <div class="coupon-card">
    <div class="coupon-header">
      <h3>☕ COFFEE CHAT CLUB</h3>
      <p>10잔을 채우면 특별한 혜택이! ({{ count }} / 10)</p>
    </div>

    <div class="stamps-grid">
      <div 
        v-for="i in 10" 
        :key="i" 
        class="stamp-slot"
        :class="{ 'stamped': i <= count }"
      >
        <div class="icon-placeholder">☕</div>
        
        <div v-if="i <= count" class="stamp-mark">
          <div class="stamp-inner">
            <span>참 잘했어요</span>
            <span class="date">{{ new Date().toLocaleDateString().slice(5, 10) }}</span>
          </div>
        </div>
        
        <div v-if="i === 10 && count < 10" class="gift-icon">🎁</div>
      </div>
    </div>

    <div class="coupon-footer">
      <p v-if="count >= 10" class="complete-msg">🎉 축하합니다! 골드 멘티 등급 달성!</p>
      <p v-else>커피챗을 완료할 때마다 도장을 찍어드려요.</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  count: {
    type: Number,
    default: 0
  }
});
</script>

<style scoped>
/* 쿠폰 카드 전체 (크라프트지 느낌) */
.coupon-card {
  background-color: #f3e5d0; /* 크라프트 종이 색 */
  background-image: url("https://www.transparenttextures.com/patterns/cardboard.png"); /* 종이 질감 패턴 (선택) */
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  border: 1px dashed #8c6a4f;
  color: #5d4037;
  font-family: 'Courier New', monospace; /* 영수증/쿠폰 느낌 폰트 */
  position: relative;
  overflow: hidden;
}

.coupon-header {
  text-align: center;
  margin-bottom: 20px;
  border-bottom: 2px solid #5d4037;
  padding-bottom: 10px;
}

.coupon-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 900;
  letter-spacing: 1px;
}

.coupon-header p {
  margin: 4px 0 0;
  font-size: 0.8rem;
  opacity: 0.8;
}

/* 스탬프 그리드 (5개씩 2줄) */
.stamps-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

/* 개별 슬롯 */
.stamp-slot {
  aspect-ratio: 1; /* 정사각형 유지 */
  border: 2px dashed #bcaaa4;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-color: rgba(255, 255, 255, 0.4);
}

.icon-placeholder {
  font-size: 1.2rem;
  opacity: 0.3;
  filter: grayscale(100%);
}

.gift-icon {
  position: absolute;
  font-size: 1.4rem;
}

/* 도장 (Stamped) 효과 */
.stamp-mark {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: stamp-bounce 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
  transform: rotate(-15deg); /* 살짝 삐뚤게 찍힘 */
  z-index: 2;
}

/* 도장 내부 디자인 */
.stamp-inner {
  width: 85%;
  height: 85%;
  border: 3px double #d32f2f; /* 빨간 인주 색 */
  border-radius: 50%;
  color: #d32f2f;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 900;
  background-color: rgba(211, 47, 47, 0.1); /* 잉크 번짐 효과 */
  box-shadow: 0 0 0 2px rgba(211, 47, 47, 0.05); /* 외곽 번짐 */
}

.stamp-inner .date {
  font-size: 0.5rem;
  margin-top: 2px;
}

/* 도장 찍히는 애니메이션 */
@keyframes stamp-bounce {
  0% { transform: scale(3) rotate(15deg); opacity: 0; }
  50% { transform: scale(0.9) rotate(-15deg); opacity: 1; }
  100% { transform: scale(1) rotate(-15deg); opacity: 1; }
}

.coupon-footer {
  text-align: center;
  font-size: 0.85rem;
  color: #8d6e63;
}

.complete-msg {
  color: #d32f2f;
  font-weight: bold;
  animation: blink 2s infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
</style>