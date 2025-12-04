<template>
  <div class="page-container">
    <div class="content-wrapper">
      <div class="header-section">
        <h1>마이페이지</h1>
        <p>내 정보와 주문(예약) 상태를 확인하세요</p>
      </div>

      <div class="main-grid">
        
        <aside class="left-column">
          
          <div class="card profile-card">
            <div class="profile-header">
              <div class="avatar-circle">
                {{ authStore.userName?.charAt(0) || '유' }}
                <span class="role-badge">
                  {{ authStore.userRole === 'mentee' ? '멘티' : '멘토' }}
                </span>
              </div>
              <h2>{{ authStore.userName || '사용자' }}</h2>
              <div class="profile-info">
                <p><span class="icon">👤</span> {{ authStore.userName }}</p>
                <p><span class="icon">🆔</span> {{ authStore.userRole === 'mentee' ? '멘티' : '멘토' }}</p>
              </div>
            </div>

            <div v-if="authStore.userRole === 'mentee'" class="buzzer-section">
              <div class="divider"></div>
              <h3 class="section-title">주문 벨 (예약 상태)</h3>
              <CafeBuzzer 
                :status="currentBuzzerStatus" 
                @click="goToChatOrNetwork"
              />
            </div>

            <div class="napkin-container">
              <div class="napkin-paper">
                <div class="napkin-texture"></div>
                <label class="napkin-label">Napkin Note (Memo)</label>
                
                <div v-if="isLoadingIntro" class="loading-text">로딩 중...</div>
                <div v-else class="napkin-content">
                  <textarea
                    v-model="selfIntroText"
                    placeholder="여기에 자유롭게 메모하세요... (경력, 관심사 등)"
                    rows="6"
                    class="handwriting-font"
                  ></textarea>
                  <button 
                    @click="handleUpdateProfile" 
                    :disabled="isUpdating || !selfIntroText.trim()"
                    class="pen-btn"
                    title="수정하기"
                  >
                    ✏️
                  </button>
                </div>
                <p v-if="updateSuccess" class="napkin-msg success">저장됨!</p>
              </div>
            </div>

          </div>
        </aside>

        <main class="right-column">
          
          <div v-if="authStore.userRole === 'mentee'" class="tray-section">
            <h3 class="section-label">지금 준비된 커피챗</h3>
            <CafeTray 
              :items="upcomingChats" 
              @enter-chat="goToChat"
            />
          </div>

          <div class="card location-card">
            <div class="card-header"><h3>📍 나의 위치 정보 설정</h3></div>
            <LocationUpdater />
          </div>

          <div v-if="authStore.userRole === 'mentee'" class="card cup-section">
            <div class="card-header">
              <h3>🥤 찜한 멘토 (Wishlist)</h3>
              <router-link to="/network?tab=list" class="more-link">더보기 +</router-link>
            </div>
            
            <div v-if="likedMentorsList.length > 0" class="cups-scroll-area">
              <CupSleeve 
                v-for="(mentor, idx) in likedMentorsList" 
                :key="mentor.id" 
                :mentor="mentor"
                :index="idx"
                @click="goToMentorProfile(mentor)"
              />
            </div>
            <div v-else class="empty-cups">
              <p>아직 찜한 멘토가 없습니다.</p>
              <p class="small">네트워크 탭에서 멘토를 찾아보세요!</p>
            </div>
          </div>

          <div v-if="authStore.userRole === 'mentee'" class="card stamp-section">
            <div class="card-header"><h3>🎫 나의 활동 쿠폰</h3></div>
            <StampCard :count="completedChatCount" />
          </div>

          <div class="card schedule-card" v-if="authStore.userRole === 'mentor'">
            <div class="card-header"><h3>📅 내 일정 관리</h3></div>
            <MentorAvailability />
          </div>

        </main>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useBookingStore } from '@/store/bookingstore';
import { useRouter } from 'vue-router';
import api from '@/services/api';
import { supabase } from '@/supabaseClient';

// ✅ 컴포넌트 임포트
import LocationUpdater from '@/components/profile/LocationUpdater.vue';
import MentorAvailability from '@/components/profile/MentorAvailability.vue';
import CafeBuzzer from '@/components/common/CafeBuzzer.vue'; 
import StampCard from '@/components/common/StampCard.vue';
import CafeTray from '@/components/common/CafeTray.vue';
import CupSleeve from '@/components/common/CupSleeve.vue';

const authStore = useAuthStore();
const bookingStore = useBookingStore();
const router = useRouter();

