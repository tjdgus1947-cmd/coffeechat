<template>
  <div 
    class="buzzer-wrapper" 
    :class="status"
    @click="handleClick"
  >
    <div class="buzzer-body">
      <div class="led-lights">
        <span class="led top"></span>
        <span class="led right"></span>
        <span class="led bottom"></span>
        <span class="led left"></span>
      </div>

      <div class="buzzer-center">
        <div class="logo-icon">☕</div>
        <div class="status-text">
          <span v-if="status === 'waiting'">WAITING...</span>
          <span v-else-if="status === 'pickup'">PICK UP</span>
          <span v-else>ORDER</span>
        </div>
      </div>
    </div>
    
    <p class="buzzer-message">{{ message }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  // status: 'idle' (없음), 'waiting' (대기중/진동), 'pickup' (승인됨/반짝임)
  status: {
    type: String,
    default: 'idle'
  }
});

const emit = defineEmits(['click']);

const message = computed(() => {
  switch (props.status) {
    case 'waiting': return '주문(예약) 확인 중입니다...';
    case 'pickup': return '커피챗이 준비되었습니다! (클릭)';
    default: return '새로운 커피챗을 주문해보세요!';
  }
});

function handleClick() {
  if (props.status === 'pickup') {
    emit('click'); // 픽업 상태일 때만 클릭 이벤트 발송 (채팅방 이동 등)
  }
}
</script>

<style scoped>
/* 진동벨 전체 래퍼 */
.buzzer-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: default;
  transition: transform 0.3s;
}

/* 진동벨 몸체 (검정 둥근 사각형) */
.buzzer-body {
  width: 140px;
  height: 140px;
  background: #2c2c2c;
  border-radius: 50%; /* 원형 */
  border: 6px solid #4a4a4a;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 20px rgba(0,0,0,0.3);
}

/* 중앙 로고 영역 */
.buzzer-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
}
.logo-icon { font-size: 32px; margin-bottom: 4px; }
.status-text { 
  font-family: 'Courier New', monospace; 
  font-weight: 900; 
  font-size: 14px; 
  color: #777;
}

/* --- [상태: 대기중 (Waiting)] --- */
/* 붉은색 LED + 진동 */
.buzzer-wrapper.waiting .buzzer-body {
  border-color: #ff4444;
  animation: vibrate 0.4s linear infinite; /* 🔥 진동 애니메이션 */
  box-shadow: 0 0 15px rgba(255, 68, 68, 0.4);
}
.buzzer-wrapper.waiting .status-text { color: #ff4444; text-shadow: 0 0 5px #ff4444; }
.buzzer-wrapper.waiting .led { background-color: #ff4444; box-shadow: 0 0 10px #ff4444; }

/* --- [상태: 픽업 (Pickup)] --- */
/* 초록색 LED + 깜빡임 */
.buzzer-wrapper.pickup { cursor: pointer; }
.buzzer-wrapper.pickup:hover { transform: scale(1.05); }
.buzzer-wrapper.pickup .buzzer-body {
  border-color: #22c55e;
  box-shadow: 0 0 30px rgba(34, 197, 94, 0.6);
  animation: pulse-green 1s infinite alternate;
}
.buzzer-wrapper.pickup .status-text { color: #22c55e; }
.buzzer-wrapper.pickup .led { background-color: #22c55e; box-shadow: 0 0 15px #22c55e; }

/* LED 라이트 위치 잡기 */
.led-lights {
  position: absolute;
  width: 100%; height: 100%;
  border-radius: 50%;
  animation: spin 3s linear infinite; /* 불빛 회전 */
}
.led {
  position: absolute;
  width: 8px; height: 8px;
  border-radius: 50%;
  background-color: #555; /* 꺼진 상태 */
}
.led.top { top: 10px; left: 50%; transform: translateX(-50%); }
.led.bottom { bottom: 10px; left: 50%; transform: translateX(-50%); }
.led.left { left: 10px; top: 50%; transform: translateY(-50%); }
.led.right { right: 10px; top: 50%; transform: translateY(-50%); }

.buzzer-message {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  text-align: center;
  background: white;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid #eee;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* 🔥 핵심 애니메이션: 진동 (Vibrate) */
@keyframes vibrate {
  0% { transform: translate(0); }
  25% { transform: translate(-2px, 2px) rotate(-1deg); }
  50% { transform: translate(2px, -2px) rotate(1deg); }
  75% { transform: translate(-2px, -2px) rotate(-1deg); }
  100% { transform: translate(0) rotate(0); }
}

@keyframes spin { 
  100% { transform: rotate(360deg); } 
}

@keyframes pulse-green {
  from { box-shadow: 0 0 10px rgba(34, 197, 94, 0.4); }
  to { box-shadow: 0 0 25px rgba(34, 197, 94, 0.9); }
}
</style>
