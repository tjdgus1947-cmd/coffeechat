<!-- MenteeNetworkView.vue -->

<template>
  <div class="network-view-container">

    <!-- 1. 탭 메뉴 -->
    <div class="cafe-tabs">
      <button 
        @click="currentView = 'graph'" 
        :class="{ active: currentView === 'graph' }"
      >
        <span class="icon">☕</span> 네트워크
      </button>
      <button 
        @click="currentView = 'map'" 
        :class="{ active: currentView === 'map' }"
      >
        <span class="icon">🗺️</span> 지도
      </button>
      <button 
        @click="currentView = 'list'" 
        :class="{ active: currentView === 'list' }"
      >
        <span class="icon">📋</span> 파트너 목록
      </button>
      <button 
        @click="currentView = 'management'" 
        :class="{ active: currentView === 'management' }"
      >
        <span class="icon">🧾</span> 약속 관리
      </button>
    </div>

    <!-- 2. 메인 컨텐츠 영역 -->
    <div class="paper-panel">
      
      <!-- 네트워크 뷰 -->
      <div v-show="currentView === 'graph'" class="view-content graph-wrapper">
        
        <!-- 상단 정보 스트립 -->
        <div class="info-strip">
          <div class="tape-left"></div>
          <div class="info-text">
            <span class="highlight">Tip.</span> 바리스타(멘토)를 <strong>더블 클릭</strong>하여 찜(❤️) 목록에 담아보세요!
          </div>
          <div class="like-counter">
            내가 찜한 바리스타 <span class="badge">{{ likedMentors.length }}</span>명
          </div>
          <div class="tape-right"></div>
        </div>

        <!-- 데이터가 없을 때 안내 문구 -->
        <div v-if="graphNodes.length === 0 && !isLoadingTopMentors" class="empty-graph-message">
          <p>☕ 아직 추천 파트너가 준비되지 않았습니다.</p>
          <p>잠시만 기다려주시거나, 프로필을 업데이트 해보세요!</p>
        </div>

        <!-- 그래프 컴포넌트 -->
        <NetworkGraph
          v-else
          :nodes="graphNodes"
          :edges="graphEdges"
          @node-click="handleNodeClick"
          @node-double-click="handleNodeDoubleClick"
          class="graph-component"
        />
        
        <TopMentorsPanel
          :mentors="topMentorsList"
          :loading="isLoadingTopMentors"
          @select-mentor="handleTopMentorClick"
          class="top-mentors-floating"
        />
      </div>

      <!-- 지도 뷰 -->
      <div v-show="currentView === 'map'" class="view-content map-wrapper">
        <MentorMap />
      </div>

      <!-- 멘토 목록 뷰 -->
      <div v-show="currentView === 'list'" class="view-content list-wrapper">
        <MentorListPanel
          :mentors="topMentorsList"
          :loading="isLoadingTopMentors"
          :currentUserId="currentUserId"
          @view-profile="handleTopMentorClick"
          @open-booking="openBookingModal"
        />
      </div>

      <!-- 커피챗 관리 뷰 -->
      <div v-if="currentView === 'management'" class="view-content management-wrapper">
        <div class="receipt-style-container">
          <!-- 로딩 중 -->
          <div v-if="bookingStore.isLoading" class="loading-state">
            <p>🧾 주문 내역을 불러오는 중...</p>
          </div>

          <div v-else>
            <section class="manage-section completed-section">
              <div class="section-header">
                <h3>🎉 지난 만남 (완료)</h3>
                <span class="desc">종료된 세션입니다. 후기를 남겨주세요.</span>
              </div>
              <div v-if="completedChats.length > 0" class="chat-list">
                <div v-for="chat in completedChats" :key="chat.id" class="chat-card completed">
                  <div class="chat-info">
                    <span class="mentor-name">{{ chat.mentor?.full_name || '바리스타' }}님</span>
                    <span class="chat-time">{{ formatSchedule(chat.start_time, chat.end_time) }}</span>
                  </div>
                  <button class="review-btn" :class="{ 'reviewed': chat.has_review }" @click="openReviewModal(chat)">
                    {{ chat.has_review ? '📖 후기 확인' : '✍️ 후기 작성' }}
                  </button>
                </div>
              </div>
              <div v-else class="empty-state-box">아직 완료된 만남이 없습니다.</div>
            </section>

            <section class="manage-section active-section">
              <div class="section-header">
                <h3>📨 약속 현황 (진행 중)</h3>
                <span class="desc">승인 대기 중이거나 예정된 일정입니다.</span>
              </div>
              <div v-if="activeChats.length > 0" class="chat-list">
                <div v-for="chat in activeChats" :key="chat.id" class="chat-card">
                  <div class="chat-top">
                    <span class="mentor-name">{{ chat.mentor?.full_name || '바리스타' }}님</span>
                    <span :class="['status-badge', chat.status]">
                      {{ getStatusLabel(chat.status) }}
                    </span>
                  </div>
                  <div class="chat-details">
                    <p v-if="chat.start_time">📅 {{ formatSchedule(chat.start_time, chat.end_time) }}</p>
                    <p v-else class="no-time">시간 정보 없음</p>
                  </div>
                </div>
              </div>
              <div v-else class="empty-state-box">
                <p>현재 진행 중인 약속이 없습니다.</p>
                <button class="link-btn" @click="currentView = 'list'">👉 파트너 찾으러 가기</button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>

    <!-- 모달 및 플로팅 버튼 -->
    <MentorProfileModal
      v-if="selectedMentor"
      :mentor="selectedMentor"
      :currentUserId="currentUserId"
      :isLiked="isLiked(selectedMentor.id || selectedMentor.user_id)"
      @close="closeSidebar"
      @book="openBookingModal"
      @toggle-like="toggleLike"
      class="modal-overlay"
    />

    <BookingModal
      :show="isModalOpen"
      :mentor-id="mentorForBooking?.id"
      :mentor-name="mentorForBooking?.name"
      @close="closeBookingModal"
      @booking-confirmed="closeBookingModal"
    />

    <ReviewModal
      :show="isReviewModalOpen"
      :chat="selectedChatForReview"
      :mentee-id="currentUserId"
      @close="closeReviewModal"
      @review-submitted="handleReviewSubmitted"
    />

    <button
      v-if="currentView === 'graph'"
      class="floating-chat-btn"
      @click="goToChat"
      title="채팅하기"
    >
      💬
      <span v-if="chatStore.unreadCount > 0" class="chat-badge">
        {{ chatStore.unreadCount > 9 ? '9+' : chatStore.unreadCount }}
      </span>
    </button>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from 'axios';