// --- 상태 변수 ---
const selfIntroText = ref('');
const isLoadingIntro = ref(false);
const isUpdating = ref(false);
const updateSuccess = ref(false);
const updateError = ref(null);
const likedMentorsList = ref([]); // 찜한 멘토 목록

// ⭐️ [추가됨] career_info 텍스트 파싱 헬퍼 함수
function parseCareerInfo(text) {
  if (!text) return { company: '소속 없음' };
  // "회사: 삼성전자," 같은 패턴에서 회사명 추출
  const companyMatch = text.match(/회사:\s*([^,]+)/);
  return { 
    company: companyMatch ? companyMatch[1].trim() : '소속 없음' 
  };
}

// --- [3. 진동벨] 상태 계산 ---
const currentBuzzerStatus = computed(() => {
  const bookings = bookingStore.bookings;
  if (!bookings || bookings.length === 0) return 'idle';
  // 1순위: 승인됨 -> 픽업
  if (bookings.some(b => b.status === 'approved')) return 'pickup';
  // 2순위: 대기중 -> 진동
  if (bookings.some(b => b.status === 'pending')) return 'waiting';
  return 'idle';
});

// --- [1. 쿠폰] 완료 횟수 계산 ---
const completedChatCount = computed(() => {
  if (!bookingStore.bookings) return 0;
  const now = new Date();
  return bookingStore.bookings.filter(chat => {
    // 조건: 승인됨 + 시간이 지남
    if (chat.status !== 'approved') return false;
    if (!chat.end_time) return false;
    return new Date(chat.end_time) < now;
  }).length;
});

// --- [4. 트레이] 다가오는 일정 계산 ---
const upcomingChats = computed(() => {
  if (!bookingStore.bookings) return [];
  const now = new Date();
  // 조건: 승인됨 + 아직 시간 안 지남 (최대 2개)
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return false;
    if (!chat.end_time) return true;
    return new Date(chat.end_time) >= now;
  }).slice(0, 2);
});

// --- 이동 함수들 ---
function goToChatOrNetwork() {
  if (currentBuzzerStatus.value === 'pickup') {
    goToChat();
  } else {
    router.push({ name: 'network', query: { tab: 'list' } });
  }
}

function goToChat() {
  router.push({ name: 'network', query: { view: 'chat' } });
}

function goToMentorProfile() {
  router.push({ name: 'network', query: { tab: 'list' } });
}

// --- 데이터 로딩 (onMounted) ---
onMounted(async () => {
  // 1. 자기소개 불러오기
  if (authStore.userId && authStore.userRole) {
    isLoadingIntro.value = true;
    try {
      const response = await api.get('/profile/introduction', {
        params: { user_id: authStore.userId, role: authStore.userRole }
      });
      selfIntroText.value = response.data.introduction_text || '';
    } catch (err) { console.error(err); } 
    finally { isLoadingIntro.value = false; }
  }

  // 2. 멘티 전용 데이터 (예약 목록, 찜 목록)
  if (authStore.userRole === 'mentee') {
    await bookingStore.fetchBookings();
    await fetchLikedMentors();
  }
});

// ⭐️ [수정됨] 찜 목록 불러오기 (career_info 파싱 적용)
async function fetchLikedMentors() {
  try {
    const { data: likes, error: likeError } = await supabase
      .from('user_likes')
      .select('liked_mentor_id')
      .eq('user_id', authStore.userId);

    if (likeError) throw likeError;
    if (!likes || likes.length === 0) return;

    const mentorIds = likes.map(l => l.liked_mentor_id);

    // 멘토 정보 조회 (users 테이블 + mentor_profiles의 career_info)
    const { data: mentors, error: mentorError } = await supabase
      .from('users')
      .select('id, full_name, mentor_profiles(career_info)')
      .in('id', mentorIds);

    if (mentorError) throw mentorError;

    likedMentorsList.value = mentors.map(m => {
      // ⭐️ career_info를 파싱해서 company를 추출
      const profile = m.mentor_profiles?.[0] || {};
      const parsed = parseCareerInfo(profile.career_info);
      
      return {
        id: m.id,
        name: m.full_name,
        company: parsed.company // 파싱된 회사명 사용
      };
    });
  } catch (error) {
    console.error('찜 목록 로딩 실패:', error);
  }
}

