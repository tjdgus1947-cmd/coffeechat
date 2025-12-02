<!-- 앱의 모든 페이지 상단에 공통으로 표시될 메뉴바 -->

<template>
  <nav class="navbar">
    <div class="logo">
      <router-link to="/">
        <img :src="logoUrl" alt="CoffeeChat 로고" class="logo-image">
      </router-link>
    </div>

    <div class="nav-actions">
      <template v-if="authStore.isAuthenticated">
        <router-link to="/network" class="nav-link">대시보드</router-link>
        <router-link to="/mypage" class="nav-link">마이페이지</router-link>
        <button @click="handleLogout" class="nav-link logout-link">
          로그아웃
        </button>
      </template>
      <template v-else>
        <router-link to="/login" class="nav-link">로그인</router-link>
        <router-link to="/register" class="cta-button">회원가입</router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import logoUrl from '@/assets/images/logo.png';


const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  // MOCK_LOGIN 모드에서는 localStorage를 지워야 하므로,
  // auth.js의 logout 함수를 호출하는 것이 가장 안전합니다.
  authStore.logout();
  
  // (wbs_detail.md) MOCK_LOGIN=false일 때도 
  // authStore.logout()이 알아서 /login으로 보내줍니다.
};
</script>



<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 40px;
  height: 70px;
  
  /* 배경: 아주 연한 크림색 or 흰색 */
  background-color: #FFFFFF; 
  /* 테두리: 포인트 컬러를 얇게 사용하여 세련되게 */
  border-bottom: 3px solid var(--point-color); 
  box-shadow: 0 4px 15px rgba(54, 18, 5, 0.05);
}

.logo a {
  text-decoration: none;
  display: flex; 
  align-items: center;
}

.logo-image {
  height: 50px;
  width: auto;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.nav-link {
  display: inline-block;
  padding: 8px 16px;
  text-decoration: none;
  color: var(--text-sub); /* 연한 갈색 */
  font-weight: 500;
  border-radius: 20px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: var(--bg-cream);
  color: var(--primary-color);
}

.nav-link.router-link-exact-active {
  background-color: var(--bg-cream);
  color: var(--point-color); /* 활성화된 메뉴는 포인트 컬러(카라멜) */
  font-weight: 700;
}

.logout-link {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-size: inherit;
}

/* 회원가입 버튼: 포인트 컬러(카라멜) 사용 */
.cta-button {
  display: inline-block;
  padding: 10px 24px;
  text-decoration: none;
  color: #ffffff;
  background-color: var(--point-color); /* ✨ 포인트 컬러 적용 */
  border-radius: 24px;
  font-weight: 600;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(223, 135, 35, 0.3);
}

.cta-button:hover {
  background-color: var(--point-hover);
  transform: translateY(-2px);
}
</style>