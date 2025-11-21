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
            🎯 목표 달성률 <strong>{{ goalProgress }}%</strong> · <strong>{{ stats.total }}건</strong> 신청 처리
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

    <section class="content-section">
      <div class="content-wrapper">
        
        <!-- 첫 번째 행: 커피챗 목록 + 레벨 -->
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
              <h3>멘토 레벨</h3>
              <span class="level-badge">Lv. {{ mentorLevel.level }}</span>
            </div>
            <div class="panel-body level-body">
              <div class="xp-info">
                <p class="xp-total">
                  {{ mentorLevel.totalXP }}
                  <span class="unit"> P</span>
                </p>
                <p class="xp-weekly">이번 주 XP {{ mentorLevel.weeklyXP }}</p>
              </div>

              <div class="xp-progress">
                <div class="progress-header">
                  <span>다음 레벨까지</span>
                  <span>{{ mentorLevel.currentXP }} / {{ mentorLevel.nextLevelXP }} XP</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: mentorLevel.progress + '%' }"></div>
                </div>
              </div>

              <div class="badges-section">
                <h4>획득한 배지 ({{ earnedBadges }} / {{ totalBadges }})</h4>
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

              <div class="ranking-box">
                <div class="ranking-content">
                  <div>
                    <p class="ranking-label">내 순위</p>
                    <p class="ranking-value">{{ myRanking.rank ? `#${myRanking.rank}` : '데이터 없음' }}</p>
                    <p class="ranking-points">포인트 {{ myRanking.points }}P</p>
                  </div>
                  <div class="ranking-trend" :class="rankingTrendClass">
                    <span class="trend-icon">{{ rankingTrendIcon }}</span>
                    <span class="trend-text">{{ rankingTrendText }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 두 번째 행: 최근 받은 리뷰 + 멘토 랭킹 -->
        <div class="bottom-grid">
          <!-- 최근 받은 리뷰 -->
          <article class="review-panel">
            <div class="panel-header">
              <div>
                <h3>최근 받은 리뷰</h3>
                <p class="panel-desc">멘티 피드백을 확인하세요.</p>
              </div>
              <div class="rating-badge">
                <span class="star-icon">⭐</span>
                <span class="rating-value">{{ averageRating }}</span>
              </div>
            </div>

            <div class="panel-body">
              <div v-if="recentReviews.length > 0" class="review-list">
                <div v-for="review in recentReviews" :key="review.id" class="review-item">
                  <div class="review-header">
                    <div class="reviewer-info">
                      <img
                        :src="review.avatar || 'https://via.placeholder.com/40'"
                        :alt="review.menteeName"
                        class="reviewer-avatar"
                      />
                      <div class="reviewer-details">
                        <span class="reviewer-name">{{ review.menteeName }}</span>
                        <span class="review-date">{{ review.dateLabel }}</span>
                      </div>
                    </div>
                    <div class="review-stars">
                      <span
                        v-for="i in 5"
                        :key="i"
                        :class="i <= review.rating ? 'star filled' : 'star'"
                      >★</span>
                    </div>
                  </div>
                  <p class="review-session">{{ review.session }}</p>
                  <p class="review-comment">{{ review.comment }}</p>
                </div>
              </div>

              <div v-else class="empty-reviews">
                <p class="emoji">📝</p>
                <p>아직 리뷰가 없습니다. 커피챗이 완료되면 멘티에게 후기를 요청해보세요.</p>
              </div>
            </div>
          </article>

          <!-- 멘토 랭킹 -->
          <article class="ranking-panel">
            <div class="panel-header">
              <div>
                <h3>멘토 랭킹</h3>
                <p class="panel-desc">이번 달 상위 멘토 현황</p>
              </div>
              <div class="top-badge">
                상위 10위까지 {{ pointsToTopTen }}P
              </div>
            </div>

            <div class="panel-body">
              <!-- 내 순위 강조 박스 -->
              <div class="my-rank-box">
                <div class="rank-content">
                  <div class="rank-left">
                    <div class="rank-number">
                      {{ myRanking.rank ? `#${myRanking.rank}` : '-' }}
                    </div>
                    <div class="rank-info">
                      <p class="rank-label">내 순위</p>
                      <p class="rank-name">{{ authStore.userName || '멘토' }}</p>
                    </div>
                  </div>
                  <div class="rank-right">
                    <p class="rank-label">포인트</p>
                    <p class="rank-points">{{ myRanking.points }}P</p>
                  </div>
                </div>
              </div>

              <!-- 상위 멘토 리스트 -->
              <div v-if="topMentors.length > 0" class="top-mentors-list">
                <div
                  v-for="mentor in topMentors"
                  :key="mentor.id"
                  class="mentor-rank-item"
                >
                  <div class="mentor-rank-left">
                    <span class="mentor-rank-number">#{{ mentor.rank }}</span>
                    <div class="mentor-info">
                      <p class="mentor-name">{{ mentor.name }}</p>
                      <p class="mentor-category">포인트 {{ mentor.points }}P</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-else class="empty-ranking">
                <p>상위 멘토 데이터가 아직 준비되지 않았습니다.</p>
              </div>
            </div>
          </article>
        </div>

      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useMentorStore } from '@/store/mentorStore';
