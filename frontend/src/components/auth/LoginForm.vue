<template>
  <form @submit.prevent="handleLogin">
    <div class="form-group">
      <label for="email">이메일</label>
      <input type="email" v-model="email" required>
    </div>
    <div class="form-group">
      <label for="password">비밀번호</label>
      <input type="password" v-model="password" required>
    </div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <button type="submit" :disabled="isLoading">
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
    // 3-4 단계: auth.js 스토어에 실제 API를 호출하는
    // login 액션을 구현할 예정입니다.
    await authStore.login({ email: email.value, password: password.value });
    
    // 로그인이 성공하면 네트워크 뷰로 이동
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
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

form {
  font-family: 'Gowun Dodum', sans-serif;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #4A352D;
  font-size: 1rem;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  box-sizing: border-box;
  border: 2px solid #D4C3A3;
  border-radius: 8px;
  font-size: 1rem;
  font-family: 'Gowun Dodum', sans-serif;
  background-color: #FFFFFF;
  color: #4A352D;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #CC9966;
  box-shadow: 0 0 0 3px rgba(204, 153, 102, 0.1);
}

.form-group input::placeholder {
  color: #A89F94;
}

.error {
  color: #D64545;
  font-size: 0.875rem;
  margin-top: 16px;
  padding: 12px;
  background-color: #FFE5E5;
  border-radius: 8px;
  border-left: 4px solid #D64545;
}

button {
  width: 100%;
  padding: 14px 24px;
  background-color: #CC9966;
  color: white;
  border: 2px solid #CC9966;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1.125rem;
  font-weight: 700;
  font-family: 'Gowun Dodum', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  transition: all 0.2s ease;
  box-shadow: 2px 2px 0 #D4C3A3;
  margin-top: 8px;
}

button:hover:not(:disabled) {
  background-color: #DDAA66;
  transform: translate(0, 0);
  box-shadow: 1px 1px 0 #D4C3A3;
}

button:disabled {
  background-color: #D4C3A3;
  border-color: #D4C3A3;
  cursor: not-allowed;
  opacity: 0.6;
}
</style>