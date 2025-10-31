<template>
  <div class="auth-container">
    <div v-if="!role">
      <h2>회원가입</h2>
      <p class="subtitle">어떤 역할로 가입하시겠어요?</p>
      <div class="choice-container">
        <button class="choice-card" @click="goRegister('mentee')">
          <div class="card-icon">👩‍🎓</div>
          <h3>멘티 가입</h3>
          <p>성장을 도와줄 멘토를 찾아보세요.</p>
        </button>

        <button class="choice-card" @click="goRegister('mentor')">
          <div class="card-icon">👨‍🏫</div>
          <h3>멘토 가입</h3>
          <p>당신의 지식과 경험을 나눠주세요.</p>
        </button>
      </div>

      <p class="login-link">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </p>
    </div>

    <div v-else>
      <h2>회원가입 - {{ role === 'mentee' ? '멘티' : '멘토' }}</h2>
      <MenteeRegisterForm v-if="role === 'mentee'" />
      <MentorRegisterForm v-if="role === 'mentor'" />

      <p class="back-link">
        <router-link to="/register">역할 다시 선택하기</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MenteeRegisterForm from '@/components/auth/MenteeRegisterForm.vue';
import MentorRegisterForm from '@/components/auth/MentorRegisterForm.vue';

const route = useRoute();
const router = useRouter();

// route.params.role 이 없으면 선택 화면을 표시
const role = computed(() => {
  const r = route.params.role;
  if (!r) return null;
  return r === 'mentor' ? 'mentor' : 'mentee';
});

function goRegister(selected) {
  // selected: 'mentee' | 'mentor'
  router.push({ path: `/register/${selected}` });
}
</script>
<style scoped>
/* 전체 컨테이너 스타일 */
.auth-container {
  max-width: 700px;
  margin: 40px auto;
  padding: 40px; /* 내부 여백 증가 */
  border: 1px solid #e0e0e0; /* 테두리 색상 연하게 */
  border-radius: 12px; /* 모서리 더 둥글게 */
  background-color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); /* 은은한 그림자 */
}

.auth-container h2 {
  text-align: center;
  font-size: 2rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.subtitle {
  text-align: center;
  font-size: 1rem;
  color: #666;
  margin-bottom: 30px;
}

/* --- 역할 선택 화면 --- */
.choice-container {
  display: flex;
  flex-direction: row; /* 가로로 배치 */
  align-items: stretch; /* 카드 높이 동일하게 */
  justify-content: center;
  gap: 30px; /* 카드 사이 간격 */
  margin: 30px 0;
}

.choice-card {
  /* <button> 태그 기본 스타일 리셋 */
  appearance: none;
  font-family: inherit; /* 폰트 상속 */
  
  flex: 1; /* 양쪽 카드가 공간을 1:1로 나눠 가짐 */
  min-width: 200px;
  padding: 30px 20px;
  
  font-size: 1rem;
  border-radius: 12px;
  border: 1px solid #ddd;
  background: #fafafa;
  cursor: pointer;
  
  text-align: center;
  
  transition: all 0.3s ease; /* 부드러운 전환 효과 */
}

.choice-card:hover {
  background: #ffffff;
  border-color: #007bff; /* 테마 색상 (예: 파란색) */
  transform: translateY(-5px); /* 살짝 위로 이동 */
  box-shadow: 0 6px 16px rgba(0, 123, 255, 0.1); /* 강조된 그림자 */
}

.card-icon {
  font-size: 3.5rem; /* 아이콘(이모지) 크기 */
  margin-bottom: 15px;
}

.choice-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.choice-card p {
  font-size: 0.9rem;
  color: #666;
  line-height: 1.5;
  min-height: 40px; /* 설명글 높이를 비슷하게 맞춰줌 */
}

/* 하단 '로그인' 링크 */
.login-link {
  text-align: center;
  margin-top: 20px;
  font-size: 0.9rem;
  color: #555;
}

.login-link a,
.back-link a {
  color: #007bff;
  text-decoration: none;
  font-weight: 500;
}

.login-link a:hover,
.back-link a:hover {
  text-decoration: underline;
}

/* --- 가입 폼 화면 --- */
.back-link {
  text-align: center;
  margin-top: 20px;
}
</style>