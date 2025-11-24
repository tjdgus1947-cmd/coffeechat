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
          
          <div class="mentee-details">
            <p v-if="request.mentee?.current_situation" class="detail-item">
              <span class="icon">📚</span>
              <span class="label">현재 상황:</span>
              <span class="value">{{ request.mentee.current_situation }}</span>
            </p>
            <p v-if="request.mentee?.career_goal" class="detail-item">
              <span class="icon">🎯</span>
              <span class="label">진로 목표:</span>
              <span class="value">{{ request.mentee.career_goal }}</span>
            </p>
          </div>

          <div v-if="request.concern" class="concern-box">
            <p class="concern-label">💬 고민 내용</p>
            <p class="concern-text">{{ request.concern }}</p>
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

// 🔥 수정됨: 수락 버튼 핸들러
const handleApprove = async (requestId) => {
  if (!confirm('이 시간에 커피챗을 진행하시겠습니까?\n(수락 시 채팅방이 자동 생성됩니다)')) return;

  try {
    // 1. 예약 상태를 '승인'으로 변경
    await mentorStore.updateBookingStatus(requestId, 'approved');

    // 2. 채팅방 생성 API 호출
    // (백엔드 주소나 포트가 다르다면 수정해주세요)
    

    alert('✅ 수락되었습니다! [채팅] 탭에서 대화를 시작해보세요.');
    
    // (선택사항) 여기서 페이지 새로고침을 하거나 목록을 다시 불러올 수 있습니다.
    // await mentorStore.fetchReceivedBookings();

  } catch (error) {
    console.error('수락 처리 중 오류 발생:', error);
    alert('수락 처리에 실패했습니다. 잠시 후 다시 시도해주세요.');
  }
};

const handleReject = async (requestId) => {
  if (!confirm('정말 거절하시겠습니까?')) return;
  try {
    await mentorStore.updateBookingStatus(requestId, 'rejected');
  } catch (error) {
    console.error('거절 처리 실패:', error);
    alert('처리 중 오류가 발생했습니다.');
  }
};

const formatDate = (isoString) => {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('ko-KR');
};

const formatSchedule = (start, end) => {
  if (!start || !end) return '시간 정보 없음';
  const startDate = new Date(start);
  const endDate = new Date(end);
  
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
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 20px; border: 1px solid #eee; border-radius: 12px; margin-bottom: 15px;
  background-color: #fafafa; transition: all 0.2s;
}
.request-card:hover {
    border-color: #6d28d9; background-color: #fff;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.mentee-info { flex-grow: 1; }
.name-row { font-size: 1.15rem; margin-bottom: 10px; color: #333; }

/* 🔥 멘티 상세 정보 스타일 */
.mentee-details {
  background-color: #f0f9ff;
  border-left: 3px solid #3b82f6;
  padding: 12px;
  margin: 10px 0;
  border-radius: 8px;
}

.detail-item {
  margin: 6px 0;
  font-size: 14px;
  color: #1e40af;
  display: flex;
  align-items: flex-start;
  gap: 6px;
}

.detail-item .icon {
  font-size: 16px;
}

.detail-item .label {
  font-weight: 600;
  min-width: 80px;
}

.detail-item .value {
  flex: 1;
  color: #374151;
}

/* 🔥 고민 내용 스타일 */
.concern-box {
  background-color: #fef3c7;
  border-left: 3px solid #f59e0b;
  padding: 12px;
  margin: 10px 0;
  border-radius: 8px;
}

.concern-label {
  font-size: 13px;
  font-weight: 700;
  color: #b45309;
  margin: 0 0 6px 0;
}

.concern-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.time-info p { margin: 5px 0; font-size: 1.05rem; color: #444; }
.time-info strong { color: #6d28d9; }
.applied-at { font-size: 0.85rem; color: #888; }

.actions {
  display: flex; flex-direction: column;
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