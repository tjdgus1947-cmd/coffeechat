<template>
  <div class="login-page">
    <div class="login-container">
      <!-- Logo/Brand Section -->
      <div class="brand-section">
        <div class="brand-icon">☕</div>
        <h1 class="brand-title">CoffeeChat AI</h1>
        <p class="brand-subtitle">Connect. Share. Grow.</p>
        <div class="vintage-divider"></div>
      </div>

      <!-- Login Form Section -->
      <div class="form-section">
        <h2 class="form-title">로그인</h2>
        <LoginForm />
        <div class="signup-link">
          <span>계정이 없으신가요?</span>
          <router-link to="/register" class="link-accent">회원가입</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue';
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

.login-page {
  font-family: 'Gowun Dodum', sans-serif;
  background-color: #F8F7F3;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  transform: translateY(-40px);
}

.login-container {
  background: #FFFFFF;
  max-width: 480px;
  width: 100%;
  padding: 48px;
  border-radius: 16px;
  border: 2px solid #D4C3A3;
  box-shadow: 4px 4px 0 #D4C3A3;
  transform: translateY(-40px);
}

.brand-section {
  text-align: center;
  margin-bottom: 40px;
}

.brand-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.brand-title {
  font-size: 1.875rem;
  font-weight: 800;
  color: #4A352D;
  margin-bottom: 8px;
}

.brand-subtitle {
  font-size: 1rem;
  color: #4A352D;
  margin-bottom: 16px;
  font-weight: 400;
}

.vintage-divider {
  width: 80px;
  height: 2px;
  background-color: #D4C3A3;
  opacity: 0.8;
  margin: 0 auto;
}

.form-section {
  margin-top: 32px;
}

.form-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4A352D;
  text-align: center;
  margin-bottom: 32px;
}

.signup-link {
  text-align: center;
  margin-top: 24px;
  font-size: 1rem;
  color: #4A352D;
}

.signup-link span {
  margin-right: 8px;
}

.link-accent {
  color: #CC9966;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.2s;
}

.link-accent:hover {
  color: #DDAA66;
  text-decoration: underline;
}

@media (max-width: 600px) {
  .login-container {
    padding: 32px 24px;
  }
  
  .brand-title {
    font-size: 1.5rem;
  }
  
  .form-title {
    font-size: 1.25rem;
  }
}
</style>