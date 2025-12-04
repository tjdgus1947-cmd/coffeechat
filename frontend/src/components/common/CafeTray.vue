<template>
  <div class="tray-container">
    <div class="wood-tray">
      <div class="tray-handle left"></div>
      <div class="tray-handle right"></div>
      
      <div class="tray-surface">
        <div v-if="items.length > 0" class="items-grid">
          <div v-for="item in items" :key="item.id" class="tray-set">
            
            <div class="coffee-cup" @click="$emit('enter-chat', item)" title="채팅방 입장">
              <div class="steam-animation">
                <span></span><span></span><span></span>
              </div>
              <div class="cup-body">
                <div class="cup-sleeve">
                  {{ item.mentor?.full_name?.charAt(0) || 'M' }}
                </div>
              </div>
              <div class="cup-plate"></div>
            </div>

            <div class="order-ticket">
              <div class="ticket-header">ORDER #{{ item.id.slice(0, 4) }}</div>
              <div class="ticket-body">
                <p class="mentor-name">{{ item.mentor?.full_name || '멘토' }}님</p>
                <p class="schedule">{{ formatSchedule(item.start_time) }}</p>
                <button class="chat-btn" @click="$emit('enter-chat', item)">입장하기</button>
              </div>
            </div>

          </div>
        </div>

        <div v-else class="empty-tray">
          <div class="napkin">
            <p>준비된 메뉴가 없습니다.</p>
            <p class="sub">새로운 커피챗을 주문해보세요!</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    default: () => []
  }
});

defineEmits(['enter-chat']);

function formatSchedule(isoString) {
  if (!isoString) return '시간 미정';
  const date = new Date(isoString);
  return date.toLocaleString('ko-KR', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}
</script>

<style scoped>
/* 우드 트레이 전체 컨테이너 */
.tray-container {
  width: 100%;
  display: flex;
  justify-content: center;
  perspective: 1000px; /* 3D 효과를 위한 원근감 */
}

/* 트레이 몸체 (나무 질감) */
.wood-tray {
  position: relative;
  width: 100%;
  min-height: 220px;
  background-color: #8d6e63;
  background-image: url("https://www.transparenttextures.com/patterns/wood-pattern.png");
  border-radius: 20px;
  box-shadow: 
    0 20px 50px rgba(0,0,0,0.3),
    inset 0 0 0 5px #6d4c41, /* 안쪽 테두리 */
    inset 0 0 20px rgba(0,0,0,0.5); /* 안쪽 그림자 */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
  transform: rotateX(10deg); /* 살짝 기울여서 입체감 주기 */
}

/* 손잡이 */
.tray-handle {
  position: absolute;
  top: 50%;
  width: 40px;
  height: 80px;
  background: #5d4037;
  border-radius: 8px;
  transform: translateY(-50%);
  box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
}
.tray-handle.left { left: -10px; border-top-right-radius: 0; border-bottom-right-radius: 0; }
.tray-handle.right { right: -10px; border-top-left-radius: 0; border-bottom-left-radius: 0; }

.tray-surface {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
}

/* 아이템 그리드 */
.items-grid {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
  justify-content: center;
}

.tray-set {
  display: flex;
  align-items: flex-end; /* 컵과 영수증 바닥 맞춤 */
  gap: 15px;
}

/* ☕ 커피잔 스타일 */
.coffee-cup {
  position: relative;
  width: 70px;
  height: 90px;
  cursor: pointer;
  transition: transform 0.2s;
  z-index: 10;
}
.coffee-cup:hover { transform: translateY(-5px) scale(1.05); }

.cup-body {
  width: 100%;
  height: 100%;
  background: #fdfbf7; /* 종이컵 색 */
  border-radius: 0 0 10px 10px;
  position: relative;
  box-shadow: -5px 0 10px rgba(0,0,0,0.1);
  overflow: hidden;
  border-top: 5px solid #eee; /* 뚜껑 느낌 */
}

.cup-sleeve {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 110%;
  height: 40px;
  background: #8d6e63; /* 컵 홀더 색 */
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.cup-plate {
  position: absolute;
  bottom: -5px;
  left: -10px;
  width: 90px;
  height: 10px;
  background: rgba(0,0,0,0.2);
  border-radius: 50%;
  filter: blur(4px);
  z-index: -1;
}

/* 김이 모락모락 */
.steam-animation span {
  position: absolute;
  top: -20px;
  width: 4px;
  height: 20px;
  background: white;
  opacity: 0;
  border-radius: 50%;
  animation: steam 2s infinite;
}
.steam-animation span:nth-child(1) { left: 20px; animation-delay: 0.5s; }
.steam-animation span:nth-child(2) { left: 35px; animation-delay: 1s; }
.steam-animation span:nth-child(3) { left: 50px; animation-delay: 1.5s; }

@keyframes steam {
  0% { transform: translateY(0) scaleX(1); opacity: 0; }
  50% { opacity: 0.6; }
  100% { transform: translateY(-30px) scaleX(2); opacity: 0; }
}

/* 🧾 주문서(티켓) 스타일 */
.order-ticket {
  width: 140px;
  background: #fff;
  padding: 15px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  transform: rotate(3deg); /* 살짝 삐뚤게 */
  position: relative;
}
.order-ticket::after { /* 상단 테이프 */
  content: '';
  position: absolute;
  top: -10px; left: 50%;
  transform: translateX(-50%);
  width: 40px; height: 15px;
  background: rgba(255, 255, 255, 0.4);
  border: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.ticket-header {
  border-bottom: 2px dashed #ddd;
  padding-bottom: 5px;
  margin-bottom: 10px;
  font-weight: bold;
  text-align: center;
  color: #555;
}

.mentor-name { font-size: 0.9rem; font-weight: 800; margin: 0; color: #333; }
.schedule { font-size: 0.75rem; color: #666; margin: 4px 0 10px; }

.chat-btn {
  width: 100%;
  padding: 6px;
  background: #333;
  color: white;
  border: none;
  font-size: 0.7rem;
  cursor: pointer;
  font-weight: bold;
}
.chat-btn:hover { background: #555; }

/* 냅킨 (빈 상태) */
.empty-tray {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}
.napkin {
  background: #fdfbf7;
  padding: 30px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
  transform: rotate(-2deg);
  text-align: center;
  color: #8d6e63;
  font-family: 'Gowun Dodum', sans-serif; /* 손글씨 느낌 폰트 권장 */
}
.napkin p { margin: 0; font-weight: bold; }
.napkin .sub { font-size: 0.8rem; margin-top: 5px; opacity: 0.8; font-weight: normal; }
</style>