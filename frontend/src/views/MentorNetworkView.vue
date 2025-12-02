<template>
  <div class="network-view-container">

    <div class="view-switcher">
      <button @click="currentView = 'graph'" :class="{ active: currentView === 'graph' }">
        🔗 멘토 네트워크
      </button>

      <button @click="currentView = 'management'" :class="{ active: currentView === 'management' }">
        📅 예약 관리
        <span v-if="pendingCount > 0" class="badge">{{ pendingCount }}</span>
      </button>

      <button @click="currentView = 'chat'" :class="{ active: currentView === 'chat' }">
        💬 채팅
      </button>
    </div>

    <div v-show="currentView === 'graph'" class="graph-panel-wrapper">
      <div v-if="isLoadingGraph" class="loading-overlay">
        <div class="spinner"></div>
        <p>AI가 멘토님의 성향과 유사한 동료를 분석 중입니다...</p>
      </div>

      <NetworkGraph
        v-else
        :nodes="graphNodes"
        :edges="graphEdges"
        @node-click="handleNodeClick"
        class="graph-panel"
      />
      
      <TopMentorsPanel
        title="✨ 추천 동료 멘토"
        :mentors="similarMentorsList"
        :loading="isLoadingGraph"
        @select-mentor="handleTopMentorClick"
        class="top-mentors-floating"
      />
    </div>

    <div v-if="currentView === 'management'" class="management-panel">
      <section class="manage-section active-section">
        <div class="section-header">
          <h3>📩 들어온 요청 ({{ pendingRequests.length }})</h3>
        </div>
        <div v-if="pendingRequests.length > 0" class="chat-list">
          <div v-for="req in pendingRequests" :key="req.id" class="chat-card request-card">
            <div class="chat-top">
              <span class="mentee-name">🧑‍💻 멘티 (ID: {{ req.mentee_id?.slice(0,4) }}..)</span>
              <span class="request-time">{{ formatDate(req.created_at) }} 요청</span>
            </div>
            <div class="chat-details">
              <p><strong>희망 일정:</strong> {{ formatSchedule(req.start_time, req.end_time) }}</p>
              <p class="concern-text" v-if="req.concern">"{{ req.concern }}"</p>
            </div>
            <div class="action-buttons">
              <button class="btn-approve" @click="handleBookingStatus(req.id, 'approved')">수락</button>
              <button class="btn-reject" @click="handleBookingStatus(req.id, 'rejected')">거절</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state-box">대기 중인 요청이 없습니다.</div>
      </section>
    </div>

    <div v-if="currentView === 'chat'" class="chat-view-wrapper">
      <div class="chat-layout">
        <ChatRoomList @select-room="handleSelectRoom" class="chat-room-list" />
        <ChatRoom :selected-room="selectedChatRoom" class="chat-room" />
      </div>
    </div>

    <MentorSidebar
      v-if="currentView === 'graph' && selectedMentor"
      :mentor="selectedMentor"
      :currentUserId="currentUserId"
      :is-mentor-view="true" 
      @close="closeSidebar"
      class="sidebar-panel"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { supabase } from '@/supabaseClient';
import axios from 'axios';

// 컴포넌트 import (경로는 프로젝트 구조에 맞게 확인 필요)
import NetworkGraph from '@/components/graph/NetworkGraph.vue';
import TopMentorsPanel from '@/components/ranking/TopMentorsPanel.vue';
import MentorSidebar from '@/components/profile/MentorSidebar.vue';
import ChatRoomList from '@/components/chat/ChatRoomList.vue';
import ChatRoom from '@/components/chat/ChatRoom.vue';

import { useMentorStore } from '@/store/mentorStore'; 

const mentorStore = useMentorStore();

// 상태 변수
const currentView = ref('graph');
const currentUserId = ref('');
const isLoadingGraph = ref(false);

const graphNodes = ref([]);
const graphEdges = ref([]);
const similarMentorsList = ref([]);
const selectedMentor = ref(null);
const selectedChatRoom = ref(null);

