<template>
  <div class="request-list-container">
    <!-- 1. mentorStore의 isLoading state를 확인 -->
    <div v-if="mentorStore.isLoading" class="loading">
      <p>받은 신청 목록을 불러오는 중...</p>
    </div>

    <!-- 2. mentorStore의 receivedBookings 배열 (실제 API 응답)을 순회 -->
    <ul v-else-if="mentorStore.receivedBookings.length > 0" class="request-list">
      
      <!-- 
        3. ⭐️ (최종)
           bookings.py가 반환하는 '실제' 데이터 객체에 맞게 수정
           (예: request.id, request.status, request.mentee.full_name)
      -->
      <li v-for="request in mentorStore.receivedBookings" :key="request.id" class="request-card">
        <div class="mentee-info">
          <!-- 
            4. ⭐️ (최종)
            bookings.py의 select('... mentee:users(full_name)') 쿼리에 따라
            'request.mentee.full_name'을 읽습니다.
          -->
          <strong>{{ request.mentee.full_name || '이름 없음' }}</strong>
          
          <!-- 
            (참고) 멘티의 '상황'을 표시하려면,
            bookings.py의 select 쿼리를 수정해야 합니다.
            (예: '... mentee:users(full_name, mentee_profiles(current_situation))')
          -->
          <!-- <p>{{ request.mentee?.mentee_profiles?.current_situation || '정보 없음' }}</p> -->
        </div>
        
        <!-- 5. 'status' 컬럼 값을 기반으로 UI 변경 -->
        <div class="actions">
          <!-- 5a. 'pending' (대기중)일 때만 버튼 표시 -->
          <template v-if="request.status === 'pending'">
            <button class="btn approve" @click="handleApprove(request.id)">수락</button>
            <button class="btn reject" @click="handleReject(request.id)">거절</button>
          </template>
          <!-- 5b. 'approved' (수락됨)일 때 -->
          <span v-else-if="request.status === 'approved'" class="status approved">
            수락됨
          </span>
          <!-- 5c. 'rejected' (거절됨)일 때 -->
          <span v-else-if="request.status === 'rejected'" class="status rejected">
            거절됨
          </span>
        </div>
      </li>
    </ul>

    <!-- 6. API 응답이 빈 배열일 경우 -->
    <div v-else class="no-requests">
      <p>아직 멘티에게 받은 커피챗 신청이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useMentorStore } from '@/store/mentorStore'; 

const mentorStore = useMentorStore();

// 7. ⭐️ (최종) 컴포넌트가 로드될 때 '진짜' API를 호출
onMounted(() => {
  mentorStore.fetchReceivedBookings();
});

// 8. ⭐️ (가짜) 수락/거절 버튼 핸들러 (아직 API 연동 안 됨)
const handleApprove = (requestId) => {
  // (wbs_detail.md) (추후 구현: await api.post(`/bookings/approve/${requestId}`))
  console.log('(가짜) 수락:', requestId);
  alert('수락 API 연동 필요');
};

const handleReject = (requestId) => {
  // (wbs_detail.md) (추후 구현: await api.post(`/bookings/reject/${requestId}`))
  console.log('(가짜) 거절:', requestId);
  alert('거절 API 연동 필요');
};
</script>

<style scoped>
.request-list {
  list-style: none;
  padding: 0;
  margin-top: 10px;
}
.request-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #eee;
}
.request-card:last-child {
  border-bottom: none;
}
.mentee-info strong {
  font-size: 1.1rem;
}
.mentee-info p {
  font-size: 0.9rem;
  color: #555;
  margin: 5px 0 0;
}
.no-requests {
  padding: 20px;
  text-align: center;
  color: #777;
}
.actions {
  display: flex;
  gap: 10px;
}
.btn {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}
.btn.approve {
  background-color: #6d28d9;
  color: white;
}
.btn.reject {
  background-color: #f3f4f6;
  color: #dc2626;
}
.status {
  font-weight: bold;
  padding: 5px 10px;
  border-radius: 12px;
  font-size: 0.9rem;
}
.status.approved {
  background-color: #f0fdf4;
  color: #16a34a;
}
.status.rejected {
  background-color: #fef2f2;
  color: #dc2626;
}
</style>