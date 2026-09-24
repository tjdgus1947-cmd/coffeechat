<template>
  <div class="mentor-container cafe-theme">

    <div class="cafe-tabs">
      <button 
        @click="currentView = 'dashboard'" 
        :class="{ active: currentView === 'dashboard' }"
      >
        <span class="icon">📊</span> 매니저 대시보드
      </button>

      <button 
        @click="currentView = 'chat'" 
        :class="{ active: currentView === 'chat' }"
      >
        <span class="icon">💬</span> 채팅 (상담)
      </button>
    </div>

    <div v-show="currentView === 'dashboard'" class="mentor-dashboard">
      <section class="top-section">
        <div class="welcome-card wood-texture">
          
          <div class="card-top">
            <div class="greeting-text">
              <span class="sub-label">HEAD BARISTA DESK</span>
              <h2>안녕하세요, {{ authStore.userName || '멘토' }}님 ☕</h2>
              <p>오늘도 멘티들에게 따뜻한 성장을 내려주세요.</p>
            </div>
            <div class="goal-badge paper-texture">
              🎯 이번 달 목표 달성률 <strong>{{ goalProgress }}%</strong>
            </div>
          </div>

          <div class="stats-row">
            <div class="stat-ticket blue">
              <span class="pin">📍</span>
              <div class="stat-label">전체 신청</div>
              <div class="stat-value">{{ stats.total }}</div>
            </div>

            <div class="stat-ticket yellow">
              <span class="pin">📍</span>
              <div class="stat-label">응답 대기</div>
              <div class="stat-value">{{ stats.pending }}</div>
            </div>

            <div class="stat-ticket green">
              <span class="pin">📍</span>
              <div class="stat-label">확정 세션</div>
              <div class="stat-value">{{ stats.approved }}</div>
            </div>
          </div>

        </div>
      </section>

      <section class="content-section">
        <div class="content-wrapper">
          
          <div class="content-grid">
            <div class="main-panel">
              <div class="panel-header">
                <h3>📜 Incoming Orders (신청 목록)</h3>
                <span class="count-badge">{{ stats.total }}건</span>
              </div>
              <div class="panel-body list-scroll-area">
                <MentorRequestList />
              </div>
            </div>

            <div class="side-panel">
              <div class="panel-header">
                <h3>🎖️ Barista Level</h3>
                <span class="level-badge">Lv. {{ mentorLevel.level }}</span>
              </div>
              <div class="panel-body level-body">
                <div class="xp-info">
                  <p class="xp-total">
                    {{ mentorLevel.totalXP }}
                    <span class="unit"> XP</span>
                  </p>
                  <p class="xp-weekly">이번 주 획득 +{{ mentorLevel.weeklyXP }}</p>
                </div>

                <div class="xp-progress">
                  <div class="progress-header">
                    <span>Next Level</span>
                    <span>{{ mentorLevel.currentXP }} / {{ mentorLevel.nextLevelXP }}</span>
                  </div>
                  <div class="progress-bar-bg">
                    <div class="progress-fill" :style="{ width: mentorLevel.progress + '%' }"></div>
                  </div>
                </div>

                <div class="badges-section">
                  <h4>내 컬렉션 ({{ earnedBadges }} / {{ totalBadges }})</h4>
                  <div class="badges-grid">
                    <div
                      v-for="badge in badges"
                      :key="badge.name"
                      class="badge-item"
                      :class="{ earned: badge.earned }"
                    >
                      <span class="badge-icon">{{ badge.icon }}</span>
                      <span class="badge-name">{{ badge.name }}</span>
                    </div>
                  </div>
                </div>

                <div class="ranking-board">
                  <div class="chalk-text">
                    <p class="rank-title">🏆 이달의 우수 멘토</p>
                    <div class="rank-row">
                      <span class="my-rank">내 순위: #{{ myRanking.rank || '-' }}</span>
                      <span class="my-points">{{ myRanking.points }} P</span>
                    </div>
                    <div class="rank-trend" :class="getTrendColor(myRanking.diff)">
                      {{ getTrendIcon(myRanking.diff) }} {{ getTrendText(myRanking.diff) }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bottom-grid">
            <article class="review-panel">
              <div class="panel-header">
                <h3>💬 Guest Reviews (후기)</h3>
                <div class="rating-badge">
                  ⭐ {{ averageRating }}
                </div>
              </div>

              <div class="panel-body">
                <div v-if="recentReviews.length > 0" class="review-list">
                  <div v-for="review in recentReviews" :key="review.id" class="review-sticky">
                    <div class="pin-top">📌</div>
                    <p class="review-comment">"{{ review.comment }}"</p>
                    <div class="review-footer">
                      <span class="reviewer">- {{ review.menteeName }}</span>
                      <span class="stars">{{ '★'.repeat(review.rating) }}</span>
                    </div>
                  </div>
                </div>

                <div v-else class="empty-reviews">
                  <p>아직 작성된 후기가 없습니다.</p>
                </div>
              </div>
            </article>

            <article class="ranking-panel">
              <div class="panel-header">
                <h3>🏆 Hall of Fame</h3>
                <p class="top-ten-info">TOP 10 진입까지 {{ pointsToTopTen }}P</p>
              </div>

              <div class="panel-body">
                <div v-if="topMentors.length > 0" class="top-mentors-list">
                  <div
                    v-for="mentor in topMentors"
                    :key="mentor.id"
                    class="mentor-rank-row"
                  >
                    <span class="rank-num">#{{ mentor.rank }}</span>
                    <span class="rank-name">{{ mentor.name }}</span>
                    <span class="dots"></span>
                    <span class="rank-p">{{ mentor.points }}P</span>
                  </div>
                </div>
                <div v-else class="empty-ranking">
                  <p>데이터 집계 중...</p>
                </div>
              </div>
            </article>
          </div>

        </div>
      </section>
    </div>

    <div v-if="currentView === 'chat'" class="chat-view-wrapper">
      <div class="chat-layout">
        <ChatRoomList 
          @select-room="handleSelectRoom" 
          ref="chatRoomListRef"
          class="chat-room-list"
          :class="{ 'hidden-mobile': selectedChatRoom }"
        />
        <div class="chat-room-pane" :class="{ 'hidden-mobile': !selectedChatRoom }">
          <div v-if="selectedChatRoom" class="mobile-back-header">
            <button class="back-btn" @click="selectedChatRoom = null">← 목록으로</button>
          </div>
          <ChatRoom 
            :selected-room="selectedChatRoom"
            class="chat-room"
          />
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useMentorStore } from '@/store/mentorStore';
import { supabase } from '@/supabaseClient';

