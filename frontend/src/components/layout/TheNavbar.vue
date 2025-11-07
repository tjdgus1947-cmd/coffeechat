<!-- 앱의 모든 페이지 상단에 공통으로 표시될 메뉴바 -->

<template>
  <header class="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50 shadow-sm">
    <div class="container mx-auto px-4 py-4">
      <div class="flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="flex items-center">
          <img :src="logoUrl" alt="CoffeeChat 로고" class="h-16 w-auto">
        </router-link>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center gap-8">
          <a href="#" class="text-gray-600 hover:text-gray-900 transition">멘토 찾기</a>
          <a href="#" class="text-gray-600 hover:text-gray-900 transition">후기</a>
          <router-link v-if="authStore.isAuthenticated" to="/network" class="text-gray-600 hover:text-gray-900 transition">
            네트워크
          </router-link>
        </nav>

        <!-- Desktop Auth Buttons -->
        <div class="hidden md:flex items-center gap-4">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/mypage" class="text-gray-600 hover:text-gray-900 transition font-medium">
              마이페이지
            </router-link>
            <button 
              @click="handleLogout" 
              class="px-4 py-2 text-gray-600 hover:text-gray-900 transition font-medium"
            >
              로그아웃
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="px-4 py-2 text-gray-600 hover:text-gray-900 transition font-medium">
              로그인
            </router-link>
            <router-link 
              to="/register" 
              class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-all"
            >
              시작하기
            </router-link>
          </template>
        </div>

        <!-- Mobile Menu Button -->
        <button 
          @click="toggleMobileMenu" 
          class="md:hidden p-2 text-gray-600 hover:text-gray-900"
        >
          <svg v-if="!mobileMenuOpen" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
          <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Mobile Menu -->
      <div v-if="mobileMenuOpen" class="md:hidden mt-4 pb-4 flex flex-col gap-4 border-t pt-4">
        <a href="#" class="text-gray-600 hover:text-gray-900 transition">멘토 찾기</a>
        <a href="#" class="text-gray-600 hover:text-gray-900 transition">후기</a>
        <router-link v-if="authStore.isAuthenticated" to="/network" class="text-gray-600 hover:text-gray-900 transition">
          네트워크
        </router-link>
        
        <div class="flex flex-col gap-2 pt-2">
          <template v-if="authStore.isAuthenticated">
            <router-link to="/mypage" class="w-full px-4 py-2 text-center text-gray-600 hover:bg-gray-100 rounded-lg transition">
              마이페이지
            </router-link>
            <button 
              @click="handleLogout" 
              class="w-full px-4 py-2 text-center text-gray-600 hover:bg-gray-100 rounded-lg transition"
            >
              로그아웃
            </button>
          </template>
          <template v-else>
            <router-link to="/login" class="w-full px-4 py-2 text-center text-gray-600 hover:bg-gray-100 rounded-lg transition">
              로그인
            </router-link>
            <router-link to="/register" class="w-full px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-center rounded-lg font-medium transition-all">
              시작하기
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import logoUrl from '@/assets/images/logo-purple.png';

const mobileMenuOpen = ref(false);

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value;
};

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
  padding: 15px 40px; /* 상하좌우 여백 조정 */
  height: 60px;
  background-color: #ffffff;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}
.logo a {
 text-decoration: none;
 display: flex; 
 align-items: center;
}

/* 6. ⭐️ (추가) 로고 이미지 크기 조절 (Canvas 버전) */
.logo-image {
  height: 50px; /* 로고 높이 (Navbar 높이(60px)보다 작게) */
  width: auto; /* 가로 비율 자동 */
}


/* --- 주요 변경 사항 --- */

/* 링크와 버튼을 묶는 오른쪽 정렬 컨테이너 */
.nav-actions {
  display: flex;
  align-items: center;
  gap: 10px; /* 요소 사이의 간격 */
}

/* '네트워크', '마이페이지', '로그인' 등 일반 링크 스타일 */
.nav-link {
  display: inline-block;
  padding: 8px 16px; /* 클릭 영역 확보 및 알약 모양을 위한 패딩 */
  margin: 0 5px;
  text-decoration: none;
  color: #333;
  font-weight: 500;
  border-radius: 6px; /* 둥근 모서리 */
  transition: background-color 0.3s ease, color 0.3s ease;
}

/* 일반 링크 hover 효과 */
.nav-link:hover {
  background-color: #f3f4f6; /* 은은한 회색 배경 */
  color: #000;
}

/* 활성화된 라우터 링크 (알약 모양) */
.nav-link.router-link-exact-active {
  background-color: #f3eefc; /* 매우 연한 보라색 */
  color: #6d28d9;
  font-weight: 600;
}

/* 로그아웃 버튼을 nav-link처럼 보이도록 리셋 */
.logout-link {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit; /* 폰트 상속 */
  font-size: inherit; /* 폰트 크기 상속 */
}

/* '회원가입' CTA 버튼 스타일 */
.cta-button {
  display: inline-block;
  padding: 10px 18px; /* 링크보다 살짝 더 크게 */
  margin-left: 10px;
  text-decoration: none;
  color: #ffffff;
  background-color: #6d28d9; /* 메인 컬러 */
  border: none;
  border-radius: 6px;
  font-weight: 500;
  transition: background-color 0.3s ease;
}

.cta-button:hover {
  background-color: #5b21b6; /* 호버 시 살짝 더 어두운 보라색 */
}
</style>