onMounted(async () => {
  const { data: { user } } = await supabase.auth.getUser();
  if (user) {
    currentUserId.value = user.id;
    // 1. 멘토 네트워크(벡터 유사도) 가져오기
    await fetchMentorNetwork(user.id);
    
    // 2. 예약 요청 목록 가져오기
    if (mentorStore.fetchReceivedBookings) {
      await mentorStore.fetchReceivedBookings(); 
    }
  }
});

// 🔥 [핵심] 백엔드 API와 연결된 멘토 네트워크 로직
async function fetchMentorNetwork(mentorId) {
  isLoadingGraph.value = true;
  try {
    // 1. 우리가 만든 matching.py의 새 API 호출
    const response = await axios.get(`http://localhost:8000/api/matching/mentor-network`, {
      params: {
        user_id: mentorId,
        limit: 20,           // 최대 20명
        min_similarity: 0.1  // 최소 유사도 10% 이상
      }
    });
    
    // API 응답 구조: { center_user_id: "...", matches: [ { user_id, similarity, career_info }, ... ] }
    const { matches, center_user_id } = response.data;

    const nodes = [];
    const edges = [];

    // 2. 중심 노드 (나) 생성
    nodes.push({
      id: 'me',
      label: '나',
      type: 'input', 
      position: { x: 0, y: 0 },
      data: { user_id: center_user_id, full_name: '나', type: 'me' },
      style: { background: '#6d28d9', color: 'white', fontWeight: 'bold' }
    });

    // 3. 매칭된 멘토들 노드/엣지 생성
    if (matches && matches.length > 0) {
      const radius = 300; // 중심으로부터의 거리

      matches.forEach((match, index) => {
        // 원형 배치 (Circular Layout)
        const angle = (2 * Math.PI * index) / matches.length;
        
        // 라벨: 이름이 없으면 career_info 앞부분이나 ID 사용
        const labelText = match.career_info 
          ? (match.career_info.length > 8 ? match.career_info.substring(0,8)+'...' : match.career_info)
          : '멘토';

        nodes.push({
          id: match.user_id,
          label: labelText,
          type: 'mentor', // NetworkGraph 내부 로직에 따름 (default or custom)
          position: { 
            x: radius * Math.cos(angle), 
            y: radius * Math.sin(angle) 
          },
          data: { 
            ...match, 
            full_name: labelText, // 사이드바 표시용 이름 매핑
            type: 'mentor',
            matchingScore: (match.similarity * 100).toFixed(1) // 패널 표시용 점수
          }
        });

        // 엣지 생성 (유사도에 따라 굵기/색상 다르게 가능)
        edges.push({
          id: `edge-${index}`,
          source: 'me',
          target: match.user_id,
          animated: true,
          label: `${(match.similarity * 100).toFixed(0)}%`,
          style: { 
            stroke: '#7c3aed', 
            strokeWidth: 1 + (match.similarity * 5) // 유사도가 높으면 더 굵게
          }
        });
      });
      
      // 랭킹 리스트용 데이터 매핑
      similarMentorsList.value = matches.map(m => ({
        ...m,
        full_name: m.career_info || '동료 멘토',
        matchingScore: (m.similarity * 100).toFixed(1)
      }));
    }

    graphNodes.value = nodes;
    graphEdges.value = edges;

  } catch (error) {
    console.error("멘토 네트워크 로드 실패:", error);
    // 에러 시 나 자신만 표시
    graphNodes.value = [{ id: 'me', label: '나', position: {x:0, y:0}, data: {type:'me'} }];
  } finally {
    isLoadingGraph.value = false;
  }
}

// --- 예약 관리 Computed ---
const pendingRequests = computed(() => {
  return mentorStore.receivedBookings?.filter(b => b.status === 'pending') || [];
});
const pendingCount = computed(() => pendingRequests.value.length);

