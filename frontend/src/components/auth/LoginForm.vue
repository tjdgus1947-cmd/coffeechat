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
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; }
.form-group input { width: 100%; padding: 8px; box-sizing: border-box; }
.error { color: red; font-size: 14px; }
button { width: 100%; padding: 10px; background-color: #6d28d9; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #ccc; }
</style>