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
 * wbs_detail.md[cite: wbs_detail.md]의 API 엔드포인트들을 호출하는 함수들
 */

// 1. (10단계 테스트) 회원가입 API 호출
export const signUpUser = (email, password, role, fullName) => {
  return apiClient.post('/api/auth/register', {
    email,
    password,
    role,
    full_name: fullName,
  });
};

// 2. (14단계) 멘토 목록 조회 API 호출
export const getMentors = () => {
  return apiClient.get('/api/mentors/');
};

// 3. (26단계 - 새로 추가) 18단계의 AI 추천 멘토 조회 API
export const getRecommendedMentors = (menteeId) => {
  // 8단계에서 만든 FastAPI 엔드포인트 호출 [cite: wbs_detail.md]
  return apiClient.get(`/api/mentors/recommended/${menteeId}`);
};

// 4. (26단계 - 새로 추가) 23단계의 위치 기반 검색 API
export const getNearbyMentors = (menteeId, radiusMeters) => {
  // 21단계에서 만든 FastAPI 엔드포인트 호출
  return apiClient.post('/api/location/nearby-mentors', {
    mentee_id: menteeId,
    radius_meters: radiusMeters
  });
};

export default apiClient;