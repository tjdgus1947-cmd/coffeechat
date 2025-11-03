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
      <label>소속 (회사)</label>
      <input type="text" v-model="form.company" placeholder="예: 삼성전자">
    </div>
    <div class="form-group">
      <label>직무 (부서)</label>
      <input type="text" v-model="form.team" placeholder="예: 법무팀">
    </div>
    <div class="form-group">
      <label>총 경력 (년)</label>
      <input type="number" v-model="form.experienceYears">
    </div>
    <div class="form-group">
      <label>전문 분야 (쉼표로 구분)</label>
      <input type="text" v-model="form.topics" placeholder="예: 법무, 변호사, 계약">
    </div>
    <div class="form-group">
      <label>자기 소개 (멘티에게 보여집니다)</label>
      <textarea v-model="form.introduction" rows="3"></textarea>
    </div>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    <button type="submit" :disabled="isLoading">
      {{ isLoading ? '가입 중...' : '멘토로 가입하기' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
// import api from '@/services/api'; // (wbs_detail.md) /api/auth/register

const authStore = useAuthStore(); // (wbs_detail.md) 스토어에 멘토 등록 액션 추가 필요
const router = useRouter();

const form = ref({
  email: '',
  password: '',
  name: '',
  company: '',
  team: '',
  experienceYears: 0,
  topics: '',
  introduction: '',
});
const isLoading = ref(false);
const errorMessage = ref('');

const handleSubmit = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  try {
    // (수정) 님의 백엔드 API를 실제로 호출합니다.
    // 님의 auth.js 스토어가 이 'form.value' (JSON)를
    // /api/auth/register/mentor로 보내도록 이미 수정되었습니다.
    await authStore.registerMentor(form.value);  
    
    // (수정) API가 성공한 후에 알림창을 띄웁니다.
    alert('멘토 가입 신청이 완료되었습니다. 관리자 승인 후 활동 가능합니다.');
    router.push({ name: 'login' });

  } catch (error) {
    console.error('멘토 가입 실패:', error);
    errorMessage.value = '가입에 실패했습니다: ' + (error.response?.data?.detail || error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* LoginForm.vue와 스타일 공유 */
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; }
.form-group input, .form-group textarea { width: 100%; padding: 8px; box-sizing: border-box; }
.error { color: red; font-size: 14px; }
button { width: 100%; padding: 10px; background-color: #6d28d9; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #ccc; }
</style>