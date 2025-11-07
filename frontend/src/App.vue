

<template>
  <div id="app-container">
    <TheNavbar />

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import TheNavbar from '@/components/layout/TheNavbar.vue';
</script>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f8f9fa; /* 앱 전체 배경색 (선택) */
}

main {
  flex-grow: 1;
  padding: 20px;
}
</style>