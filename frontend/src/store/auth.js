import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/services/api'; 
import router from '@/router'; 

const MOCK_LOGIN = false; 

export const useAuthStore = defineStore('auth', () => {
  // --- State ---
  const user = ref(JSON.parse(localStorage.getItem('user')) || null);
  const token = ref(localStorage.getItem('token') || null);

  // --- Getters ---
  const isAuthenticated = computed(() => !!token.value && !!user.value);
  const userId = computed(() => user.value?.id);
  // (수정) 'user.role'이 아니라 'user.user_metadata.role'을 보도록 변경
  const userRole = computed(() => user.value?.user_metadata?.role);
  // (신규) 'user_metadata'에서 이름을 가져오는 getter 추가
  const userName = computed(() => user.value?.user_metadata?.full_name);

  // --- Actions ---  
  async function login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials); 
      
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

  async function registerMentee(formData) {
    try {
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

  async function registerMentor(mentorData) {
    try {
      await api.post('/auth/register/mentor', mentorData);
    } catch (error) {
       console.error('멘토 회원가입 실패:', error);
       throw error;
    }
  }

  function logout() {
    logoutCleanup();
    router.push({ name: 'login' });
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