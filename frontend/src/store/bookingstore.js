import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import api from '@/services/api'; 

const MOCK_DATA = true;

export const useBookingStore = defineStore('booking', () => {
  // --- State ---
  const bookings = ref([]); 
  const isLoading = ref(false);

  // --- Actions ---
  async function fetchBookings() {
    const authStore = useAuthStore();
    if (!authStore.userId) return;

    isLoading.value = true;
    
    if (MOCK_DATA) {
      console.warn('!!! MOCK DATA (Bookings) 활성 상태 !!!');
      setMockBookings(); 
      isLoading.value = false;
    } else {
      try {
        console.log('실제 예약 목록을 API에서 가져옵니다...');
        const response = await api.get('/bookings/me'); 
        bookings.value = response.data;
      } catch (error) {
        console.error('예약 목록 로딩 실패:', error);
        bookings.value = [];
      } finally {
        isLoading.value = false;
      }
    }
  }

  function setMockBookings() {
    bookings.value = [
      {
        id: 'book-123',
        mentor_name: '한법무',
        mentor_company: '삼성전자',
        status: 'pending', 
      },
      {
        id: 'book-124',
        mentor_name: '이회계',
        mentor_company: '삼일회계법인',
        status: 'approved',
      },
      {
        id: 'book-125',
        mentor_name: '박재무',
        mentor_company: '삼성증권',
        status: 'rejected',
      },
    ];
  }
  
  function clearBookings() {
    bookings.value = [];
  }

  return {
    bookings,
    isLoading,
    fetchBookings,
    clearBookings
  };
});