// --- [5. 냅킨 메모] 저장 ---
async function handleUpdateProfile() {
  if (!selfIntroText.value.trim()) return;
  isUpdating.value = true;
  updateSuccess.value = false;
  try {
    await api.post('/profile/update-introduction', {
      user_id: authStore.userId, role: authStore.userRole, introduction_text: selfIntroText.value
    });
    updateSuccess.value = true;
    setTimeout(() => { updateSuccess.value = false; }, 3000);
  } catch (error) { updateError.value = '실패'; } 
  finally { isUpdating.value = false; }
}
</script>

<style scoped>
/* 페이지 레이아웃 */
.page-container { min-height: 100vh; background-color: #f9fafb; padding: 40px 20px; }
.content-wrapper { max-width: 1200px; margin: 0 auto; }
.header-section { margin-bottom: 30px; }
.header-section h1 { font-size: 28px; font-weight: 700; color: #111; margin-bottom: 8px; }
.header-section p { color: #666; }

.main-grid { display: grid; grid-template-columns: 340px 1fr; gap: 24px; align-items: start; }
@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

/* 카드 공통 스타일 */
.card { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.03); border: 1px solid #f3f4f6; margin-bottom: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.card-header h3 { font-size: 18px; font-weight: 700; color: #1f2937; }

/* 프로필 헤더 */
.profile-header { text-align: center; margin-bottom: 20px; }
.avatar-circle { width: 100px; height: 100px; background-color: #8b5cf6; color: white; font-size: 36px; font-weight: bold; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; position: relative; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.role-badge { position: absolute; bottom: 0; right: 0; background-color: #7c3aed; border: 3px solid white; font-size: 12px; padding: 4px 8px; border-radius: 20px; font-weight: 600; }
.profile-header h2 { font-size: 20px; font-weight: 700; margin-bottom: 16px; }
.profile-info { text-align: left; background-color: #f9fafb; padding: 16px; border-radius: 12px; }
.profile-info p { margin-bottom: 8px; color: #555; font-size: 14px; }
.icon { margin-right: 6px; }

/* 3. 진동벨 섹션 */
.buzzer-section { display: flex; flex-direction: column; align-items: center; padding-bottom: 20px; margin-bottom: 20px; }
.divider { width: 100%; height: 1px; background: #eee; margin: 20px 0; }
.section-title { font-size: 14px; font-weight: 700; color: #888; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; }

/* 5. 냅킨 메모 스타일 */
.napkin-container { padding-top: 10px; }
.napkin-paper { background-color: #fffdf5; padding: 20px; position: relative; box-shadow: 2px 3px 8px rgba(0,0,0,0.1); transform: rotate(-1deg); border: 1px solid #f0e6d2; }
.napkin-texture { position: absolute; top: 5px; left: 5px; right: 5px; bottom: 5px; border: 2px dashed #e8dfcc; pointer-events: none; }
.napkin-label { display: block; font-family: 'Courier New', monospace; font-size: 12px; color: #a1887f; margin-bottom: 8px; font-weight: bold; }
.handwriting-font { width: 100%; border: none; background: transparent; font-family: 'Gowun Dodum', sans-serif; font-size: 15px; line-height: 1.6; color: #4e342e; resize: none; outline: none; background-image: linear-gradient(transparent 95%, #e0e0e0 95%); background-size: 100% 1.6em; padding: 0; }
.pen-btn { position: absolute; bottom: -10px; right: -10px; background: #fff; border: 1px solid #ddd; border-radius: 50%; width: 32px; height: 32px; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.1); display: flex; align-items: center; justify-content: center; font-size: 14px; }
.napkin-msg { font-size: 12px; color: #4caf50; text-align: right; margin-top: 5px; font-weight: bold; }

/* 6. 컵 홀더 스타일 */
.cups-scroll-area { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 10px; }
.cups-scroll-area::-webkit-scrollbar { height: 6px; }
.cups-scroll-area::-webkit-scrollbar-thumb { background: #d7ccc8; border-radius: 3px; }
.empty-cups { text-align: center; color: #9ca3af; padding: 20px 0; }
.empty-cups .small { font-size: 12px; margin-top: 4px; }
.more-link { font-size: 12px; color: #8d6e63; text-decoration: none; }

/* 오른쪽 섹션 공통 */
.tray-section { margin-bottom: 30px; }
.section-label { font-size: 16px; font-weight: 700; color: #361205; margin-bottom: 12px; padding-left: 10px; border-left: 4px solid #DF8723; }
.right-column { display: flex; flex-direction: column; gap: 24px; }
</style>