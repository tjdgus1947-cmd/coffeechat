import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import api from '@/services/api'; // ⭐️ Axios(api.js) 사용

// 1. ⭐️ (최종) 가짜 데이터 스위치를 끕니다.
const MOCK_DATA = false;

export const useMentorStore = defineStore('mentor', () => {
  // --- State ---
  const receivedBookings = ref([]); 
  const isLoading = ref(false);

  // --- Actions ---

  /**
   * (가상 API) /api/bookings/received
   * 현재 멘토가 '받은' 커피챗 신청 목록을 API에서 가져옵니다.
   */



  
// [수정] src/store/mentorStore.js

async function fetchReceivedBookings() {
    const authStore = useAuthStore();
    if (!authStore.userId) return;

    isLoading.value = true;
    
    // 1. MOCK_DATA = false 이므로 이 코드는 건너뜁니다.
    if (MOCK_DATA) {
      // ... (생략)
    } else {
      // 2. ⭐️ 'else' 블록 (실제 API 호출)이 실행됩니다.
      try {
        console.log('실제 멘토용 예약 목록을 API에서 가져옵니다...');
        
        // 3. ⭐️ (⭐️ 중요 ⭐️)
        //    백엔드(bookings.py)에 정의된 주소는 '/bookings/received/me' 입니다.
        const response = await api.get('/bookings/received/me'); // 👈 '/me' 추가
        
        receivedBookings.value = response.data;
        console.log('멘토 예약 목록 로드 성공:', response.data);

      } catch (error) {
        // 4. (에러 확인) RLS 정책이 없으면 여기서 500 에러가 뜰 겁니다.
        console.error('멘토 예약 목록 로딩 실패:', error);
        receivedBookings.value = [];
      } finally {
        isLoading.value = false;
      }
    }
  }


async function updateBookingStatus(bookingId, newStatus) {
    isLoading.value = true;
    try {
      // 백엔드에 PUT 요청 전송 ('approved' or 'rejected')
      await api.put(`/bookings/${bookingId}/status`, {
        status: newStatus
      });
      
      // 성공 시 목록 새로고침 (가장 확실한 방법)
      await fetchReceivedBookings();
      alert(newStatus === 'approved' ? '승인되었습니다.' : '거절되었습니다.');

    } catch (error) {
      console.error('상태 변경 실패:', error);
      alert('처리 중 오류가 발생했습니다.');
    } finally {
      isLoading.value = false;
    }
  }



return {
    receivedBookings,
    isLoading,
    fetchReceivedBookings,
    updateBookingStatus
  };
});
// ... (store의 나머지 부분)smm
