<template>
  <div class="network-page-root">
    
    <MentorNetworkView v-if="isMentorView" />

    <MenteeNetworkView v-else />

  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useAuthStore } from '@/store/auth';

// 위에서 만든 두 컴포넌트 임포트
import MenteeNetworkView from '@/views/MenteeNetworkView.vue';
import MentorNetworkView from '@/views/MentorNetworkView.vue';

const authStore = useAuthStore();

// 멘토 여부 확인
const isMentorView = computed(() => authStore.userRole === 'mentor');
</script>

<style scoped>
/* ✅ 화면 전체 높이를 확보하는 필수 스타일 */
.network-page-root {
  width: 100%;
  height: 100%; /* 부모(App.vue > main)의 높이를 꽉 채움 */
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 이중 스크롤 방지 */
}
</style>