import { supabase } from '@/supabaseClient';
import MentorRequestList from '@/components/profile/MentorRequestList.vue';

const authStore = useAuthStore();
const mentorStore = useMentorStore();

const receivedReviews = ref([]);
const topMentors = ref([]);
const myRanking = ref({ rank: 0, diff: 0, points: 0 });
const pointsToTopTen = ref(0);

onMounted(async () => {
  mentorStore.fetchReceivedBookings();
  await Promise.all([
    fetchReceivedReviews(),
    fetchMentorRanking()
  ]);
});

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
      .from('users')
      .select('id, full_name')
      .in('id', menteeIds);

    if (menteeError) {
      console.error('멘티 정보 조회 실패:', menteeError);
    }

    const menteeMap = {};
    (mentees || []).forEach(m => {
      menteeMap[m.id] = m;
    });

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

    const { data: reviewRows, error: reviewsError } = await supabase
      .from('reviews')
      .select('mentor_id, rating');

    if (reviewsError) throw reviewsError;

    if (!reviewRows || reviewRows.length === 0) {
      topMentors.value = [];
      myRanking.value = { rank: 0, diff: 0, points: 0 };
      pointsToTopTen.value = 0;
      return;
    }

    // mentor_id별 리뷰 수 / 평점 집계
    const statsMap = {};
    for (const row of reviewRows) {
      const mId = row.mentor_id;
      if (!mId) continue;
      if (!statsMap[mId]) {
        statsMap[mId] = { mentor_id: mId, reviewCount: 0, totalRating: 0 };
      }
      statsMap[mId].reviewCount += 1;
      statsMap[mId].totalRating += row.rating || 0;
    }

    const mentorStats = Object.values(statsMap).map(s => {
      const avgRating = s.reviewCount > 0 ? s.totalRating / s.reviewCount : 0;
      // 포인트 계산 규칙 (원하면 나중에 바꿔도 됨)
      const points = s.reviewCount * 10 + avgRating * 20;
      return {
        mentor_id: s.mentor_id,
        reviewCount: s.reviewCount,
        avgRating,
        points
      };
    });

    // 포인트 기준 내림차순 정렬
    mentorStats.sort((a, b) => b.points - a.points);

    const mentorIds = mentorStats.map(m => m.mentor_id);

    const { data: mentorsInfo, error: mentorsError } = await supabase
      .from('users')
      .select('id, full_name, role')
      .in('id', mentorIds)
      .eq('role', 'mentor');

    if (mentorsError) throw mentorsError;

    const mentorNameMap = {};
    (mentorsInfo || []).forEach(m => {
      mentorNameMap[m.id] = m.full_name;
    });

    topMentors.value = mentorStats.slice(0, 10).map((m, index) => ({
      id: m.mentor_id,
      rank: index + 1,
      name: mentorNameMap[m.mentor_id] || '멘토',
      points: Math.round(m.points)
    }));

    // 내 순위/포인트 계산
    const myIdx = mentorStats.findIndex(m => m.mentor_id === user.id);
    if (myIdx !== -1) {
      const myPoints = Math.round(mentorStats[myIdx].points);
      myRanking.value = { rank: myIdx + 1, diff: 0, points: myPoints };

      let topTenThreshold = 0;
      if (mentorStats.length >= 10) {
        topTenThreshold = mentorStats[9].points;
      } else {
        topTenThreshold = mentorStats[mentorStats.length - 1].points;
      }
      const gap = topTenThreshold - mentorStats[myIdx].points;
      pointsToTopTen.value = gap > 0 ? Math.round(gap) : 0;
    } else {
      myRanking.value = { rank: 0, diff: 0, points: 0 };
      pointsToTopTen.value = 0;
    }
  } catch (error) {
    console.error('멘토 랭킹 조회 실패:', error);
    topMentors.value = [];
    myRanking.value = { rank: 0, diff: 0, points: 0 };
    pointsToTopTen.value = 0;
  }
}

