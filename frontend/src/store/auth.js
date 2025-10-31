// frontend/src/store/auth.js
// (API 주소 3곳 수정 완료)

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api'; 
import router from '@/router'; 

// 1. ⭐️ 백엔드 연동 시 이 값을 false로 바꾸면 됩니다 ⭐️
const MOCK_LOGIN = false; 

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userId = computed(() => user.value?.id);
  const userRole = computed(() => user.value?.role);

  // --- Actions ---  

  /**
   * (wbs_detail.md) /api/auth/login
   * 로그인 API를 호출하고, 성공 시 토큰과 사용자 정보를 저장합니다.
   */
  async function login(credentials) {
    try {
      // 🚨 (수정) /api/auth/login
      const response = await api.post('/auth/login', credentials); 
      
      // 🚨 (수정) 님의 Supabase 백엔드 응답 형식에 맞게 수정
      // 님의 auth.py[cite: backend/app/api/auth.py]는 response.user와 response.session을 반환합니다.
      const access_token = response.data.session?.access_token;
      const user_data = response.data.user;
      
      if (!access_token || !user_data) {
        throw new Error('서버 응답 형식이 올바르지 않습니다.');
      }

      user.value = user_data;
      token.value = access_token;

      localStorage.setItem('user', JSON.stringify(user_data));
      localStorage.setItem('token', access_token);

      updateApiHeaders();

    } catch (error) {
      console.error('로그인 실패:', error);
      logoutCleanup();
      throw error; 
    }
  }

  /**
   * (wbs_detail.md) /api/auth/register (멘티)
   * 멘티 회원가입 API를 호출합니다.
   */
  async function registerMentee(formData) {
    try {
      // 🚨 (수정) /api/auth/register/mentee
      await api.post('/auth/register/mentee', formData, { 
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } catch (error) {
      console.error('멘티 회원가입 실패:', error);
      throw error; 
    }
  }

  /**
   * (wbs_detail.md) /api/auth/register (멘토)
   * 멘토 회원가입 API를 호출합니다.
   */
  // 🚨 (수정) 멘토 폼은 FormData가 아닌 JSON(mentorData)을 받습니다.
  async function registerMentor(mentorData) {
    try {
      // 🚨 (수정) /api/auth/register/mentor
      await api.post('/auth/register/mentor', mentorData);
    } catch (error) {
       console.error('멘토 회원가입 실패:', error);
       throw error;
    }
  }

  /**
   * 로그아웃: 상태와 로컬 스토리지를 비웁니다.
   */
  function logout() {
    logoutCleanup();
    // 로그인 페이지로 이동
    router.push({ name: 'login' });
  }

  // --- 내부 헬퍼 함수 ---
  
  /**
   * 로그아웃 시 상태/스토리지 정리
   */
  function logoutCleanup() {
    user.value = null;
    token.value = null;
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    updateApiHeaders(); // API 헤더에서 토큰 제거
  }
  
  /**
   * api.js 인스턴스의 기본 헤더를 업데이트합니다.
   */
  function updateApiHeaders() {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
    } else {
      delete api.defaults.headers.common['Authorization'];
    }
  }
  
  // --- 앱 초기화 ---
  updateApiHeaders();

  
  // 2. ⭐️ MOCK_LOGIN이 true일 때 가짜 로그인 실행 ⭐️
  if (MOCK_LOGIN && !token.value) {
    console.warn('!!! MOCK LOGIN 활성 상태 !!!');
    
    // 1단계에서 썼던 '김멘티' 가짜 정보를 localStorage에 강제 주입
    const mockUser = {
      id: 'mentee-kim-fake-id', // (wbs_detail.md) 백엔드 ID 형식에 맞게
      name: '김멘티 (테스트)',
      role: 'mentee',
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
    isAuthenticated, 
    userRole, 
    login, 
    logout, 
    registerMentee,
    registerMentor 
  };
});