import { supabase } from '@/supabaseClient';
import { useRoute } from 'vue-router';

import { useNetworkStore } from '@/store/network';
import { useBookingStore } from '@/store/bookingstore'; 
import { useChatStore } from '@/store/chatStore';

import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import BookingModal from '@/components/calendar/BookingModal.vue';
import MentorMap from '@/components/map/MentorMap.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorListPanel from '@/components/list/MentorListPanel.vue';
import MentorProfileModal from '@/components/profile/MentorProfileModal.vue';
import ReviewModal from '@/components/review/ReviewModal.vue';
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

const route = useRoute();
const networkStore = useNetworkStore();
const bookingStore = useBookingStore();
const chatStore = useChatStore();

const currentView = ref('graph');
const selectedMentor = ref(null);
const mentorForBooking = ref(null);
const isModalOpen = ref(false);
const currentUserId = ref('');
const topMentorsList = ref([]);
const isLoadingTopMentors = ref(false);
const isReviewModalOpen = ref(false);
const selectedChatForReview = ref(null);
const reviewStatusMap = ref({});
const likedMentors = ref([]);

onMounted(async () => {
  if (route.query.tab === 'list') currentView.value = 'list';
  networkStore.fetchNetworkData();
  try {
    const { data: { user }, error } = await supabase.auth.getUser();
    if (user) {
      currentUserId.value = user.id;
      await fetchTopMentorsWithRealScore();
      await bookingStore.fetchBookings();
      await loadLikedMentors();
      await fetchReviewStatus();
    }
  } catch (err) { console.error('Auth 에러:', err); }
});

async function loadLikedMentors() {
  try {
    const { data } = await supabase.from('user_likes').select('liked_mentor_id').eq('user_id', currentUserId.value);
    likedMentors.value = (data || []).map(item => item.liked_mentor_id);
  } catch (error) { likedMentors.value = []; }
}

async function toggleLike(mentorId) {
  const isCurrentlyLiked = isLiked(mentorId);
  try {
    if (isCurrentlyLiked) {
      await supabase.from('user_likes').delete().eq('user_id', currentUserId.value).eq('liked_mentor_id', mentorId);
      likedMentors.value = likedMentors.value.filter(id => id !== mentorId);
    } else {
      await supabase.from('user_likes').insert({ user_id: currentUserId.value, liked_mentor_id: mentorId });
      likedMentors.value.push(mentorId);
    }
  } catch (error) { console.error('찜 변경 실패:', error); }
}

function isLiked(mentorId) { return likedMentors.value.includes(mentorId); }