// ---------------- 기본 통계/레벨 ----------------
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
  const nextLevelXP = 500;
  const progress = Math.round((currentXP / nextLevelXP) * 100);
  const weeklyXP = Math.min(totalXP, 300);
  return { level, totalXP, currentXP, nextLevelXP, progress, weeklyXP };
});

const badges = computed(() => [
  { icon: '🏆', name: '첫 수락', earned: stats.value.approved > 0 },
  { icon: '⭐', name: '완료 전문가', earned: stats.value.approved >= 5 },
  { icon: '⚡', name: '빠른 응답', earned: stats.value.pending === 0 && stats.value.total > 0 },
  { icon: '🎖️', name: '10회 달성', earned: stats.value.approved >= 10 },
  { icon: '👑', name: '20회 달성', earned: stats.value.approved >= 20 }
]);

const earnedBadges = computed(() => badges.value.filter(b => b.earned).length);
const totalBadges = computed(() => badges.value.length);

// 트렌드용 (지금은 diff=0이라 "변동 없음"만 뜸)
const bookingsThisMonth = computed(() => {
  const now = new Date();
  return (mentorStore.receivedBookings || []).filter(b => {
    const date = new Date(b.created_at || b.start_time);
    return (
      date.getFullYear() === now.getFullYear() &&
      date.getMonth() === now.getMonth()
    );
  });
});

const bookingsLastMonth = computed(() => {
  const now = new Date();
  const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  return (mentorStore.receivedBookings || []).filter(b => {
    const date = new Date(b.created_at || b.start_time);
    return (
      date.getFullYear() === lastMonth.getFullYear() &&
      date.getMonth() === lastMonth.getMonth()
    );
  });
});

const approvedThisMonth = computed(
  () => bookingsThisMonth.value.filter(b => b.status === 'approved').length
);
const approvedLastMonth = computed(
  () => bookingsLastMonth.value.filter(b => b.status === 'approved').length
);

// 필요하면 나중에 diff 계산을 여기서 myRanking.value에 반영해도 됨

const rankingTrendClass = computed(() => {
  if (!stats.value.total) return 'text-gray-400';
  if (myRanking.value.diff > 0) return 'text-green-600';
  if (myRanking.value.diff < 0) return 'text-red-600';
  return 'text-gray-500';
});

const rankingTrendIcon = computed(() => {
  if (!stats.value.total) return '📊';
  if (myRanking.value.diff > 0) return '📈';
  if (myRanking.value.diff < 0) return '📉';
  return '➡️';
});

const rankingTrendText = computed(() => {
  if (!stats.value.total) return '변동 없음';
  if (myRanking.value.diff > 0) return `+${myRanking.value.diff}`;
  if (myRanking.value.diff < 0) return `${myRanking.value.diff}`;
  return '변동 없음';
});

// ---------------- 리뷰 파생 데이터 ----------------
const recentReviews = computed(() => {
  return receivedReviews.value.slice(0, 3).map(review => ({
    id: review.id,
    menteeName: review.mentee?.full_name || '멘티',
    rating: review.rating ?? 5,
    comment: review.content || '후기 내용이 없습니다.',
    session: '커피챗',
    dateLabel: formatRelativeTime(review.created_at),
    avatar: null
  }));
});

const averageRating = computed(() => {
  if (receivedReviews.value.length === 0) return 'N/A';
  const total = receivedReviews.value.reduce(
    (sum, r) => sum + (r.rating ?? 0),
    0
  );
  return (total / receivedReviews.value.length).toFixed(1);
});

