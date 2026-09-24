<template>
  <div class="page-container cafe-theme">
    <div class="content-wrapper">
      <div class="header-section">
        <h1 class="handwritten-font">My Cafe Table</h1>
        <p>오늘의 주문 내역과 나의 이야기를 확인하세요</p>
      </div>

      <div class="main-grid">
        
        <aside class="left-column">
          
          <div class="card profile-card wood-texture">
            <div class="profile-header">
              <div class="avatar-circle">
                {{ authStore.userName?.charAt(0) || 'U' }}
                <span class="role-badge">
                  {{ authStore.userRole === 'mentee' ? 'GUEST' : 'BARISTA' }}
                </span>
              </div>
              <h2>{{ authStore.userName || '사용자' }}</h2>
              <div class="profile-info">
                <p class="email">{{ authStore.user?.email }}</p>
              </div>
            </div>

            <div v-if="authStore.userRole === 'mentee'" class="order-receipt-section">
              <div class="receipt-header-line">
                <span>ORDER LIST</span>
                <span class="date">{{ new Date().toLocaleDateString() }}</span>
              </div>

              <div class="receipt-content">
                <div v-if="pendingBookings.length > 0" class="receipt-item pending">
                  <span class="icon">⏳</span>
                  <div class="text">
                    <span class="status">Waiting...</span>
                    <span class="desc">{{ pendingBookings.length }}건 주문 확인 중</span>
                  </div>
                </div>

                <div v-if="approvedBookings.length > 0" class="receipt-item approved" @click="goToChat">
                  <span class="icon">🔔</span>
                  <div class="text">
                    <span class="status">Pick Up!</span>
                    <span class="desc">{{ approvedBookings.length }}건 준비 완료</span>
                  </div>
                  <button class="go-btn">Go</button>
                </div>

                <div v-if="pendingBookings.length === 0 && approvedBookings.length === 0" class="no-orders">
                  <p>현재 주문이 없습니다.</p>
                  <router-link to="/network?tab=list" class="menu-link">👉 메뉴판 보기</router-link>
                </div>
              </div>
              <div class="jagged-edge"></div>
            </div>

            <div class="napkin-container">
              <div class="napkin-paper">
                <div class="napkin-texture"></div>
                <label class="napkin-label">My Story (자기소개) 🖊️</label>
                
                <div v-if="isLoadingIntro" class="loading-text">로딩 중...</div>
                <div v-else class="napkin-content">
                  <textarea
                    v-model="selfIntroText"
                    placeholder="멘토님에게 나를 소개해보세요. (경력, 관심사, 고민 등)"
                    rows="12" 
                    class="handwriting-font"
                  ></textarea>
                  <button 
                    @click="handleUpdateProfile" 
                    :disabled="isUpdating || !selfIntroText.trim()"
                    class="pen-btn"
                    title="저장"
                  >
                    💾
                  </button>
                </div>
                <p v-if="updateSuccess" class="napkin-msg success">저장되었습니다!</p>
              </div>
            </div>

          </div>
        </aside>

        <main class="right-column">
          
          <div v-if="authStore.userRole === 'mentee'" class="tray-section">
            <h3 class="section-label">Serving Tray (오늘의 커피챗)</h3>
            <CafeTray 
              :items="upcomingChats" 
              @enter-chat="goToChat"
            />
          </div>

          <div class="card location-card">
            <div class="card-header">
              <h3>📍 단골 카페 위치 (내 좌표)</h3>
            </div>
            <LocationUpdater />
          </div>

           

          <div v-if="authStore.userRole === 'mentee'" class="card stamp-section">
            <div class="card-header"><h3>🎫 Membership Card</h3></div>
            <StampCard :count="completedChatCount" />
          </div>

          <div class="card schedule-card" v-if="authStore.userRole === 'mentor'">
            <div class="card-header"><h3>📅 Shift Schedule (일정 관리)</h3></div>
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

import LocationUpdater from '@/components/profile/LocationUpdater.vue';
import MentorAvailability from '@/components/profile/MentorAvailability.vue';
import StampCard from '@/components/common/StampCard.vue';
import CafeTray from '@/components/common/CafeTray.vue';
import CupSleeve from '@/components/common/CupSleeve.vue';

