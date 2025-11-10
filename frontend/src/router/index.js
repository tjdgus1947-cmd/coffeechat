import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth'; // 1. auth 스토어 가져오기
import HomeView from '@/views/HomeView.vue';
import NetworkView from '@/views/NetworkView.vue';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login', // 2. 로그인 페이지 추가
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true } // (선택) 로그인한 사용자는 못 가게 막기
  },
  {
    // /register 또는 /register/:role(mentee|mentor) 에서 처리
    path: '/register/:role?', // 선택적 role 파라미터 허용
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true } // (선택) 로그인한 사용자는 못 가게 막기
  },
  {
    path: '/network', // 4. 기존 네트워크 페이지
    name: 'network',
    component: NetworkView,
    meta: { requiresAuth: true } // 5. 이 페이지는 '인증이 필요함'
  },
 
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true } // 인증 필요
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresAuth: true } // 인증 필요
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// -----------------------------------------------------------------
// 6. ⭐️ 네비게이션 가드 (가장 중요한 부분) ⭐️
// -----------------------------------------------------------------
router.beforeEach((to, from, next) => {
  // 라우터가 이동하기 '전에' 이 함수가 매번 실행됩니다.
  
  // auth.js 스토어에서 로그인 상태(isAuthenticated)를 가져옵니다.
  // (3-4 단계에서 스토어가 로컬 스토리지를 읽도록 수정할 예정)
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  // 가려는 페이지(to)가 '인증이 필요한(requiresAuth)' 페이지인지 확인
  if (to.meta.requiresAuth) {
    if (isAuthenticated) {
      // 1. 인증이 필요한데, 로그인 함 -> 통과
      next();
    } else {
      // 2. 인증이 필요한데, 로그인 안 함 -> 로그인 페이지로 강제 이동
      console.log('인증 필요! 로그인 페이지로 이동합니다.');
      next({ name: 'login' }); // /login 경로로 리다이렉트
    }
  } 
  // (선택 사항) 로그인한 사용자가 /login, /register 페이지 접근 시
  else if (to.meta.requiresGuest && isAuthenticated) {
    // 3. 로그인한 사람이 login 페이지 또 가려고 함 -> 네트워크 뷰로 보내기
    next({ name: 'network' });
  } 
  else {
    // 4. 그 외 (/, /login, /register 등) -> 항상 통과
    next();
  }
});

export default router;