const graphNodes = computed(() => {
  return networkStore.nodes.map(node => {
    if (node.data?.type === 'mentor') {
      const mentorId = node.data.id || node.data.user_id;
      return { ...node, data: { ...node.data, isLiked: isLiked(mentorId) } };
    }
    return node;
  });
});
const graphEdges = computed(() => networkStore.edges);

async function fetchTopMentorsWithRealScore() {
  if (!currentUserId.value) {
    topMentorsList.value = networkStore.nodes.filter(n => n.data?.type === 'mentor').map(n => n.data);
    return;
  }
  isLoadingTopMentors.value = true;
  try {
    const { data: { session } } = await supabase.auth.getSession();
    const response = await axios.get(`http://localhost:8000/api/matching/find-matches`, {
      headers: { Authorization: `Bearer ${session?.access_token}` },
      params: { user_id: currentUserId.value, role: 'mentee', limit: 100 }
    });
    topMentorsList.value = response.data.matches.map(match => {
      const node = networkStore.nodes.find(n => n.data?.user_id === match.user_id);
      return node ? { ...node.data, ...match, isLiked: isLiked(match.user_id) } : null;
    }).filter(Boolean);
  } catch (e) { console.error(e); } 
  finally { isLoadingTopMentors.value = false; }
}

const completedChats = computed(() => {
  const now = new Date();
  if (!bookingStore.bookings) return []; 
  return bookingStore.bookings
    .filter(chat => {
      if (chat.status !== 'approved') return false;
      if (!chat.end_time) return false;
      return new Date(chat.end_time) < now; 
    })
    .map(chat => ({
      ...chat,
      has_review: !!reviewStatusMap.value[chat.id]
    }));
});

const activeChats = computed(() => {
  const now = new Date();
  if (!bookingStore.bookings) return []; 
  return bookingStore.bookings.filter(chat => {
    if (chat.status !== 'approved') return true;
    if (!chat.end_time) return true; 
    return new Date(chat.end_time) >= now;
  });
});

const handleNodeClick = (node) => { selectedMentor.value = node.data?.type === 'mentor' ? node.data : null; };
const handleNodeDoubleClick = (node) => { if (node.data?.type === 'mentor') toggleLike(node.data.id || node.data.user_id); };
const handleTopMentorClick = (mentor) => { selectedMentor.value = mentor; };
const closeSidebar = () => { selectedMentor.value = null; };
const openBookingModal = (mentor) => { mentorForBooking.value = mentor; isModalOpen.value = true; };
const closeBookingModal = () => { isModalOpen.value = false; mentorForBooking.value = null; bookingStore.fetchBookings(); }; 
function goToChat() { currentView.value = 'chat'; }

async function fetchReviewStatus() {
  try {
    const { data } = await supabase.from('reviews').select('coffee_chat_id').eq('mentee_id', currentUserId.value);
    reviewStatusMap.value = {};
    (data || []).forEach(r => { reviewStatusMap.value[r.coffee_chat_id] = true; });
  } catch (error) { console.error(error); }
}

function getStatusLabel(status) { return status === 'approved' ? '승인됨' : (status === 'rejected' ? '거절됨' : '승인 대기'); }
function formatSchedule(start, end) { return start ? new Date(start).toLocaleDateString() : '미정'; }
function openReviewModal(chat) { selectedChatForReview.value = chat; isReviewModalOpen.value = true; }
function closeReviewModal() { isReviewModalOpen.value = false; selectedChatForReview.value = null; }
async function handleReviewSubmitted() { await bookingStore.fetchBookings(); await fetchReviewStatus(); }
</script>

<style scoped>
/* ☕ 배경 및 레이아웃 */
.network-view-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: calc(100vh - 70px); 
  position: relative;
  background-color: #F7F4E8;
  padding: 20px;
  box-sizing: border-box;
  overflow: hidden; 
}

/* ☕ 탭 메뉴 */
.cafe-tabs {
  display: flex;
  gap: 8px;
  padding-left: 10px;
  margin-bottom: -1px;
  z-index: 10;
  flex-shrink: 0;
}

.cafe-tabs button {
  padding: 12px 24px;
  border: 1px solid #D1A872;
  border-bottom: none;
  background-color: #EFE5D9;
  color: #8A5A34;
  border-radius: 12px 12px 0 0;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: all 0.2s ease;
}

.cafe-tabs button.active {
  background-color: #FFFFFF;
  color: #361205;
  padding-bottom: 14px;
  transform: translateY(-2px);
  box-shadow: 0 -4px 6px rgba(54, 18, 5, 0.1);
  font-weight: 800;
  border-top: 3px solid #DF8723;
}

.cafe-tabs .icon { margin-right: 6px; }

