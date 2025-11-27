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
    router.push({ name: 'home' });
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
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

.form-group input::placeholder {
  color: #9ca3af;
}

.error {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 14px;
  text-align: center;
}

.submit-button {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  font-weight: 600;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s, transform 0.1s;
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