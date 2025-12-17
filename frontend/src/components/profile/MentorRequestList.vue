<template>
  <div class="request-list-container">
    
    <div v-if="mentorStore.isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>주문서를 확인하고 있습니다...</p>
    </div>

    <ul v-else-if="mentorStore.receivedBookings.length > 0" class="request-list">
      <li v-for="request in mentorStore.receivedBookings" :key="request.id" class="ticket-card">
        
        <div class="ticket-hole"></div>

        <div class="ticket-content">
          <div class="ticket-header">
            <span class="order-num">ORDER #{{ request.id.slice(0, 4) }}</span>
            <span class="request-date">{{ formatDate(request.created_at) }}</span>
          </div>

          <div class="mentee-profile">
            <div class="mentee-avatar">{{ request.mentee?.full_name?.charAt(0) || 'U' }}</div>
            <div class="mentee-text">
              <strong>{{ request.mentee?.full_name || '익명 멘티' }}</strong>
              <span class="sub-text">{{ request.mentee?.current_situation || '정보 없음' }}</span>
            </div>
          </div>

          <div class="request-details">
            <div class="detail-row">
              <span class="icon">🎯</span> 
              <span class="value">{{ request.mentee?.career_goal || '-' }}</span>
            </div>
            <div class="detail-row highlight">
              <span class="icon">📅</span>
              <span class="value">{{ formatSchedule(request.start_time, request.end_time) }}</span>
            </div>
          </div>

          <div v-if="request.concern" class="concern-note">
            <p class="note-label">📝 멘티의 고민:</p>
            <p class="note-text">"{{ request.concern }}"</p>
          </div>
        </div>
        
        <div class="ticket-actions">
          <template v-if="request.status === 'pending'">
            <button class="action-btn approve" @click="handleApprove(request.id)" title="수락">
              ✅
            </button>
            <button class="action-btn reject" @click="handleReject(request.id)" title="거절">
              ❌
            </button>
          </template>

          <div v-else-if="request.status === 'approved'" class="stamp approved">
            <span>APPROVED</span>
          </div>
          <div v-else-if="request.status === 'rejected'" class="stamp rejected">
            <span>REJECTED</span>
          </div>
        </div>

        <div class="jagged-edge"></div>
      </li>
    </ul>

    <div v-else class="no-requests">
      <div class="empty-icon">📭</div>
      <p>아직 도착한 주문(신청)이 없습니다.</p>
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
  if (!confirm('이 시간에 커피챗을 진행하시겠습니까?\n(수락 시 채팅방이 생성됩니다)')) return;
  try {
    await mentorStore.updateBookingStatus(requestId, 'approved');
  } catch (error) {
    console.error('수락 실패:', error);
    alert('오류가 발생했습니다.');
  }
};

const handleReject = async (requestId) => {
  if (!confirm('정말 거절하시겠습니까?')) return;
  try {
    await mentorStore.updateBookingStatus(requestId, 'rejected');
  } catch (error) {
    console.error('거절 실패:', error);
  }
};

const formatDate = (isoString) => {
  if (!isoString) return '';
  return new Date(isoString).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
};

const formatSchedule = (start, end) => {
  if (!start || !end) return '시간 정보 없음';
  const startDate = new Date(start);
  const startTime = startDate.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  const endTime = new Date(end).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  return `${startDate.toLocaleDateString()} ${startTime} ~ ${endTime}`;
};
</script>

<style scoped>
.request-list-container {
  padding: 10px;
}

.request-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 🎟️ 티켓 카드 스타일 */
.ticket-card {
  background-color: #fff;
  background-image: radial-gradient(#f0f0f0 1px, transparent 1px);
  background-size: 10px 10px;
  border-radius: 2px; /* 종이 느낌을 위해 둥글지 않게 */
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: flex;
  position: relative;
  overflow: hidden;
  border-left: 5px solid #8d6e63; /* 왼쪽 포인트 컬러 */
}

/* 상단 구멍 (펀치) */
.ticket-hole {
  position: absolute;
  top: 15px;
  left: -8px;
  width: 16px;
  height: 16px;
  background-color: #f7f4e8; /* 배경색과 동일하게 */
  border-radius: 50%;
  box-shadow: inset -1px -1px 2px rgba(0,0,0,0.1);
  z-index: 2;
}

.ticket-content {
  flex: 1;
  padding: 20px 20px 30px; /* 하단 지그재그 여백 */
}

.ticket-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
  border-bottom: 1px dashed #ccc;
  padding-bottom: 5px;
  font-family: 'Courier New', monospace;
  color: #888;
  font-size: 0.85rem;
}

/* 멘티 프로필 */
.mentee-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.mentee-avatar {
  width: 40px; height: 40px;
  background-color: #a1887f;
  color: #fff;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
}

.mentee-text strong {
  display: block;
  font-size: 1.1rem;
  color: #3e2723;
}

.mentee-text .sub-text {
  font-size: 0.85rem;
  color: #6d4c41;
}

/* 상세 정보 */
.request-details {
  margin-bottom: 15px;
  font-size: 0.9rem;
  color: #555;
}

.detail-row {
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-row.highlight {
  color: #d84315; /* 날짜 강조 (오렌지/레드) */
  font-weight: 600;
}

/* 고민 메모 (포스트잇 느낌) */
.concern-note {
  background-color: #fff9c4; /* 노란색 포스트잇 */
  padding: 10px 15px;
  border-radius: 2px;
  box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
  font-size: 0.9rem;
  color: #4e342e;
  transform: rotate(-1deg);
}
.note-label { font-size: 0.75rem; color: #fbc02d; font-weight: bold; margin-bottom: 4px; }
.note-text { margin: 0; line-height: 1.4; font-style: italic; }

/* 오른쪽 액션 영역 */
.ticket-actions {
  width: 80px;
  border-left: 2px dashed #e0e0e0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background-color: #fafafa;
}

.action-btn {
  width: 40px; height: 40px;
  border-radius: 50%;
  border: 2px solid #e0e0e0;
  background: #fff;
  font-size: 1.2rem;
  cursor: pointer;
  transition: all 0.2s;
}
.action-btn:hover { transform: scale(1.1); box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.action-btn.approve:hover { border-color: #4caf50; background-color: #e8f5e9; }
.action-btn.reject:hover { border-color: #f44336; background-color: #ffebee; }

/* 도장 (Stamp) 효과 */
.stamp {
  border: 3px double;
  border-radius: 4px;
  padding: 5px 2px;
  font-weight: 900;
  font-family: 'Courier New', monospace;
  text-align: center;
  transform: rotate(-15deg);
  opacity: 0.8;
  font-size: 0.8rem;
  width: 70px;
}
.stamp.approved { color: #2e7d32; border-color: #2e7d32; }
.stamp.rejected { color: #c62828; border-color: #c62828; }

/* 하단 지그재그 */
.jagged-edge {
  position: absolute; bottom: 0; left: 0; right: 0; height: 10px;
  background: linear-gradient(-45deg, transparent 16px, #fff 0), linear-gradient(45deg, transparent 16px, #fff 0);
  background-size: 20px 20px;
  background-repeat: repeat-x;
}

/* 로딩 & 빈 상태 */
.loading-state, .no-requests {
  text-align: center;
  padding: 40px;
  color: #8d6e63;
}
.spinner {
  border: 4px solid #efebe9;
  border-top: 4px solid #8d6e63;
  border-radius: 50%;
  width: 30px; height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}
.empty-icon { font-size: 40px; margin-bottom: 10px; opacity: 0.5; }

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>