import MentorRequestList from '@/components/profile/MentorRequestList.vue';
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

const authStore = useAuthStore();
const mentorStore = useMentorStore();

const currentView = ref('dashboard');
const selectedChatRoom = ref(null);
const chatRoomListRef = ref(null);

const receivedReviews = ref([]);
const topMentors = ref([]);
const myRanking = ref({ rank: 0, diff: 0, points: 0 });
const pointsToTopTen = ref(0);

// --- 초기 데이터 로딩 ---
onMounted(async () => {
  mentorStore.fetchReceivedBookings();
  await Promise.all([
    fetchReceivedReviews(),
    fetchMentorRanking()
  ]);
});

function handleSelectRoom(room) {
  selectedChatRoom.value = room;
}

// ---------------- 리뷰 불러오기 ----------------
async function fetchReceivedReviews() {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data: reviews, error: reviewError } = await supabase
      .from('reviews')
      .select('id, created_at, rating, content, mentee_id')
      .eq('mentor_id', user.id)
      .order('created_at', { ascending: false })
      .limit(10);

    if (reviewError) throw reviewError;
    if (!reviews || reviews.length === 0) {
      receivedReviews.value = [];
      return;
    }

    const menteeIds = [...new Set(reviews.map(r => r.mentee_id))];
    const { data: mentees, error: menteeError } = await supabase
      .from('users').select('id, full_name').in('id', menteeIds);

    const menteeMap = {};
    (mentees || []).forEach(m => { menteeMap[m.id] = m; });

    receivedReviews.value = reviews.map(review => ({
      ...review,
      mentee: menteeMap[review.mentee_id] || null
    }));
  } catch (error) {
    console.error('리뷰 조회 실패:', error);
    receivedReviews.value = [];
  }
}

