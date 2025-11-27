// src/store/auth.js

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api'; 
import router from '@/router'; 

const MOCK_LOGIN = false; 

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

  async function registerMentee(menteeData) {
    try {
      await api.post('/auth/register/mentee', menteeData);
    } catch (error) {
      console.error('멘티 회원가입 실패:', error);
      throw error; 
    }
  }

  async function registerMentor(mentorData) {
    try {
      await api.post('/auth/register/mentor', mentorData);
    } catch (error) {
      console.error('멘토 회원가입 실패:', error);
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
    updateApiHeaders(); 
  }
  
  function updateApiHeaders() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }
  
  // --- 앱 초기화 ---
  updateApiHeaders();
  
  if (MOCK_LOGIN && !token.value) {
    console.warn('!!! MOCK LOGIN 활성 상태 !!!');
    const mockUser = {
      id: 'mentee-kim-fake-id', 
      user_metadata: {
        full_name: '김멘티 (테스트)',
        role: 'mentee',
      }
    };
    const mockToken = 'fake-jwt-token-for-development';

    localStorage.setItem('user', JSON.stringify(mockUser));
    localStorage.setItem('token', mockToken);
    
    user.value = mockUser;
    token.value = mockToken;
    
    updateApiHeaders();
  }
  return { 
    user, 
    token, 
    userId, 
    userName, // 👈 (추가)
    isAuthenticated, 
    userRole, 
    login, 
    logout, 
    registerMentee,
    registerMentor 
  };
});