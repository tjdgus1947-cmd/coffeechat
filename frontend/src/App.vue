<template>
  <div id="app-container">
    <TheNavbar />

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import TheNavbar from '@/components/layout/TheNavbar.vue';

// 🔥 추가: chatStore, authStore 가져오기
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/auth';

// 스토어 인스턴스 생성
const chatStore = useChatStore();
const authStore = useAuthStore();

// 앱 처음 로딩될 때 unread-count 불러오기
onMounted(async () => {
  // 로그인 정보가 불러질 때까지 기다림
  // (initializeAuth는 main.js에서 호출되고 있음)
  await authStore.initializeAuth?.();

  // 로그인 되어 있으면 unread-count 요청
  if (authStore.isAuthenticated) {
    await chatStore.fetchUnreadCount();
  }

  // 🔁 30초마다 갱신 (선택 기능)
  setInterval(() => {
    if (authStore.isAuthenticated) {
      chatStore.fetchUnreadCount();
    }
  }, 30000);
});
</script>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #ffffff;
}

main {
  flex-grow: 1;
  padding: 0;
  width: 100%;
  max-width: 100%;
}
</style>
