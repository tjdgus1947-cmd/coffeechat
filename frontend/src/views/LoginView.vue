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
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
}
</style>