// ---------------- 공통 유틸 ----------------
function formatRelativeTime(dateString) {
  if (!dateString) return '최근';
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return '오늘';
  if (diffDays === 1) return '어제';
  if (diffDays < 7) return `${diffDays}일 전`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}주 전`;
  return `${Math.floor(diffDays / 30)}개월 전`;
}
</script>

<style scoped>
.mentor-dashboard {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f9fafb;
}

/* 상단 섹션 */
.top-section {
  padding: 30px 40px;
  background: #fff;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f8f9fa;
  border-radius: 20px;
  padding: 30px 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.sub-label {
  font-size: 12px;
  font-weight: 700;
  color: #6d28d9;
  letter-spacing: 0.5px;
  display: block;
  margin-bottom: 6px;
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

.goal-badge strong { color: #6d28d9; }

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-item {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  transition: transform 0.2s;
}

.stat-item:hover { transform: translateY(-2px); }

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.stat-icon.blue { background: #eff6ff; }
.stat-icon.yellow { background: #fefce8; }
.stat-icon.green { background: #f0fdf4; }

.stat-text .label {
  font-size: 13px;
  color: #6b7280;
  display: block;
  margin-bottom: 4px;
}

.stat-text .value {
  font-size: 24px;
  font-weight: 800;
  color: #111827;
}

/* 콘텐츠 섹션 */
.content-section {
  flex: 1;
  padding: 30px 40px 40px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: 1.8fr 1.2fr;
  gap: 24px;
}

/* 패널 공통 스타일 */
.main-panel, .side-panel, .review-panel, .ranking-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.02);
}

.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #111827;
}

.panel-desc {
  font-size: 13px;
  color: #6b7280;
  margin: 4px 0 0 0;
}

.count-badge, .level-badge, .top-badge {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.count-badge { background: #f3f4f6; color: #4b5563; }
.level-badge { background: #f5f3ff; color: #6d28d9; }
.top-badge { background: #eff6ff; color: #2563eb; }

.rating-badge {
  display: flex;
  align-items: center;
  gap: 8px;
}

.star-icon { font-size: 20px; }
.rating-value { font-size: 22px; font-weight: 800; color: #111827; }

.panel-body {
  max-height: 400px;
  overflow-y: auto;
}

.list-scroll-area { padding: 10px; }

/* 레벨 패널 */
.level-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.xp-total {
  font-size: 32px;
  font-weight: 800;
  color: #111827;
  margin: 0;
}

.xp-total .unit {
  font-size: 16px;
  color: #6b7280;
  font-weight: 500;
}

.xp-weekly {
  font-size: 13px;
  color: #6b7280;
  margin: 4px 0 0 0;
}

.xp-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #6b7280;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6d28d9, #8b5cf6);
  transition: width 0.3s;
}

.badges-section h4 {
  font-size: 14px;
  font-weight: 700;
  color: #374151;
  margin: 0 0 12px 0;
}

.badges-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.badge-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #f9fafb;
  color: #9ca3af;
}

.badge-item.earned {
  background: #f5f3ff;
  border-color: #c4b5fd;
  color: #6d28d9;
}

.badge-icon { font-size: 18px; }
.badge-name { font-size: 13px; font-weight: 600; }

.ranking-box {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
}

.ranking-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ranking-label {
  font-size: 12px;
  color: #6b7280;
  margin: 0 0 4px 0;
}

.ranking-value {
  font-size: 18px;
  font-weight: 800;
  color: #111827;
  margin: 0 0 2px 0;
}

.ranking-points {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.ranking-trend {
  display: flex;
  align-items: center;
  gap: 6px;
}

.trend-icon { font-size: 16px; }
.trend-text { font-size: 13px; font-weight: 600; }

.text-green-600 { color: #059669; }
.text-red-600 { color: #dc2626; }
.text-gray-400 { color: #9ca3af; }
.text-gray-500 { color: #6b7280; }

/* 리뷰 패널 */
.review-list {
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  background: #f9fafb;
  border-radius: 12px;
  padding: 16px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reviewer-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reviewer-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.reviewer-name {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  display: block;
}

.review-date {
  font-size: 12px;
  color: #6b7280;
}

.review-stars {
  display: flex;
  gap: 2px;
}

.star {
  color: #d1d5db;
  font-size: 14px;
}

.star.filled {
  color: #fbbf24;
}

.review-session {
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
  margin: 0 0 8px 0;
}

.review-comment {
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
  margin: 0;
}

.empty-reviews {
  padding: 60px 20px;
  text-align: center;
  color: #9ca3af;
}

.empty-reviews .emoji {
  font-size: 40px;
  margin-bottom: 12px;
}

/* 랭킹 패널 */
.my-rank-box {
  margin: 20px 24px;
  background: linear-gradient(135deg, #eff6ff, #f5f3ff);
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #e0e7ff;
}

.rank-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rank-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.rank-number {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #6d28d9, #8b5cf6);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 800;
}

.rank-name {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.rank-right {
  text-align: right;
}

.rank-points {
  font-size: 18px;
  font-weight: 800;
  color: #6d28d9;
  margin: 0;
}

.top-mentors-list {
  padding: 0 24px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mentor-rank-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.mentor-rank-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mentor-rank-number {
  font-size: 14px;
  font-weight: 700;
  color: #6b7280;
  min-width: 24px;
}

.mentor-info {
  display: flex;
  flex-direction: column;
}

.mentor-name {
  font-size: 14px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.mentor-category {
  font-size: 12px;
  color: #6b7280;
  margin: 2px 0 0 0;
}

.empty-ranking {
  padding: 60px 20px;
  text-align: center;
  color: #9ca3af;
  font-size: 14px;
}

/* 반응형 */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .top-section,
  .content-section {
    padding: 20px;
  }
  
  .welcome-card {
    padding: 20px;
  }
  
  .card-top {
    flex-direction: column;
    gap: 16px;
  }
}
</style>