const authStore = useAuthStore();
const bookingStore = useBookingStore();
const router = useRouter();

const selfIntroText = ref('');
const isLoadingIntro = ref(false);
const isUpdating = ref(false);
const updateSuccess = ref(false);
const likedMentorsList = ref([]);

// 예약 상태
const pendingBookings = computed(() => bookingStore.bookings?.filter(b => b.status === 'pending') || []);
const approvedBookings = computed(() => bookingStore.bookings?.filter(b => b.status === 'approved') || []);

// 쿠폰/트레이
const completedChatCount = computed(() => {
  if (!bookingStore.bookings) return 0;
  const now = new Date();
  return bookingStore.bookings.filter(chat => chat.status === 'approved' && chat.end_time && new Date(chat.end_time) < now).length;
});

const upcomingChats = computed(() => {
  if (!bookingStore.bookings) return [];
  const now = new Date();
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return false;
    return !chat.end_time || new Date(chat.end_time) >= now;
  }).slice(0, 2);
});

function goToChat() { router.push({ name: 'network', query: { view: 'chat' } }); }
function goToMentorProfile() { router.push({ name: 'network', query: { tab: 'list' } }); }

onMounted(async () => {
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

  if (authStore.userRole === 'mentee') {
    await bookingStore.fetchBookings();
    await fetchLikedMentors();
  }
});

async function fetchLikedMentors() {
  try {
    const { data: likes, error: likeError } = await supabase
      .from('user_likes').select('liked_mentor_id').eq('user_id', authStore.userId);
    if (likeError) throw likeError;
    if (!likes || likes.length === 0) return;

    const mentorIds = likes.map(l => l.liked_mentor_id);
    // mentor_profiles 에는 company/team 컬럼이 없다. 회사명은 career_info("회사: OO, 직무: ...")에 들어 있다.
    const { data: mentors, error: mentorError } = await supabase
      .from('users').select('id, full_name, mentor_profiles(career_info)').in('id', mentorIds);
    if (mentorError) throw mentorError;

    // user_id 가 UNIQUE 라 1:1 관계로 인식되면 객체, 아니면 배열로 온다 → 둘 다 처리
    const careerOf = (m) => {
      const p = Array.isArray(m.mentor_profiles) ? m.mentor_profiles[0] : m.mentor_profiles;
      return p?.career_info || '';
    };
    const companyOf = (text) => text.match(/회사:\s*([^,]+)/)?.[1]?.trim();

    likedMentorsList.value = (mentors || []).map(m => ({
      id: m.id, name: m.full_name, company: companyOf(careerOf(m)) || '소속 없음'
    }));
  } catch (error) { console.error('찜 목록 로딩 실패:', error); }
}

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
  } catch (error) { console.error(error); } 
  finally { isUpdating.value = false; }
}
</script>