// ---------------- 멘토 랭킹 불러오기 ----------------
async function fetchMentorRanking() {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) return;

    const { data: reviewRows } = await supabase.from('reviews').select('mentor_id, rating');
    if (!reviewRows || reviewRows.length === 0) return;

    const statsMap = {};
    for (const row of reviewRows) {
      const mId = row.mentor_id;
      if (!mId) continue;
      if (!statsMap[mId]) statsMap[mId] = { mentor_id: mId, reviewCount: 0, totalRating: 0 };
      statsMap[mId].reviewCount += 1;
      statsMap[mId].totalRating += row.rating || 0;
    }

    const mentorStats = Object.values(statsMap).map(s => {
      const avgRating = s.reviewCount > 0 ? s.totalRating / s.reviewCount : 0;
      const points = s.reviewCount * 10 + avgRating * 20;
      return { mentor_id: s.mentor_id, points };
    });

    mentorStats.sort((a, b) => b.points - a.points);
    const mentorIds = mentorStats.map(m => m.mentor_id);

    const { data: mentorsInfo } = await supabase
      .from('users').select('id, full_name').in('id', mentorIds);

    const mentorNameMap = {};
    (mentorsInfo || []).forEach(m => { mentorNameMap[m.id] = m.full_name; });

    topMentors.value = mentorStats.slice(0, 10).map((m, index) => ({
      id: m.mentor_id,
      rank: index + 1,
      name: mentorNameMap[m.mentor_id] || '멘토',
      points: Math.round(m.points)
    }));

    const myIdx = mentorStats.findIndex(m => m.mentor_id === user.id);
    if (myIdx !== -1) {
      myRanking.value = { rank: myIdx + 1, diff: 0, points: Math.round(mentorStats[myIdx].points) };
      const lastRankPoint = mentorStats[Math.min(9, mentorStats.length - 1)].points;
      pointsToTopTen.value = Math.max(0, Math.round(lastRankPoint - myRanking.value.points));
    }
  } catch (error) {
    console.error('멘토 랭킹 조회 실패:', error);
  }
}

// ---------------- 통계/레벨 ----------------
const stats = computed(() => {
  const list = mentorStore.receivedBookings || [];
  return {
    total: list.length,
    pending: list.filter(b => b.status === 'pending').length,
    approved: list.filter(b => b.status === 'approved').length
  };
});

const goalProgress = computed(() => {
  if (stats.value.total === 0) return 0;
  return Math.round((stats.value.approved / stats.value.total) * 100);
});

const mentorLevel = computed(() => {
  const totalXP = stats.value.approved * 100 + stats.value.total * 20;
  const level = Math.floor(totalXP / 500) + 1;
  const currentXP = totalXP % 500;
  return { level, totalXP, currentXP, nextLevelXP: 500, progress: Math.round((currentXP / 500) * 100), weeklyXP: Math.min(totalXP, 300) };
});

const badges = computed(() => [
  { icon: '🌱', name: '첫 수락', earned: stats.value.approved > 0 },
  { icon: '☕', name: '숙련가', earned: stats.value.approved >= 5 },
  { icon: '⚡', name: '빠른 응답', earned: stats.value.pending === 0 && stats.value.total > 0 },
  { icon: '🏅', name: '10회 달성', earned: stats.value.approved >= 10 },
  { icon: '👑', name: '마스터', earned: stats.value.approved >= 20 }
]);

const earnedBadges = computed(() => badges.value.filter(b => b.earned).length);
const totalBadges = computed(() => badges.value.length);

const recentReviews = computed(() => {
  return receivedReviews.value.slice(0, 3).map(review => ({
    id: review.id,
    menteeName: review.mentee?.full_name || '멘티',
    rating: review.rating ?? 5,
    comment: review.content || '후기 내용이 없습니다.',
  }));
});

const averageRating = computed(() => {
  if (receivedReviews.value.length === 0) return '0.0';
  const total = receivedReviews.value.reduce((sum, r) => sum + (r.rating ?? 0), 0);
  return (total / receivedReviews.value.length).toFixed(1);
});

// 트렌드 헬퍼
const getTrendColor = (diff) => diff > 0 ? 'up' : (diff < 0 ? 'down' : 'same');
const getTrendIcon = (diff) => diff > 0 ? '🔺' : (diff < 0 ? '🔻' : '-');
const getTrendText = (diff) => diff === 0 ? '변동 없음' : Math.abs(diff);
</script>

<style scoped>
/* ☕ 전체 테마 설정 */
.mentor-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 73px); /* 네비바(70px + 테두리 3px) 제외 */
  height: calc(100dvh - 73px);
  background-color: #f7f4e8; /* 크림색 배경 */
  color: #3e2723;
  overflow: hidden;
}

/* 탭 메뉴 */
.cafe-tabs {
  display: flex;
  gap: 8px;
  padding-left: 40px;
  margin-top: 20px;
  margin-bottom: -1px;
  z-index: 10;
  flex-shrink: 0;
}

