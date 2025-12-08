<!-- 앱의 모든 페이지 상단에 공통으로 표시될 메뉴바 -->
<!-- Navbar.vue (예시 이름) -->
<template>
  <nav class="navbar">
    <!-- 로고 영역 -->
    <div class="logo no-shadow">
      <router-link to="/">
        <img :src="logoUrl" alt="CoffeeChat 로고" class="logo-image" />
      </router-link>
    </div>

    <!-- 오른쪽 메뉴 영역 -->
    <div class="nav-actions">
      <!-- 로그인 한 상태 -->
      <template v-if="authStore.isAuthenticated">
        <router-link to="/network" class="nav-link">
          대시보드
        </router-link>
        <router-link to="/mypage" class="nav-link">
          마이페이지
        </router-link>
        <button @click="handleLogout" class="nav-link">
          로그아웃
        </button>
      </template>

      <!-- 로그인 안 한 상태 -->
      <template v-else>
        <router-link to="/login" class="nav-link">
          로그인
        </router-link>
        <router-link to="/register" class="cta-button">
          회원가입
        </router-link>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import logoUrl from '@/assets/images/logo.png'; // 갈색으로 교체했으면 이 파일만 갈색으로 두면 됨

const authStore = useAuthStore();
const router = useRouter();

const handleLogout = () => {
  authStore.logout();
  // logout 안에서 /login 으로 이동 처리하고 있으면 여기서 별도 router.push 필요 없음
};
</script>

<style scoped>
/* ====== 전체 네비바 레이아웃 ====== */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;

  padding: 10px 40px;
  height: 70px;

  background-color: #ffffff;
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
  gap: 12px;
}

/* ====== 공통 pill 버튼 스타일 (로그인 / 회원가입 / 대시보드 / 마이페이지 / 로그아웃) ====== */
.nav-link,
.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;

  padding: 10px 24px;
  min-width: 90px;

  border-radius: 999px;
  border: none; /* 선 없음!!! */

  background-color: #ffffff;
  color: #4a3a2a; /* 진갈색 */

  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  box-sizing: border-box;

  /* ===== 오른쪽 버튼 스타일 핵심 ===== */
  box-shadow: 0 0 14px rgba(223, 135, 35, 0.15); /* 부드러운 크림 그림자 */

  transition: all 0.15s ease;
}

/* hover 시 */
.nav-link:hover,
.cta-button:hover {
  background-color: #fffdfa; /* 아주 연한 크림 */
  box-shadow: 0 0 20px rgba(223, 135, 35, 0.25);
}

/* ===== 활성화된 메뉴 (현재 페이지) ===== */
.router-link-exact-active {
  color: #000000 !important;
  font-weight: 700;
  box-shadow: 0 0 20px #e7a67eb4 !important;
}

/* logout 버튼도 동일한 pill 스타일 */
button.nav-link {
  border: none;
  background-color: #ffffff;
  box-shadow: 0 0 14px rgba(223, 135, 35, 0.15);
}

.logo,
.logo * {
  box-shadow: none !important;
  filter: none !important;
  background: none !important;
  border: none !important;
}

</style>