<style scoped>
/* ☕ 카페 테마 공통 */
.page-container { min-height: 100vh; background-color: #f7f4e8; padding: 40px 20px; color: #361205; }
.content-wrapper { max-width: 1200px; margin: 0 auto; }

/* 헤더 */
.header-section { margin-bottom: 30px; }
.handwritten-font { 
  font-family: serif; font-weight: 900; font-size: 2.5rem; 
  color: #361205; margin-bottom: 8px; letter-spacing: -1px; 
}
.header-section p { color: #8d6e63; }

/* 레이아웃 */
.main-grid { display: grid; grid-template-columns: 380px 1fr; gap: 30px; align-items: start; } /* 왼쪽 컬럼 너비 살짝 증가 */
@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

/* 카드 공통 */
.card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 4px 15px rgba(54, 18, 5, 0.05); margin-bottom: 24px; border: 1px solid #e0e0e0; }
.card-header h3 { font-size: 1.1rem; font-weight: 700; color: #361205; }

/* 1. 프로필 카드 */
.profile-card.wood-texture {
  background-color: #5d4037; 
  background-image: linear-gradient(135deg, #6d4c41 0%, #5d4037 100%);
  color: #fff; border: 4px solid #4e342e; padding: 30px 20px; text-align: center;
}
.profile-header { margin-bottom: 20px; }
.avatar-circle {
  width: 90px; height: 90px; background: #fdfbf7; color: #5d4037;
  font-size: 32px; font-weight: bold; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px; position: relative;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3); border: 4px solid #8d6e63;
}
.role-badge {
  position: absolute; bottom: -5px; background-color: #DF8723; color: white;
  font-size: 11px; padding: 3px 8px; border-radius: 10px; font-weight: 800;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}
.profile-header h2 { font-size: 1.4rem; font-weight: 700; margin: 0 0 5px; color: #fff; }
.email { font-size: 0.85rem; color: #d7ccc8; margin: 0; }

/* 2. 주문 현황 */
.order-receipt-section {
  background: #fff; padding: 20px 15px 30px; border-radius: 2px;
  color: #333; position: relative; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  margin-top: 20px; font-family: 'Courier New', monospace;
}
.receipt-header-line {
  border-bottom: 2px dashed #bbb; padding-bottom: 8px; margin-bottom: 12px;
  display: flex; justify-content: space-between; font-weight: bold; font-size: 0.9rem;
}
.receipt-item { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px dotted #ddd; }
.receipt-item .icon { font-size: 1.2rem; }
.receipt-item .text { flex: 1; text-align: left; }
.receipt-item .status { display: block; font-weight: 900; font-size: 0.95rem; }
.receipt-item .desc { font-size: 0.75rem; color: #666; }
.receipt-item.pending .status { color: #f57f17; }
.receipt-item.approved .status { color: #2e7d32; }
.receipt-item.approved { cursor: pointer; transition: background 0.2s; }
.receipt-item.approved:hover { background-color: #f1f8e9; }
.go-btn { background: #3e2723; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; }
.no-orders { padding: 20px 0; font-size: 0.85rem; color: #888; text-align: center; }
.menu-link { color: #DF8723; font-weight: bold; text-decoration: none; display: block; margin-top: 5px; }
.jagged-edge {
  position: absolute; bottom: 0; left: 0; right: 0; height: 10px;
  background: linear-gradient(-45deg, transparent 16px, #fff 0), linear-gradient(45deg, transparent 16px, #fff 0);
  background-size: 20px 20px; background-repeat: repeat-x;
}

/* 3. 냅킨 메모 (확대됨 🔥) */
.napkin-container { margin-top: 25px; }
.napkin-paper {
  background-color: #fffdf5; padding: 25px; position: relative;
  box-shadow: 2px 3px 8px rgba(0,0,0,0.15); transform: rotate(-1deg);
  border: 1px solid #efebe9;
}
.napkin-label { display: block; font-family: serif; font-size: 1rem; color: #a1887f; margin-bottom: 10px; text-align: left; font-weight: bold; }
.handwriting-font {
  width: 100%; border: none; background: transparent;
  font-family: serif; font-size: 1.1rem; line-height: 1.8; color: #4e342e; /* 폰트 키움 */
  resize: none; outline: none; padding: 0;
  min-height: 200px;
}
.pen-btn { float: right; background: none; border: none; font-size: 1.5rem; cursor: pointer; transition: transform 0.2s; }
.pen-btn:hover { transform: scale(1.1); }
.napkin-msg { font-size: 0.9rem; color: #2e7d32; text-align: right; clear: both; font-weight: bold; margin-top: 5px; }

/* 4. 오른쪽 섹션 */
.right-column { display: flex; flex-direction: column; gap: 24px; }
.tray-section { margin-bottom: 10px; }
.section-label { font-size: 1.1rem; font-weight: 700; margin-bottom: 12px; border-left: 4px solid #DF8723; padding-left: 10px; color: #361205; }
.cups-scroll-area { display: flex; gap: 20px; overflow-x: auto; padding-bottom: 15px; }
.cups-scroll-area::-webkit-scrollbar { height: 6px; }
.cups-scroll-area::-webkit-scrollbar-thumb { background: #d7ccc8; border-radius: 3px; }
.empty-cups { text-align: center; color: #9ca3af; padding: 20px 0; }
.empty-cups .small { font-size: 12px; margin-top: 4px; }
.more-link { font-size: 0.8rem; color: #8d6e63; text-decoration: none; }

@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }
</style>