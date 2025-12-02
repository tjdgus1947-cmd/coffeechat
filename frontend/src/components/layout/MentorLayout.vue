<template>
  <div class="mentor-layout-container">
    <div class="view-switcher">
      <button 
        @click="goDashboard" 
        :class="{ active: isDashboard }"
      >
        📊 대시보드
      </button>
      <button
        @click="goNetwork"
        :class="{ active: isNetwork }"
      >
        🌐 네트워크
      </button>
      <button 
        @click="goChat" 
        :class="{ active: isChat }"
      >
        💬 채팅
      </button>
    </div>
    <router-view />
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
const route = useRoute();
const router = useRouter();

const isDashboard = computed(() => route.name === 'mentor-dashboard');
const isNetwork = computed(() => route.name === 'mentor-network');
const isChat = computed(() => route.name === 'mentor-chat');

function goDashboard() {
  router.push({ name: 'mentor-dashboard' });
}
function goNetwork() {
  router.push({ name: 'mentor-network' });
}
function goChat() {
  router.push({ name: 'mentor-chat' });
}
</script>

<style scoped>
.mentor-layout-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f9fafb;
}
.view-switcher {
  display: flex;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 40px;
  flex-shrink: 0;
}
.view-switcher button {
  margin-right: 16px;
  padding: 10px 24px;
  border: none;
  background: none;
  font-size: 1.1rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: border 0.2s, color 0.2s;
}
.view-switcher button.active {
  color: #6d28d9;
  border-bottom: 2px solid #6d28d9;
  font-weight: bold;
}
</style>
