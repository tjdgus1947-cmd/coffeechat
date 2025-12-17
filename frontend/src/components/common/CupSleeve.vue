<template>
  <div class="cup-wrapper" @click="$emit('click')">
    <div class="cup-lid">
      <div class="lid-top"></div>
      <div class="lid-bottom"></div>
    </div>
    
    <div class="cup-body">
      <div class="sleeve" :style="{ backgroundColor: sleeveColor }">
        <div class="sleeve-content">
          <span class="mentor-name">{{ mentor.name || mentor.full_name }}</span>
          <span class="mentor-company">{{ mentor.company || '멘토' }}</span>
        </div>
      </div>
    </div>
    <div class="cup-shadow"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  mentor: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0
  }
});

// 컵 홀더 색상을 다양하게 (랜덤 느낌)
const sleeveColor = computed(() => {
  const colors = ['#8d6e63', '#a1887f', '#795548', '#6d4c41', '#5d4037'];
  return colors[props.index % colors.length];
});
</script>

<style scoped>
.cup-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: transform 0.2s;
  width: 90px;
  flex-shrink: 0; /* 가로 스크롤 시 줄어들지 않도록 */
}

.cup-wrapper:hover {
  transform: translateY(-5px);
}

/* 뚜껑 */
.cup-lid {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}
.lid-top {
  width: 80px;
  height: 8px;
  background: #eee;
  border-radius: 4px 4px 0 0;
  border: 1px solid #ddd;
}
.lid-bottom {
  width: 86px;
  height: 12px;
  background: #fff;
  border: 1px solid #ddd;
  border-bottom: 2px solid #ccc;
  border-radius: 2px;
  margin-bottom: -2px;
  z-index: 2;
}

/* 컵 몸통 */
.cup-body {
  width: 70px;
  height: 100px;
  background: #fdfbf7;
  border: 1px solid #e0e0e0;
  border-top: none;
  position: relative;
  /* 사다리꼴 만들기 */
  transform: perspective(200px) rotateX(-5deg);
  transform-origin: top;
  border-radius: 0 0 10px 10px;
  overflow: hidden;
  box-shadow: inset -5px 0 10px rgba(0,0,0,0.03);
}

/* 컵 홀더 (슬리브) */
.sleeve {
  position: absolute;
  top: 25px;
  left: -5px; /* 몸통보다 약간 튀어나오게 */
  width: calc(100% + 10px);
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.15);
  transform: translateZ(10px); /* 입체감 */
}

.sleeve-content {
  text-align: center;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  padding: 0 5px;
}

.mentor-name {
  font-size: 11px;
  font-weight: 800;
  line-height: 1.2;
}

.mentor-company {
  font-size: 9px;
  opacity: 0.9;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cup-shadow {
  width: 60px;
  height: 8px;
  background: rgba(0,0,0,0.1);
  border-radius: 50%;
  margin-top: 5px;
  filter: blur(2px);
}
</style>