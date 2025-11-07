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
      <label>자기 소개 (AI매칭에 사용됩니다)</label>
      <textarea v-model="form.introduction" rows="4" placeholder="자신의 관심사, 목표, 멘토에게 배우고 싶은 점을 자유롭게 작성해주세요."></textarea>
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
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
.form-group input, .form-group textarea { 
  width: 100%; 
  padding: 8px; 
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.form-group textarea {
  resize: vertical;
  font-family: inherit;
}
.error { color: red; font-size: 14px; margin-top: 10px; }
button { 
  width: 100%; 
  padding: 10px; 
  background-color: #6d28d9; 
  color: white; 
  border: none; 
  border-radius: 4px; 
  cursor: pointer;
  font-size: 16px;
  margin-top: 10px;
}
button:hover:not(:disabled) { background-color: #5b21b6; }
button:disabled { background-color: #ccc; cursor: not-allowed; }
</style>