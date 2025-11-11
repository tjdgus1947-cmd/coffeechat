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
      <input type="number" v-model="form.experienceYears" min="0">
    </div>
    <div class="form-group">
      <label>전문 분야 (쉼표로 구분)</label>
      <input type="text" v-model="form.topics" placeholder="예: 법무, 변호사, 계약">
    </div>
    <div class="form-group">
      <label>자기 소개 (멘티에게 보여집니다)</label>
      <textarea v-model="form.introduction" rows="4" placeholder="경력, 전문성, 멘티에게 도움 줄 수 있는 내용을 작성해주세요."></textarea>
    </div>
    <div class="form-group">
      <label>증빙 서류 (재직/재학증명서, 4대보험 등)</label>
      <FileUploader @file-changed="handleFileUpdate" />
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
import FileUploader from '@/components/common/FileUploader.vue';

const authStore = useAuthStore();
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
    // FormData를 사용해 파일과 텍스트를 함께 전송
    const formData = new FormData();
    Object.keys(form.value).forEach(key => {
      if (form.value[key] !== null) {
        formData.append(key, form.value[key]);
      }
    });

    await authStore.registerMentor(formData);
    
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