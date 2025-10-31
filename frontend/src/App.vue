

<template>
  <div id="app-container">
    <TheNavbar />

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
// 이 파일은 앱의 '껍데기' 역할만 하므로 
// <script setup> 태그는 비어있어도 괜찮습니다.
// (또는 <script> 태그를 아예 삭제해도 됩니다.)


// 2. TheNavbar 컴포넌트를 임포트합니다.
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