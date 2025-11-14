<template>
  <VueFlow
    :nodes="nodes"
    :edges="edgesWithStroke"
    :fit-view-on-init="true"
    :nodes-draggable="true"
    @node-click="onNodeClick"
    class="network-graph"
  >
    <Background />
    <Controls />
    <MiniMap />
  </VueFlow>
</template>

<script setup>
// 1. VueFlow 핵심 기능 임포트
import { VueFlow, useVueFlow } from '@vue-flow/core'; 
// 2. 부가 기능 (배경, 컨트롤, 미니맵) 임포트
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';

// 3. VueFlow 기본 스타일 임포트
import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css'; // 기본 테마

// 4. 부모(NetworkView)로부터 nodes와 edges 데이터를 받음
const props = defineProps({
  nodes: {
    type: Array,
    required: true,
  },
  edges: {
    type: Array,
    required: true,
  },
});

// 6. edge의 굵기(strokeWidth)를 data에서 style로 반영 (실선)
import { computed } from 'vue';
const edgesWithStroke = computed(() => {
  return props.edges.map(edge => {
    const strokeWidth = edge.data?.strokeWidth || 2;
    return {
      ...edge,
      style: {
        ...(edge.style || {}),
        strokeWidth,
        strokeDasharray: '0', // 실선
      }
    };
  });
});

// 5. 노드 클릭 시 부모에게 이벤트를 전달
const emit = defineEmits(['node-click']);

const onNodeClick = (event) => {
  // 클릭된 노드의 정보를 부모 컴포넌트로 전달
  emit('node-click', event.node);
};
</script>

<style scoped>
/* 그래프 컴포넌트가 부모 요소(NetworkView)의 크기를 꽉 채우도록 설정 */
.network-graph {
  width: 100%; /* 부모에서 2/3로 제한하므로 내부는 100% 유지 */
  height: 100%;
}
</style>