async function handleBookingStatus(bookingId, status) {
  if(!confirm(`${status === 'approved' ? '수락' : '거절'} 하시겠습니까?`)) return;
  try {
    // 멘토 스토어 액션 혹은 API 직접 호출
    await axios.put(`http://localhost:8000/api/bookings/${bookingId}/status`, { status });
    await mentorStore.fetchReceivedBookings();
  } catch (e) {
    alert('처리 실패');
  }
}

// --- 이벤트 핸들러 ---
function handleNodeClick(event) {
  // VueFlow 이벤트 객체 구조에 따라 node 접근
  const node = event.node || event; 
  if (node.id === 'me') return;
  selectedMentor.value = node.data;
}

function handleTopMentorClick(mentor) {
  selectedMentor.value = mentor;
}

function closeSidebar() {
  selectedMentor.value = null;
}

function handleSelectRoom(room) {
  selectedChatRoom.value = room;
}

// 유틸리티
function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return `${d.getMonth()+1}/${d.getDate()}`;
}
function formatSchedule(start, end) {
  if (!start) return '-';
  const d = new Date(start);
  return `${d.getMonth()+1}/${d.getDate()} ${d.toLocaleTimeString('ko-KR', {hour:'2-digit', minute:'2-digit', hour12:false})}`;
}
</script>

<style scoped>
/* 기존 스타일 유지 + 필요한 부분 추가 */
.network-view-container {
  display: flex;
  width: 100%;
  height: calc(100vh - 80px);
  position: relative;
  flex-direction: column;
  background-color: #f9fafb;
}

.view-switcher {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  padding: 0 20px;
}
.view-switcher button {
  padding: 15px 20px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 15px;
  font-weight: 500;
  color: #6b7280;
  border-bottom: 2px solid transparent;
  display: flex;
  align-items: center;
  gap: 6px;
}
.view-switcher button.active {
  border-bottom: 2px solid #6d28d9;
  color: #6d28d9;
  font-weight: 700;
}
.badge {
  background-color: #ef4444;
  color: white;
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
}

.graph-panel-wrapper { flex: 1; position: relative; overflow: hidden; }
.graph-panel { width: 100%; height: 100%; }

.loading-overlay {
  position: absolute; inset: 0;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  background: rgba(255,255,255,0.9); z-index: 20;
}
.spinner {
  width: 40px; height: 40px;
  border: 4px solid #f3f3f3; border-top: 4px solid #6d28d9;
  border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 10px;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.top-mentors-floating {
  position: absolute; top: 20px; right: 20px; z-index: 5;
  width: 280px; max-height: 80%;
}

.management-panel { flex: 1; padding: 30px; overflow-y: auto; max-width: 900px; margin: 0 auto; width: 100%; }
.manage-section { margin-bottom: 40px; }
.chat-list { display: flex; flex-direction: column; gap: 15px; }
.chat-card {
  background: white; border-radius: 12px; padding: 20px;
  border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.request-card { border-left: 4px solid #f59e0b; }
.chat-top { display: flex; justify-content: space-between; margin-bottom: 10px; }
.mentee-name { font-weight: bold; color: #374151; }
.action-buttons { display: flex; gap: 10px; margin-top: 15px; justify-content: flex-end; }
.btn-approve { padding: 8px 16px; background: #6d28d9; color: white; border: none; border-radius: 6px; cursor: pointer; }
.btn-reject { padding: 8px 16px; background: white; border: 1px solid #d1d5db; color: #4b5563; border-radius: 6px; cursor: pointer; }

.chat-view-wrapper { flex: 1; height: 100%; padding: 20px; min-height: 0; }
.chat-layout { display: grid; grid-template-columns: 320px 1fr; height: 100%; border: 1px solid #e5e7eb; border-radius: 12px; background: white; overflow: hidden; }
.chat-room-list { height: 100%; min-height: 0; }
.chat-room { height: 100%; min-height: 0; display: flex; flex-direction: column; }

.sidebar-panel {
  position: absolute; top: 0; right: 0; bottom: 0; width: 320px;
  background: white; border-left: 1px solid #e5e7eb; z-index: 10;
  box-shadow: -4px 0 15px rgba(0,0,0,0.05);
}
</style>