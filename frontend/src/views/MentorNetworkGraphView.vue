<template>
  <div class="network-graph-wrapper">
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
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { VueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';

import { getMentorNetwork } from '@/services/mentorNetworkService';
import { useAuthStore } from '@/store/auth';

const nodes = ref([]);
const edges = ref([]);

const authStore = useAuthStore();
const mentorId = authStore.userId; // 실제 로그인된 멘토 ID

onMounted(async () => {
  try {
    const res = await getMentorNetwork(mentorId);

    if (res?.center_mentor) {
      nodes.value = [res.center_mentor];
    } else {
      nodes.value = [];
    }

    edges.value = res?.similar_mentors || [];
  } catch (err) {
    console.error('[NetworkGraph] API Error:', err);
  }
});
</script>

<style scoped>
.network-graph-wrapper {
  width: 100%;
  height: 90vh;
  background: #fafafa;
}
</style>
