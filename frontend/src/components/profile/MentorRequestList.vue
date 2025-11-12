<template>
  <div class="request-list-container">
    <div v-if="mentorStore.isLoading" class="loading">
      <p>받은 신청 목록을 불러오는 중...</p>
    </div>

    <ul v-else-if="mentorStore.receivedBookings.length > 0" class="request-list">
      <li v-for="request in mentorStore.receivedBookings" :key="request.id" class="request-card">
        
        <div class="mentee-info">
          <div class="name-row">
            <strong>{{ request.mentee?.full_name || '알 수 없음' }}</strong> 멘티님의 신청
          </div>
          
          <div class="time-info">
             <p>
               📅 희망 일정: 
               <strong>{{ formatSchedule(request.start_time, request.end_time) }}</strong>
             </p>
             <span class="applied-at">
               (신청일: {{ formatDate(request.created_at) }})
             </span>
          </div>
        </div>
        
        <div class="actions">
          <template v-if="request.status === 'pending'">
            <button class="btn approve" @click="handleApprove(request.id)">수락</button>
            <button class="btn reject" @click="handleReject(request.id)">거절</button>
          </template>
          <span v-else-if="request.status === 'approved'" class="status approved">수락됨</span>
          <span v-else-if="request.status === 'rejected'" class="status rejected">거절됨</span>
        </div>

      </li>
    </ul>

    <div v-else class="no-requests">
      <p>아직 받은 커피챗 신청이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useMentorStore } from '@/store/mentorStore'; 

const mentorStore = useMentorStore();

onMounted(() => {
  mentorStore.fetchReceivedBookings();
});

const handleApprove = async (requestId) => {
  if (!confirm('이 시간에 커피챗을 진행하시겠습니까?')) return;
  await mentorStore.updateBookingStatus(requestId, 'approved');
};

const handleReject = async (requestId) => {
  if (!confirm('정말 거절하시겠습니까?')) return;
  await mentorStore.updateBookingStatus(requestId, 'rejected');
};

// --- ⭐️ 날짜/시간 포맷팅 헬퍼 함수 ---
const formatDate = (isoString) => {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('ko-KR');
};

const formatSchedule = (start, end) => {
  if (!start || !end) return '시간 정보 없음';
  const startDate = new Date(start);
  const endDate = new Date(end);
  
  // 예: 2023. 10. 25. (수) 14:00 ~ 15:00
  const datePart = startDate.toLocaleDateString('ko-KR', { 
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' 
  });
  const startTimePart = startDate.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  const endTimePart = endDate.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  
  return `${datePart} ${startTimePart} ~ ${endTimePart}`;
};
</script>

<style scoped>
.request-list {
  list-style: none; padding: 0; margin-top: 15px;
}
.request-card {
  display: flex; justify-content: space-between; align-items: flex-start; /* 상단 정렬 */
  padding: 20px; border: 1px solid #eee; border-radius: 12px; margin-bottom: 15px;
  background-color: #fafafa; transition: all 0.2s;
}
.request-card:hover {
    border-color: #6d28d9; background-color: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.mentee-info { flex-grow: 1; }
.name-row { font-size: 1.15rem; margin-bottom: 10px; color: #333; }
.time-info p { margin: 5px 0; font-size: 1.05rem; color: #444; }
.time-info strong { color: #6d28d9; }
.applied-at { font-size: 0.85rem; color: #888; }

.actions {
  display: flex; flex-direction: column; /* 버튼 세로 배치 */
  gap: 8px; min-width: 80px;
}
.btn {
  padding: 8px 14px; border: none; border-radius: 8px;
  cursor: pointer; font-weight: 600; font-size: 0.9rem; transition: opacity 0.2s;
}
.btn:hover { opacity: 0.9; }
.btn.approve { background-color: #6d28d9; color: white; }
.btn.reject { background-color: #f1f5f9; color: #64748b; }

.status {
  text-align: center; padding: 6px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 600;
}
.status.approved { background-color: #dcfce7; color: #15803d; }
.status.rejected { background-color: #fef2f2; color: #dc2626; }

.no-requests, .loading {
  padding: 40px; text-align: center; color: #999; font-size: 1.1rem;
}
</style>