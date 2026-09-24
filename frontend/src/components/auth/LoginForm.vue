<template>
  <form class="login-form" @submit.prevent="handleLogin" novalidate>
    <div class="form-group">
      <label for="login-email">이메일</label>
      <input
        id="login-email"
        type="email"
        v-model="email"
        placeholder="coffee@example.com"
        autocomplete="email"
        required
      >
    </div>

    <div class="form-group">
      <label for="login-password">비밀번호</label>
      <div class="password-field">
        <input
          id="login-password"
          :type="showPassword ? 'text' : 'password'"
          v-model="password"
          placeholder="비밀번호를 입력하세요"
          autocomplete="current-password"
          required
        >
        <button
          type="button"
          class="toggle-visibility"
          :aria-label="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
          @click="showPassword = !showPassword"
        >
          {{ showPassword ? '숨기기' : '보기' }}
        </button>
      </div>
    </div>

    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>

    <button type="submit" class="submit-btn" :disabled="isLoading">
      <span v-if="isLoading" class="spinner" aria-hidden="true"></span>
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
const showPassword = ref(false);
const isLoading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
  if (!email.value || !password.value) {
    errorMessage.value = '이메일과 비밀번호를 모두 입력해주세요.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';
  try {
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
.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.9rem;
  font-weight: 700;
  color: #4A352D;
}

.form-group input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  font-size: 1rem;
  color: #4A352D;
  background: #FFFDF8;
  border: 1.5px solid #D4C3A3;
  border-radius: 10px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.form-group input::placeholder { color: #B8A58A; }
.form-group input:focus {
  outline: none;
  border-color: #CC9966;
  box-shadow: 0 0 0 3px rgba(204, 153, 102, 0.2);
}

.password-field { position: relative; }
.password-field input { padding-right: 72px; }
.toggle-visibility {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  padding: 4px 10px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #CC9966;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.toggle-visibility:hover { background: #F8F7F3; }

.error {
  margin: -4px 0 0;
  padding: 10px 12px;
  font-size: 0.9rem;
  color: #B15408;
  background: #FFF4EA;
  border: 1px solid #F2D2B3;
  border-radius: 8px;
}

.submit-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  margin-top: 4px;
  padding: 13px 24px;
  font-family: 'Gowun Dodum', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: #FFFFFF;
  background: #CC9966;
  border: 2px solid #CC9966;
  border-radius: 10px;
  box-shadow: 2px 2px 0 #D4C3A3;
  cursor: pointer;
  transition: all 0.2s ease;
}
.submit-btn:hover:not(:disabled) {
  background: #DDAA66;
  border-color: #DDAA66;
  box-shadow: 1px 1px 0 #D4C3A3;
  transform: translate(1px, 1px);
}
.submit-btn:disabled {
  background: #D4C3A3;
  border-color: #D4C3A3;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  border-top-color: #FFFFFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
