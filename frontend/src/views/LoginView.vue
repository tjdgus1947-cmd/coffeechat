<template>
  <div class="auth-container">
    <h2>로그인</h2>
    <LoginForm />
    <p>
      계정이 없으신가요? 
      <router-link to="/register">회원가입</router-link>
    </p>
  </div>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue';
</script>

<style scoped>
.auth-container {
  max-width: 500px;
  margin: 60px auto;
  padding: 0;
  border: none;
  border-radius: 16px;
  box-shadow: none;
  background: transparent;
}
</style>