/* ☕ 메인 컨텐츠 영역 */
.paper-panel {
  flex-grow: 1;
  background-color: #FFFFFF;
  border: 1px solid #D1A872;
  border-radius: 0 16px 16px 16px;
  box-shadow: 0 10px 30px rgba(54, 18, 5, 0.08);
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* 모든 뷰의 공통 스타일 */
.view-content {
  width: 100%;
  height: 100%;
  position: relative;
  overflow-y: auto; 
}

/* 🌟 [수정] 그래프 뷰 래퍼 스타일 (높이 확보) */
.graph-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 500px; /* 최소 높이 보장 */
}

.graph-component {
  flex-grow: 1;
  width: 100%;
  height: 100%; /* 부모 높이 채우기 */
  background-color: #FCF9F2;
}

/* 빈 상태 메시지 */
.empty-graph-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: #8A5A34;
  font-size: 1.1rem;
  z-index: 5;
}

/* 🌟 관리 뷰 래퍼 스타일 */
.management-wrapper {
  background-color: #FAFAFA;
  padding: 0;
}

.receipt-style-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 0 20px 60px; 
}

/* 관리 섹션 스타일 */
.manage-section {
  margin-bottom: 40px;
  background-color: #FFFFFF;
  padding: 24px;
  border-radius: 8px;
  border: 1px dashed #D1A872; 
  box-shadow: 0 4px 10px rgba(0,0,0,0.03);
}

.section-header h3 {
  font-size: 1.2rem;
  color: #361205;
  border-bottom: 2px solid #361205;
  padding-bottom: 10px;
  margin-bottom: 10px;
  display: inline-block;
}

.desc {
  display: block;
  color: #8A5A34;
  margin-bottom: 20px;
  font-size: 0.95rem;
}

/* 채팅 리스트 카드 */
.chat-card {
  background: #FFFFFF;
  border: 1px solid #E6DCCD;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: transform 0.2s;
}

.chat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(54, 18, 5, 0.08);
  border-color: #DF8723;
}

.chat-card.completed {
  border-left: 4px solid #DF8723; 
}

.mentor-name {
  font-weight: 700;
  color: #361205;
  font-size: 1.1rem;
}

.chat-time {
  font-size: 0.9rem;
  color: #8A5A34;
  margin-top: 4px;
  display: block;
}

/* 버튼 스타일 */
.review-btn {
  background-color: #F7F4E8;
  color: #361205;
  border: 1px solid #D1A872;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.review-btn:hover {
  background-color: #DF8723;
  color: white;
  border-color: #DF8723;
}

.link-btn {
  background: none;
  border: none;
  color: #DF8723;
  font-weight: bold;
  cursor: pointer;
  text-decoration: underline;
  margin-top: 10px;
}

/* 빈 상태 스타일 */
.empty-state-box {
  text-align: center;
  padding: 40px;
  color: #A67857;
  font-style: italic;
  background-color: #FDFBF7;
  border-radius: 8px;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #8A5A34;
  font-size: 1.1rem;
}

/* 기타 스타일 (그래프 등) */
.graph-info-bar { display: flex; justify-content: space-between; padding: 10px 20px; background: #FFF8E7; border-bottom: 1px dashed #D1A872; }
.info-strip { position: absolute; top: 20px; left: 50%; transform: translateX(-50%); z-index: 10; background: #FFF8E7; padding: 8px 30px; border: 1px dashed #DF8723; border-radius: 2px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; gap: 20px; align-items: center; }
.tape-left { position: absolute; left: -20px; top: -8px; width: 60px; height: 20px; background: rgba(223, 135, 35, 0.4); transform: rotate(-3deg); }
.tape-right { position: absolute; right: -20px; bottom: -8px; width: 60px; height: 20px; background: rgba(223, 135, 35, 0.4); transform: rotate(3deg); }
.info-text strong { color: #DF8723; }
.like-counter { border-left: 2px solid #E6DCCD; padding-left: 20px; font-weight: 600; }
.badge { background: #E06C75; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-left: 4px; }
.top-mentors-floating { position: absolute; top: 80px; right: 30px; z-index: 5; }
.floating-chat-btn { position: absolute; left: 30px; bottom: 30px; width: 60px; height: 60px; border-radius: 50%; background: #361205; color: white; border: 3px solid #D1A872; font-size: 26px; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 12px rgba(0,0,0,0.2); z-index: 20; }
.chat-badge { position: absolute; top: 0; right: 0; background: #E06C75; color: white; padding: 2px 6px; border-radius: 10px; font-size: 11px; border: 2px solid #361205; }
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 50; }
</style>