.cafe-tabs button {
  padding: 12px 24px;
  border: 1px solid #d7ccc8;
  border-bottom: none;
  background-color: #efebe9;
  color: #8d6e63;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.cafe-tabs button.active {
  background-color: #fff;
  color: #3e2723;
  padding-bottom: 14px;
  border-top: 3px solid #3e2723;
  font-weight: 800;
  box-shadow: 0 -2px 5px rgba(0,0,0,0.05);
}

.cafe-tabs .icon { margin-right: 6px; }

/* 대시보드 영역 */
.mentor-dashboard {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

/* 상단 환영 카드 (우드 텍스처) */
.top-section { padding: 30px 40px; }

.welcome-card.wood-texture {
  background-color: #5d4037;
  background-image: linear-gradient(135deg, #6d4c41 0%, #5d4037 100%);
  border: 4px solid #4e342e;
  border-radius: 16px;
  padding: 30px 40px;
  color: #fff;
  box-shadow: 0 6px 15px rgba(0,0,0,0.2);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.sub-label {
  font-size: 0.8rem; letter-spacing: 2px; color: #d7ccc8; font-weight: bold;
}

.greeting-text h2 {
  font-size: 1.8rem; margin: 5px 0; font-family: serif;
}

.goal-badge.paper-texture {
  background-color: #fff8e1;
  color: #3e2723;
  padding: 10px 20px;
  border-radius: 2px;
  transform: rotate(2deg);
  box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

/* 통계 티켓 (포스트잇 느낌) */
.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-ticket {
  background-color: #fff;
  padding: 15px 20px;
  border-radius: 2px;
  position: relative;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  text-align: center;
  color: #3e2723;
  transform: rotate(-1deg);
}
.stat-ticket:nth-child(2) { transform: rotate(1deg); }

.stat-ticket.blue { border-top: 4px solid #4fc3f7; }
.stat-ticket.yellow { border-top: 4px solid #ffb74d; }
.stat-ticket.green { border-top: 4px solid #81c784; }

.stat-ticket .pin {
  position: absolute; top: -15px; left: 50%; transform: translateX(-50%);
  font-size: 20px; text-shadow: 2px 2px 2px rgba(0,0,0,0.2);
}

.stat-label { font-size: 0.9rem; color: #8d6e63; font-weight: 700; margin-bottom: 5px; }
.stat-value { font-size: 2rem; font-weight: 900; }

/* 콘텐츠 섹션 */
.content-section { flex: 1; padding: 0 40px 40px; }
.content-wrapper { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; gap: 30px; }
.content-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
.bottom-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; }

/* 패널 공통 */
.main-panel, .side-panel, .review-panel, .ranking-panel {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}

.panel-header {
  padding: 15px 20px;
  background-color: #fafafa;
  border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.panel-header h3 { font-size: 1.1rem; color: #3e2723; margin: 0; font-weight: 800; }

/* 리스트 패널 */
.list-scroll-area { padding: 10px; max-height: 400px; overflow-y: auto; }

/* 레벨 & 배지 패널 */
.level-body { padding: 20px; display: flex; flex-direction: column; gap: 20px; }
.xp-total { font-size: 2rem; font-weight: 900; color: #3e2723; margin: 0; }
.xp-weekly { font-size: 0.8rem; color: #8d6e63; }

.progress-header { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 5px; color: #5d4037; }
.progress-bar-bg { height: 10px; background: #efebe9; border-radius: 5px; overflow: hidden; }
.progress-fill { height: 100%; background: #8d6e63; width: 50%; border-radius: 5px; }

.badges-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.badge-item {
  display: flex; align-items: center; gap: 8px; padding: 8px;
  border: 1px dashed #d7ccc8; border-radius: 6px; color: #bdbdbd;
}
.badge-item.earned {
  border-color: #ffb74d; background-color: #fff8e1; color: #e65100; font-weight: bold;
}

/* 칠판 스타일 랭킹 보드 */
.ranking-board {
  background-color: #3e2723;
  padding: 15px; border-radius: 6px; border: 4px solid #6d4c41;
  color: #fff; text-align: center;
}
.chalk-text { font-family: 'Courier New', monospace; }
.rank-title { font-size: 0.9rem; color: #ffecb3; margin-bottom: 10px; }
.rank-row { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
.rank-trend.up { color: #69f0ae; }
.rank-trend.down { color: #ff5252; }
.rank-trend.same { color: #bdbdbd; }

/* 리뷰 (포스트잇) */
.review-list {
  padding: 20px; background-color: #f7f4e8;
  display: flex; gap: 15px; overflow-x: auto;
}
.review-sticky {
  min-width: 200px; background: #fff9c4; padding: 15px;
  box-shadow: 2px 2px 5px rgba(0,0,0,0.1); transform: rotate(-2deg);
  position: relative; font-family: 'Nanum Pen Script', serif; font-size: 1.1rem;
}
.review-sticky:nth-child(even) { background: #e1bee7; transform: rotate(2deg); }
.pin-top { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); font-size: 1.2rem; }
.review-footer { margin-top: 10px; font-size: 0.9rem; text-align: right; color: #555; }

/* 랭킹 (메뉴판 리스트) */
.top-mentors-list { padding: 15px 20px; }
.mentor-rank-row {
  display: flex; align-items: center; padding: 8px 0; border-bottom: 1px dotted #ccc;
}
.rank-num { font-weight: 900; width: 30px; color: #8d6e63; }
.rank-name { font-weight: bold; color: #3e2723; }
.dots { flex: 1; border-bottom: 2px dotted #ccc; margin: 0 10px; position: relative; top: -4px; }
.rank-p { font-size: 0.9rem; color: #5d4037; }

/* 채팅 뷰 */
.chat-view-wrapper {
  padding: 20px 40px; height: 100%; box-sizing: border-box;
}
.chat-layout {
  display: grid; grid-template-columns: 350px 1fr; height: 100%;
  border: 1px solid #d7ccc8; border-radius: 8px; overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05); background: #fff;
}
.chat-room-list { border-right: 1px solid #eee; }

/* 반응형 */
@media (max-width: 1024px) {
  .content-grid, .bottom-grid, .stats-row { grid-template-columns: 1fr; }
}

/* ===== 레이아웃 보정 ===== */
/* 상단 환영 카드·탭을 아래 콘텐츠(최대 1200px)와 같은 폭·같은 왼쪽 선에 맞춤 */
.top-section > .welcome-card { max-width: 1200px; margin: 0 auto; }
.cafe-tabs { padding-left: max(40px, calc((100% - 1200px) / 2)); }
.cafe-tabs { overflow-x: auto; scrollbar-width: none; padding-top: 4px; }
.cafe-tabs::-webkit-scrollbar { display: none; }
.cafe-tabs button { flex-shrink: 0; white-space: nowrap; }
.card-top { gap: 16px; }
.goal-badge.paper-texture { flex-shrink: 0; white-space: nowrap; }
.greeting-text { min-width: 0; }

.chat-room-pane { display: flex; flex-direction: column; min-width: 0; height: 100%; overflow: hidden; }
.chat-room-pane .chat-room { flex: 1; min-height: 0; }
.mobile-back-header { display: none; padding: 10px 14px; border-bottom: 1px solid #eee; background: #faf7f2; }
.back-btn { background: none; border: none; font-weight: 700; color: #3e2723; cursor: pointer; }

/* 리뷰 포스트잇은 가로 스크롤 영역 안에서만 */
.review-panel, .review-list { min-width: 0; }
.review-sticky { flex-shrink: 0; max-width: 260px; }

@media (max-width: 1024px) {
  .top-section { padding: 20px; }
  .content-section { padding: 0 20px 30px; }
  .chat-view-wrapper { padding: 16px 20px; }
  .chat-layout { grid-template-columns: 300px 1fr; }
}

@media (max-width: 768px) {
  .mentor-container { height: calc(100vh - 63px); height: calc(100dvh - 63px); }
  .cafe-tabs { padding-left: 12px !important; margin-top: 12px; }
  .cafe-tabs button { padding: 10px 16px; font-size: 14px; }
  .top-section { padding: 14px 12px; }
  .welcome-card.wood-texture { padding: 20px 18px; }
  .card-top { flex-direction: column-reverse; align-items: flex-start; margin-bottom: 24px; }
  .goal-badge.paper-texture { padding: 6px 12px; font-size: 0.85rem; transform: rotate(1deg); }
  .greeting-text h2 { font-size: 1.4rem; }
  .stats-row { grid-template-columns: repeat(3, 1fr); gap: 10px; }
  .stat-ticket { padding: 12px 6px; }
  .stat-label { font-size: 0.75rem; white-space: nowrap; }
  .stat-value { font-size: 1.5rem; }
  .content-section { padding: 0 12px 24px; }
  .content-wrapper { gap: 20px; }
  .chat-view-wrapper { padding: 10px 12px; }
  .chat-layout { grid-template-columns: 1fr; }
  .chat-room-list { border-right: none; }
  .hidden-mobile { display: none !important; }
  .mobile-back-header { display: block; }
}
</style>
