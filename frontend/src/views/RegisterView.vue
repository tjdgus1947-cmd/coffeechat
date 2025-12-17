<template>
  <div class="register-page">
    <div class="register-container">
      <div v-if="!role">
        <!-- Brand Section -->
        <div class="brand-section">
          <div class="brand-icon">☕</div>
          <h1 class="brand-title">CoffeeChat AI</h1>
          <p class="brand-subtitle">Connect. Share. Grow.</p>
          <div class="vintage-divider"></div>
        </div>

        <h2 class="page-title">회원가입</h2>
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

        <div class="login-link">
          <span>이미 계정이 있으신가요?</span>
          <router-link to="/login" class="link-accent">로그인</router-link>
        </div>
      </div>

      <div v-else>
        <h2 class="page-title">회원가입 - {{ role === 'mentee' ? '멘티' : '멘토' }}</h2>
        <MenteeRegisterForm v-if="role === 'mentee'" />
        <MentorRegisterForm v-if="role === 'mentor'" />

        <div class="back-link">
          <router-link to="/register" class="link-accent">← 역할 다시 선택하기</router-link>
        </div>
      </div>
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
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

.register-page {
  font-family: 'Gowun Dodum', sans-serif;
  background-color: #F8F7F3;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.register-container {
  background: #FFFFFF;
  max-width: 700px;
  width: 100%;
  padding: 48px;
  border-radius: 16px;
  border: 2px solid #D4C3A3;
  box-shadow: 4px 4px 0 #D4C3A3;
  transform: translateY(-60px);
}

.brand-section {
  text-align: center;
  margin-bottom: 32px;
}

.brand-icon {
  font-size: 2.5rem;
  margin-bottom: 12px;
}

.brand-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #4A352D;
  margin-bottom: 8px;
}

.brand-subtitle {
  font-size: 0.9rem;
  color: #4A352D;
  margin-bottom: 12px;
  font-weight: 400;
}

.vintage-divider {
  width: 60px;
  height: 2px;
  background-color: #D4C3A3;
  opacity: 0.8;
  margin: 0 auto;
}

.page-title {
  text-align: center;
  font-size: 1.75rem;
  font-weight: 700;
  color: #4A352D;
  margin-bottom: 12px;
}

.subtitle {
  text-align: center;
  font-size: 1rem;
  color: #4A352D;
  margin-bottom: 32px;
}

/* --- 역할 선택 화면 --- */
.choice-container {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  justify-content: center;
  gap: 24px;
  margin: 32px 0;
}

.choice-card {
  appearance: none;
  font-family: 'Gowun Dodum', sans-serif;
  
  flex: 1;
  min-width: 200px;
  padding: 32px 24px;
  
  font-size: 1rem;
  border-radius: 12px;
  border: 2px solid #D4C3A3;
  background: #F8F7F3;
  cursor: pointer;
  
  text-align: center;
  
  transition: all 0.2s ease;
  box-shadow: 2px 2px 0 #D4C3A3;
}

.choice-card:hover {
  background: #FFFFFF;
  border-color: #CC9966;
  transform: translateY(-2px);
  box-shadow: 3px 3px 0 #D4C3A3;
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 16px;
}

.choice-card h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #4A352D;
  margin-bottom: 12px;
}

.choice-card p {
  font-size: 0.95rem;
  color: #4A352D;
  line-height: 1.5;
  min-height: 40px;
}

/* 하단 링크 */
.login-link {
  text-align: center;
  margin-top: 24px;
  font-size: 1rem;
  color: #4A352D;
}

.login-link span {
  margin-right: 8px;
}

.link-accent {
  color: #CC9966;
  text-decoration: none;
  font-weight: 700;
  transition: color 0.2s;
}

.link-accent:hover {
  color: #DDAA66;
  text-decoration: underline;
}

.back-link {
  text-align: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .register-container {
    padding: 32px 24px;
  }
  
  .choice-container {
    flex-direction: column;
  }
  
  .brand-title {
    font-size: 1.25rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}
</style>