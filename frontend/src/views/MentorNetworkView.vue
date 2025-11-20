<template>
  <div class="mentor-dashboard">
    
    <section class="top-section">
      <div class="welcome-card">
        
        <div class="card-top">
          <div class="greeting-text">
            <span class="sub-label">MENTOR DASHBOARD</span>
            <h2>안녕하세요, {{ authStore.userName || '멘토' }}님 👋</h2>
            <p>이번 달 멘토링 활동 현황을 확인하세요.</p>
          </div>
          <div class="goal-badge">
            🎯 목표 달성률 <strong>0%</strong>
          </div>
        </div>

        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-icon blue">📅</div>
            <div class="stat-text">
              <span class="label">전체 신청</span>
              <strong class="value">{{ stats.total }}</strong>
            </div>
          </div>

          <div class="stat-item">
            <div class="stat-icon yellow">🕒</div>
            <div class="stat-text">
              <span class="label">응답 대기</span>
              <strong class="value">{{ stats.pending }}</strong>
            </div>
          </div>

          <div class="stat-item">
            <div class="stat-icon green">✅</div>
            <div class="stat-text">
              <span class="label">확정 세션</span>
              <strong class="value">{{ stats.approved }}</strong>
            </div>
          </div>
        </div>

      </div>
    </section>

    <section class="bottom-section">
      <div class="content-grid">
        
        <div class="main-panel">
          <div class="panel-header">
            <h3>다가오는 커피챗 / 신청 목록</h3>
            <span class="count-badge">{{ stats.total }}건</span>
          </div>
          <div class="panel-body list-scroll-area">
            <MentorRequestList />
          </div>
        </div>

        <div class="side-panel">
          <div class="panel-header">
            <h3>오늘의 일정</h3>
            <span class="date-badge">{{ todayDate }}</span>
          </div>
          <div class="panel-body">
            <ul v-if="todaysTasks.length > 0" class="todo-list">
              <li v-for="task in todaysTasks" :key="task.id" class="todo-item">
                <span class="time">{{ formatTime(task.start_time) }}</span>
                <div class="todo-info">
                  <strong>{{ task.mentee?.full_name || '멘티' }}님</strong>
                  <span class="status">예정됨</span>
                </div>
              </li>
            </ul>
            <div v-else class="empty-state">
              <p class="emoji">☕</p>
              <p>오늘 예정된 일정이 없습니다.</p>
            </div>
          </div>
        </div>

      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useMentorStore } from '@/store/mentorStore';
import MentorRequestList from '@/components/profile/MentorRequestList.vue';

const authStore = useAuthStore();
const mentorStore = useMentorStore();

onMounted(() => {
  mentorStore.fetchReceivedBookings();
});

const stats = computed(() => {
  const list = mentorStore.receivedBookings || [];
  return {
    total: list.length,
    pending: list.filter(b => b.status === 'pending').length,
    approved: list.filter(b => b.status === 'approved').length
  };
});

const todayDate = computed(() => {
  const d = new Date();
  return `${d.getMonth() + 1}월 ${d.getDate()}일`;
});

const todaysTasks = computed(() => {
  const today = new Date().toDateString();
  return (mentorStore.receivedBookings || [])
    .filter(b => {
      if (b.status !== 'approved') return false;
      return new Date(b.start_time).toDateString() === today;
    })
    .sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
});

function formatTime(isoString) {
  return new Date(isoString).toLocaleTimeString('ko-KR', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });
}
</script>

<style scoped>
.mentor-dashboard {
  width: 100%;
  height: 100%; /* 화면 전체 채움 */
  display: flex;
  flex-direction: column;
  background-color: #fff;
}

/* --- 1. 상단 섹션 (1/3 높이) --- */
.top-section {
  /* 화면 높이의 약 30~35% 차지 */
  flex: 0 0 35%; 
  min-height: 250px; 
  padding: 30px 40px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 🔥 통합된 회색 박스 (카드) */
.welcome-card {
  width: 100%;
  max-width: 1100px;
  height: 100%;
  background-color: #f8f9fa; /* 연한 회색 배경 */
  border-radius: 20px;       /* 둥근 모서리 */
  padding: 30px 40px;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: space-between; /* 위(인사말) 아래(통계) 배분 */
  box-shadow: 0 4px 20px rgba(0,0,0,0.03); /* 아주 은은한 그림자 */
}

/* (1) 인사말 영역 */
.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.sub-label {
  font-size: 12px;
  font-weight: 700;
  color: #6d28d9;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  display: block;
}
.greeting-text h2 {
  font-size: 26px;
  color: #111827;
  margin: 0 0 6px 0;
}
.greeting-text p {
  color: #6b7280;
  margin: 0;
  font-size: 15px;
}
.goal-badge {
  background: #fff;
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 13px;
  color: #4b5563;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.goal-badge strong {
  color: #6d28d9;
}

/* (2) 통계 아이템 행 */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.stat-item {
  background: #ffffff; /* 박스 안의 흰색 카드들 */
  border-radius: 16px;
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: transform 0.2s;
}
.stat-item:hover {
  transform: translateY(-2px);
}
.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}
.stat-icon.blue { background: #eff6ff; color: #3b82f6; }
.stat-icon.yellow { background: #fefce8; color: #eab308; }
.stat-icon.green { background: #f0fdf4; color: #22c55e; }

.stat-text {
  display: flex;
  flex-direction: column;
}
.stat-text .label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 2px;
}
.stat-text .value {
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}

/* --- 2. 하단 섹션 (나머지) --- */
.bottom-section {
  flex: 1; /* 남은 공간 채움 */
  padding: 0 40px 40px 40px;
  box-sizing: border-box;
  display: flex;
  justify-content: center;
  overflow: hidden; /* 내부 스크롤 사용 */
}
.content-grid {
  width: 100%;
  max-width: 1100px;
  display: grid;
  grid-template-columns: 2.5fr 1fr; /* 좌측을 더 넓게 */
  gap: 24px;
  height: 100%;
}

/* 패널 공통 스타일 */
.main-panel, .side-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.02);
}
.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
}
.panel-header h3 {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: #111827;
}
.count-badge {
  background: #f3f4f6; color: #4b5563;
  padding: 4px 10px; border-radius: 99px;
  font-size: 12px; font-weight: 600;
}
.date-badge {
  background: #eff6ff; color: #2563eb;
  padding: 4px 10px; border-radius: 8px;
  font-size: 12px; font-weight: 600;
}

.panel-body {
  padding: 0;
  flex: 1;
  overflow-y: auto; /* 스크롤 */
}
.list-scroll-area {
  padding: 10px;
}

/* 우측 투두 리스트 */
.todo-list { list-style: none; padding: 0; margin: 0; }
.todo-item {
  display: flex;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #f3f4f6;
  gap: 16px;
}
.todo-item:last-child { border-bottom: none; }
.todo-item .time {
  font-size: 13px;
  font-weight: 600;
  color: #6d28d9;
  background: #f5f3ff;
  padding: 4px 8px;
  border-radius: 6px;
  white-space: nowrap;
}
.todo-info {
  display: flex;
  flex-direction: column;
}
.todo-info strong { font-size: 14px; color: #374151; }
.todo-info .status { font-size: 11px; color: #059669; margin-top: 2px; }

.empty-state {
  padding: 40px 20px;
  text-align: center;
  color: #9ca3af;
}
.empty-state .emoji { font-size: 32px; margin-bottom: 10px; }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: 1fr; }
  .content-grid { grid-template-columns: 1fr; }
  .top-section { height: auto; min-height: auto; padding: 20px; }
  .welcome-card { height: auto; gap: 20px; }
}
</style>