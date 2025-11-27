<template>
  <form @submit.prevent="handleLogin" class="login-form">
    <div class="form-group">
      <label for="email">이메일</label>
      <input 
        type="email" 
        id="email"
        v-model="email" 
        placeholder="example@email.com"
        required
      >
    </div>
    <div class="form-group">
      <label for="password">비밀번호</label>
      <input 
        type="password" 
        id="password"
        v-model="password" 
        placeholder="비밀번호를 입력하세요"
        required
      >
    </div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <button type="submit" :disabled="isLoading" class="submit-button">
      {{ isLoading ? '로그인 중...' : '로그인' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');
const isLoading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    await authStore.login({ email: email.value, password: password.value });
    router.push({ name: 'network' });
  } catch (error) {
    console.error('로그인 실패:', error);
    errorMessage.value = '이메일 또는 비밀번호를 확인해주세요.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 480px;
  margin: 0 auto;
  padding: 48px 40px 40px 40px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.form-group {
  margin-bottom: 32px;
}

.form-group label {
  display: block;
  margin-bottom: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #22223b;
}

.form-group input {
  width: 100%;
  padding: 18px 20px;
  font-size: 18px;
  border: 1.5px solid #d1d5db;
  border-radius: 10px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 4px rgba(109, 40, 217, 0.10);
}

.form-group input::placeholder {
  color: #b0b3c6;
  font-size: 16px;
}

.error {
  margin-bottom: 24px;
  padding: 14px;
  background-color: #fef2f2;
  border: 1.5px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 16px;
  text-align: center;
}

.submit-button {
  width: 100%;
  padding: 18px 0;
  font-size: 20px;
  font-weight: 700;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
  margin-top: 8px;
}

.submit-button:hover:not(:disabled) {
  background-color: #5b21b6;
}

.submit-button:active:not(:disabled) {
  transform: scale(0.98);
}

.submit-button:disabled {
  background-color: #d1d5db;
  cursor: not-allowed;
}
</style>