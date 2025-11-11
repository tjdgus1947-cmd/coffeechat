import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api'; 
// ⭐️ 1. 여기서 router 임포트를 "삭제"합니다. (순환 고리 끊기)
// import router from '@/router'; 
import { supabase } from '@/supabaseClient'; 

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const user = ref(null);
  const token = ref(null);

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userId = computed(() => user.value?.id);
  const userRole = computed(() => user.value?.user_metadata?.role);
  const userName = computed(() => user.value?.user_metadata?.full_name);

  // --- Actions ---   
  async function login(credentials) {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: credentials.email,
        password: credentials.password,
      });
      if (error) throw error;
      if (!data.session || !data.user) {
        throw new Error('Supabase 로그인에 성공했으나 세션 정보를 받지 못했습니다.');
      }
      user.value = data.user;
      token.value = data.session.access_token;
      updateApiHeaders(data.session.access_token);
    } catch (error) {
      console.error('로그인 실패:', error);
      logoutCleanup();
      throw error; 
    }
  }

  // (회원가입 함수는 백엔드 API를 쓰는 것이 맞으므로 그대로 둡니다)
  async function registerMentee(formData) { /* ... (기존 코드와 동일) ... */ }
  async function registerMentor(mentorData) { /* ... (기존 코드와 동일) ... */ }

  async function logout() {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('로그아웃 실패:', error);
    } finally {
      logoutCleanup();
      
      // ⭐️ 2. router를 "이 함수 내부에서" 동적으로 import 합니다.
      try {
        const router = (await import('@/router')).default;
        router.push({ name: 'login' });
      } catch (e) {
        console.error("라우터 이동 실패:", e);
        // 라우터를 못찾아도 앱이 죽지 않도록 합니다.
      }
    }
  }

  // --- 내부 헬퍼 함수 ---
  function logoutCleanup() {
    user.value = null;
    token.value = null;
    localStorage.removeItem('user'); 
    localStorage.removeItem('token'); 
    updateApiHeaders(null);
  }
  
  function updateApiHeaders(sessionToken) {
    if (sessionToken) {
      api.defaults.headers.common['Authorization'] = `Bearer ${sessionToken}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }

  // ⭐️ 3. 앱 초기화 로직 (main.js가 호출할 함수)
  async function initializeAuth() {
    const { data } = await supabase.auth.getSession();

    if (data.session) {
      user.value = data.session.user;
      token.value = data.session.access_token;
      updateApiHeaders(data.session.access_token);
    } else {
      logoutCleanup();
    }

    supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        user.value = session.user;
        token.value = session.access_token;
        updateApiHeaders(session.access_token);
      } else {
        user.value = null;
        token.value = null;
        updateApiHeaders(null);
      }
    });
  }
  
  return { 
    user, token, userId, userName,
    isAuthenticated, userRole, 
    login, logout, 
    registerMentee, registerMentor,
    initializeAuth // ⭐️ main.js가 이 함수를 쓸 수 있도록 노출
  };
});