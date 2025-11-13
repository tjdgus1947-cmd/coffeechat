<template>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>이메일</label>
      <input type="email" v-model="form.email" required>
    </div>
    <div class="form-group">
      <label>비밀번호</label>
      <input type="password" v-model="form.password" required>
    </div>
    <div class="form-group">
      <label>이름</label>
      <input type="text" v-model="form.name" required>
    </div>
    <div class="form-group">
      <label>현재 상황 (학교, 학년, 직무 등)</label>
      <input type="text" v-model="form.situation" placeholder="예: OO대학교 경영학과 4학년">
    </div>
    <div class="form-group">
      <label>관심 분야 (쉼표로 구분)</label>
      <input type="text" v-model="form.topics" placeholder="예: CPA, 재무, 회계">
    </div>
    <div class="form-group">
      <label>자기 소개 (AI 매칭에 활용됩니다)</label>
      <textarea v-model="form.introduction" rows="4" placeholder="관심사, 경력 목표, 멘토에게 배우고 싶은 점 등을 자유롭게 작성해주세요."></textarea>
    </div>

    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? '가입 중...' : '멘티로 가입하기' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const form = ref({
  email: '',
  password: '',
  name: '',
  situation: '',
  topics: '',
  introduction: '',
});
const isLoading = ref(false);
const errorMessage = ref('');

const handleSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = '';

  try {
    await authStore.registerMentee(form.value);
    
    alert('회원가입이 완료되었습니다. 로그인을 진행해주세요.');
    router.push({ name: 'login' });

  } catch (error) {
    console.error('멘티 가입 실패:', error);
    errorMessage.value = '가입에 실패했습니다: ' + (error.response?.data?.detail || error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* LoginForm.vue와 스타일 공유 (CSS 모듈화로 개선 가능) */
.form-group { margin-bottom: 15px; }
.form-group label { 
  display: block; 
  margin-bottom: 5px;
  font-weight: 500;
  color: #374151;
}
.form-group input, .form-group textarea { 
  width: 100%; 
  padding: 10px 12px;
  box-sizing: border-box;
  border: 1.5px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  font-family: inherit;
}
.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}
.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #9ca3af;
}
.form-group textarea {
  resize: vertical;
  min-height: 110px;
}
.error { 
  color: #ef4444; 
  font-size: 14px;
  margin-bottom: 10px;
}
button { 
  width: 100%; 
  padding: 12px; 
  background-color: #6d28d9; 
  color: white; 
  border: none; 
  border-radius: 6px; 
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: background-color 0.2s;
}
button:hover:not(:disabled) {
  background-color: #5b21b6;
}
button:disabled { 
  background-color: #d1d5db;
  cursor: not-allowed;
}
</style>