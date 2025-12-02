<template>
  <div class="network-graph-view">
    <div class="network-header">
      <h2>멘토 네트워크</h2>
      <p class="desc">
        내 AI 자기소개 임베딩을 기준으로, 나와 유사도가 높은 멘토들을 네트워크 형태로 보여줍니다.
      </p>
    </div>

    <div v-if="loading" class="state-box">
      <p>멘토 네트워크 데이터를 불러오는 중입니다...</p>
    </div>

    <div v-else-if="errorMessage" class="state-box error">
      <p>{{ errorMessage }}</p>
    </div>

    <div v-else-if="nodes.length === 0" class="state-box">
      <p>표시할 멘토 네트워크 데이터가 없습니다.</p>
      <p class="hint">멘토 프로필과 AI 자기소개를 먼저 작성해 주세요.</p>
    </div>

    <div v-else class="graph-card">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :fit-view-on-init="true"
        class="mentor-network-graph"
      >
        <Background />
        <Controls />
        <MiniMap />
      </VueFlow>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { VueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';

import { useAuthStore } from '@/store/auth';
import { getMentorNetwork } from '@/services/mentorNetworkService';

const authStore = useAuthStore();

const nodes = ref([]);
const edges = ref([]);
const loading = ref(true);
const errorMessage = ref('');

// authStore 구조가 userId 또는 user.id 중 어떤 것을 쓰는지 모를 수 있어 양쪽 다 대응
const mentorId = computed(() => {
  return authStore.userId || authStore.user?.id || null;
});

onMounted(async () => {
  try {
    if (!mentorId.value) {
      errorMessage.value = '로그인된 멘토 정보를 확인할 수 없습니다.';
      loading.value = false;
      return;
    }

    const data = await getMentorNetwork(mentorId.value);

    if (!data || !data.center_mentor) {
      errorMessage.value = '멘토 네트워크 데이터를 불러오지 못했습니다.';
      loading.value = false;
      return;
    }

    buildGraph(data);
  } catch (err) {
    console.error('[MentorNetworkGraphView] 네트워크 조회 실패:', err);
    errorMessage.value = '멘토 네트워크 조회 중 오류가 발생했습니다.';
  } finally {
    loading.value = false;
  }
});

/**
 * 백엔드 응답을 VueFlow 노드/엣지 구조로 변환
 * 기대 형식:
 * {
 *   center_mentor: { id, career_info, ... },
 *   similar_mentors: [
 *     { mentor_id, similarity, career_info, ... },
 *     ...
 *   ]
 * }
 */
function buildGraph(data) {
  const center = data.center_mentor;
  const similars = data.similar_mentors || data.similarMentors || [];

  const newNodes = [];
  const newEdges = [];

  // 중심 멘토 노드
  const centerId = `mentor-${center.id ?? 'center'}`;

  newNodes.push({
    id: centerId,
    position: { x: 0, y: 0 },
    data: {
      label: center.full_name || center.name || '나',
      sub: trimCareer(center.career_info),
      isCenter: true,
    },
    style: {
      padding: '12px 16px',
      borderRadius: '999px',
      border: '2px solid #6d28d9',
      background: '#f5f3ff',
      color: '#111827',
      fontWeight: 700,
      boxShadow: '0 4px 10px rgba(0,0,0,0.08)',
      minWidth: '140px',
      textAlign: 'center',
    },
  });

  if (!similars || similars.length === 0) {
    nodes.value = newNodes;
    edges.value = newEdges;
    return;
  }

  // 원형 레이아웃으로 주변 멘토 배치
  const radius = 220;
  const count = similars.length;
  const step = (2 * Math.PI) / count;

  similars.forEach((m, index) => {
    const angle = index * step;
    const x = radius * Math.cos(angle);
    const y = radius * Math.sin(angle);

    const nodeId = `mentor-${m.mentor_id ?? m.id ?? index}`;

    newNodes.push({
      id: nodeId,
      position: { x, y },
      data: {
        label: m.name || m.full_name || `멘토 ${index + 1}`,
        sub: trimCareer(m.career_info),
        similarity: m.similarity,
      },
      style: {
        padding: '10px 14px',
        borderRadius: '999px',
        border: '1px solid #e5e7eb',
        background: '#ffffff',
        fontSize: '13px',
        boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
        maxWidth: '220px',
        textAlign: 'center',
      },
    });

    newEdges.push({
      id: `edge-${centerId}-${nodeId}`,
      source: centerId,
      target: nodeId,
      label:
        typeof m.similarity === 'number'
          ? (m.similarity * 100).toFixed(0) + '%'
          : '',
      animated: true,
      style: {
        strokeWidth: 1.5,
      },
      labelBgPadding: [4, 2],
      labelBgBorderRadius: 4,
    });
  });

  nodes.value = newNodes;
  edges.value = newEdges;
}

function trimCareer(text) {
  if (!text || typeof text !== 'string') return '';
  if (text.length <= 40) return text;
  return text.slice(0, 40) + '…';
}
</script>

<style scoped>
.network-graph-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px); /* 상단 탭/네비게이션 높이 감안한 여유값 */
  padding: 24px 40px;
  box-sizing: border-box;
  background-color: #f9fafb;
}

.network-header {
  margin-bottom: 16px;
}

.network-header h2 {
  margin: 0 0 4px 0;
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.network-header .desc {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.state-box {
  margin-top: 24px;
  padding: 24px;
  border-radius: 16px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  text-align: center;
  color: #4b5563;
  font-size: 14px;
}

.state-box.error {
  border-color: #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.state-box .hint {
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.graph-card {
  margin-top: 16px;
  flex: 1;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  overflow: hidden;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
}

.mentor-network-graph {
  width: 100%;
  height: 100%;
}

/* 반응형 */
@media (max-width: 768px) {
  .network-graph-view {
    padding: 16px;
  }
}
</style>
