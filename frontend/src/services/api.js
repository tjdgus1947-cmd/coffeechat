import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (email, password) => api.post('/api/auth/login', { email, password }),
  register: (email, password, name, user_type) => 
    api.post('/api/auth/register', { email, password, name, user_type }),
  getCurrentUser: () => api.get('/api/auth/me'),
};

export const mentorsAPI = {
  getAll: (params) => api.get('/api/mentors/', { params }),
  getOne: (id) => api.get(`/api/mentors/${id}`),
  getRecommended: (menteeId, limit = 10) => 
    api.get(`/api/mentors/recommended/${menteeId}`, { params: { limit } }),
};

export const menteesAPI = {
  getOne: (id) => api.get(`/api/mentees/${id}`),
  getHistory: (id) => api.get(`/api/mentees/${id}/history`),
};

export const matchingAPI = {
  calculateScore: (menteeId, mentorId) => 
    api.get('/api/matching/calculate', { params: { mentee_id: menteeId, mentor_id: mentorId } }),
  submitFeedback: (menteeId, mentorId, rating, comment) =>
    api.post('/api/matching/feedback', { mentee_id: menteeId, mentor_id: mentorId, rating, comment }),
};

export const networkAPI = {
  getData: (menteeId) => api.get(`/api/network/${menteeId}`),
  getStats: (menteeId) => api.get(`/api/network/${menteeId}/stats`),
};

export default api;