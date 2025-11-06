<template>
  <div class="booking-list-container">
    <!-- 1. bookingStore의 isLoading state 확인 -->
    <div v-if="bookingStore.isLoading" class="loading">
      <p>신청 목록을 불러오는 중...</p>
    </div>

    <!-- 2. bookingStore의 bookings 배열 (실제 API 응답) 순회 -->
    <ul v-else-if="bookingStore.bookings.length > 0" class="booking-list">
      
      <!-- 
        3. ⭐️ (최종)
           bookings.py가 반환하는 'BookingSent' 모델에 맞게 수정
           (예: booking.id, booking.status, booking.mentor.full_name)
      -->
      <li v-for="booking in bookingStore.bookings" :key="booking.id" class="booking-card">
        <div class="mentor-info">
          <!-- 
            4. ⭐️ (최종)
            bookings.py의 select('... mentor:users(full_name)') 쿼리에 따라
            'booking.mentor.full_name'을 읽습니다.
          -->
          <strong>{{ booking.mentor.full_name || '이름 없음' }}</strong> 멘토님
          
          <!-- (참고) 멘토의 '회사'를 표시하려면,
               bookings.py의 select 쿼리를 수정해야 합니다.
               (예: '... mentor:users(full_name, mentor_profiles(company))')
          -->
        </div>
        
        <!-- 5. 'status' 컬럼 값을 기반으로 UI 변경 -->
        <div class="actions">
          <!-- 5a. 'pending' (대기중)일 때 -->
          <span v-if="booking.status === 'pending'" class="status pending">
            승인 대기중
          </span>
          <!-- 5b. 'approved' (수락됨)일 때 -->
          <span v-else-if="booking.status === 'approved'" class="status approved">
            수락됨
          </span>
          <!-- 5c. 'rejected' (거절됨)일 때 -->
          <span v-else-if="booking.status === 'rejected'" class="status rejected">
            거절됨
          </span>
        </div>
      </li>
    </ul>

    <!-- 6. API 응답이 빈 배열일 경우 -->
    <div v-else class="no-bookings">
      <p>아직 멘토에게 보낸 커피챗 신청이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useBookingStore } from '@/store/bookingstore'; // ⭐️ 멘티용 bookingstore 사용

const bookingStore = useBookingStore();

// 7. ⭐️ (최종) 컴포넌트가 로드될 때 '진짜' API를 호출
onMounted(() => {
  bookingStore.fetchBookings();
});
</script>

<style scoped>
/* MentorRequestList.vue와 유사한 스타일 적용 */
.booking-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}
.booking-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}
.booking-card:last-child {
  border-bottom: none;
}
.mentor-info strong {
  font-size: 1.1rem;
  color: #333;
}
.no-bookings {
  padding: 20px;
  text-align: center;
  color: #777;
}
.actions {
  display: flex;
  gap: 10px;
}
.status {
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
}
/* ⭐️ 상태별 색상 ⭐️ */
.status.pending {
  background-color: #fefce8; /*
Light Yellow */
  color: #a16207; /*
Dark Yellow */
}
.status.approved {
  background-color: #f0fdf4; /*
Light Green */
  color: #16a34a; /*
Green */
}
.status.rejected {
  background-color: #fef2f2; /*
Light Red */
  color: #dc2626; /*
Red */
}
</style>