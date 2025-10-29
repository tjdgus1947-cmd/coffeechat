// frontend/src/services/api.js

import axios from 'axios';

// 1단계에서 .env에 저장한 백엔드 API 주소 (http://localhost:8000)
const API_URL = import.meta.env.VITE_API_URL;

// Axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/*
 * wbs_detail.md의 API 엔드포인트들을 호출하는 함수들
 */

// 1. (10단계 테스트) 회원가입 API 호출
// (role: 'mentee' 또는 'mentor')
export const signUpUser = (email, password, role, fullName) => {
  return apiClient.post('/api/auth/register', {
    email,
    password,
    role,
    full_name: fullName,
  });
};

// 2. (8단계 구현) 멘토 목록 조회 API 호출
export const getMentors = () => {
  return apiClient.get('/api/mentors/');
};

// 3. (8단계 구현) AI 추천 멘토 조회 API 호출
export const getRecommendedMentors = (menteeId) => {
  return apiClient.get(`/api/mentors/recommended/${menteeId}`);
};

// (나중에 로그인 API도 여기에 추가)
// export const loginUser = (email, password) => { ... }

export default apiClient;