import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth'; // 1. auth 스토어 가져오기
import HomeView from '@/views/HomeView.vue';
import NetworkView from '@/views/NetworkView.vue';
import LoginView from '@/views/LoginView.vue';
import RegisterView from '@/views/RegisterView.vue';
import MentorMap from '@/components/map/MentorMap.vue'; // ⭐️ 올바른 경로!
import MentorListPanel from '@/components/list/MentorListPanel.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register/:role?',
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/network',
    name: 'network',
    component: NetworkView,
    meta: { requiresAuth: true }
  },
  {
    path: '/map',
    name: 'MentorMap', 
    component: MentorMap, // ⭐️ 이제 정상 작동!
    meta: { requiresAuth: true }
  },
  {
    path: '/mypage',
    name: 'mypage',
    component: () => import('@/views/MyPageView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/mentors/list',
    name: 'MentorList',
    component: MentorListPanel,
    meta: { requiresAuth: true }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 네비게이션 가드
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const isAuthenticated = authStore.isAuthenticated;

  if (to.meta.requiresAuth) {
    if (isAuthenticated) {
      next();
    } else {
      console.log('인증 필요! 로그인 페이지로 이동합니다.');
      next({ name: 'login' });
    }
  } 
  else if (to.meta.requiresGuest && isAuthenticated) {
    next({ name: 'network' });
  } 
  else {
    next();
  }
});

export default router;