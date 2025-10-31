import axios from 'axios';
// .env 파일에 VITE_API_URL=http://localhost:8000 (백엔드 주소)를 설정합니다.
// wbs_detail.md에 /api로 시작하니 baseURL에 /api를 추가합니다.
const api = axios.create({
  baseURL: (import.meta.env.VITE_API_URL || 'http://localhost:8000') + '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// (1단계에서는 쓰지 않지만) 로그인 구현 시 토큰을 자동으로 헤더에 추가하는 코드
// api.interceptors.request.use((config) => {
//   const token = localStorage.getItem('token'); // 예시
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

export default api;