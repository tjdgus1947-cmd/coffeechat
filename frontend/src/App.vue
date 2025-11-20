<template>
  <div id="app-container">
    <TheNavbar />

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// 2. TheNavbar 컴포넌트를 임포트합니다.
import TheNavbar from '@/components/layout/TheNavbar.vue';
</script>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #ffffff; /* 배경색 흰색으로 변경 (선택사항) */
}

main {
  flex-grow: 1;
  padding: 0; /* ⭐️ 범인 검거! 20px -> 0으로 변경 */
  width: 100%;
  max-width: 100%;
}
</style>