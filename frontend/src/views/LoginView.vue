<template>
  <div class="login-page">
    <div class="auth-container">
      <h2>로그인</h2>
      <LoginForm />
      <p class="register-link">
        계정이 없으신가요? 
        <router-link to="/register">회원가입</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue';
</script>

<style scoped>
.login-page {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f9fafb;
  padding: 20px;
}

.auth-container {
  max-width: 500px;
  width: 100%;
  padding: 48px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.auth-container h2 {
  margin-top: 0;
  margin-bottom: 28px;
  font-size: 28px;
  font-weight: 700;
  text-align: center;
  color: #111827;
}

.register-link {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.register-link a {
  color: #6d28d9;
  text-decoration: none;
  font-weight: 500;
}

.register-link a:hover {
  color: #5b21b6;
  text-decoration: underline;
}
</style>