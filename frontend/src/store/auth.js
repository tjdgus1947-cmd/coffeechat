// src/store/auth.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api'; 
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

  // ⭐️ [수정됨] 실제 API 호출 로직 추가 (FormData 전송)
  async function registerMentee(formData) {
    try {
      const response = await api.post('/auth/register/mentee', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('멘티 가입 성공:', response.data);
      return response.data;
    } catch (error) {
      console.error('멘티 가입 요청 실패:', error);
      throw error; 
    }
  }

  // ⭐️ [수정됨] 멘토 가입 (JSON -> FormData로 변경)
  async function registerMentor(formData) {
    try {
      // 백엔드(auth.py)의 sign_up_mentor가 이제 Form(...)과 File(...)을 받습니다.
      // 따라서 FormData 객체를 보내야 하며, 헤더 설정이 필요합니다.
      const response = await api.post('/auth/register/mentor', formData, {
         headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('멘토 가입 성공:', response.data);
      return response.data;
    } catch (error) {
      console.error('멘토 가입 요청 실패:', error);
      throw error;
    }
  }

  async function logout() {
    try {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
    } catch (error) {
      console.error('로그아웃 실패:', error);
    } finally {
      logoutCleanup();
      
      try {
        const router = (await import('@/router')).default;
        router.push({ name: 'login' });
      } catch (e) {
        console.error("라우터 이동 실패:", e);
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
    initializeAuth
  };
});