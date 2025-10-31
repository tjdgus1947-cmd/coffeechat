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
      <label>증빙 서류 (재직/재학증명서, 4대보험 등)</label>
      <FileUploader @file-changed="handleFileUpdate" />
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
import FileUploader from '@/components/common/FileUploader.vue';

const authStore = useAuthStore();
const router = useRouter();

const form = ref({
  email: '',
  password: '',
  name: '',
  situation: '',
  topics: '',
  proofFile: null,
});
const isLoading = ref(false);
const errorMessage = ref('');

const handleFileUpdate = (file) => {
  form.value.proofFile = file;
};

const handleSubmit = async () => {
  if (!form.value.proofFile) {
    errorMessage.value = '증빙 서류를 업로드해주세요.';
    return;
  }
  
  isLoading.value = true;
  errorMessage.value = '';

  try {
    // 3-4 단계: auth.js 스토어에 실제 API를 호출하는
    // registerMentee 액션을 구현할 예정입니다.
    
    // FormData를 사용해 파일과 텍스트를 함께 전송
    const formData = new FormData();
    Object.keys(form.value).forEach(key => {
      formData.append(key, form.value[key]);
    });

    await authStore.registerMentee(formData);
    
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
.form-group label { display: block; margin-bottom: 5px; }
.form-group input { width: 100%; padding: 8px; box-sizing: border-box; }
.error { color: red; font-size: 14px; }
button { width: 100%; padding: 10px; background-color: #6d28d9; color: white; border: none; border-radius: 4px; cursor: pointer; }
button:disabled { background-color: #ccc; }
</style>