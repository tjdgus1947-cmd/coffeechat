<!-- NetworkGraph.vue (커피챗 테마 버전) -->

<template>
  <VueFlow
    :nodes="enhancedNodes"
    :edges="enhancedEdges"
    :nodes-draggable="true"
    :min-zoom="0.3"
    @node-click="onNodeClick"
    @pane-ready="onPaneReady"
    class="network-graph"
  >
    <Background />
    <Controls position="top-left" />
    <MiniMap class="graph-minimap" />
  </VueFlow>
</template>

<script setup>
import { computed } from 'vue';
import { VueFlow, useVueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';

import '@vue-flow/core/dist/style.css';
import '@vue-flow/core/dist/theme-default.css';
import '@vue-flow/controls/dist/style.css';
import '@vue-flow/minimap/dist/style.css';

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

const emit = defineEmits(['node-click']);

// 노드에 선택 상태와 찜 상태를 반영
const enhancedNodes = computed(() => {
  return props.nodes.map(node => {
    if (node.data?.type === 'mentor') {
      const isLiked = node.data?.isLiked;
      
      return {
        ...node,
        style: {
          background: isLiked
            ? 'linear-gradient(135deg, #d4a574 0%, #c9956f 100%)'
            : 'linear-gradient(135deg, #a8846f 0%, #9a7967 100%)',
          border: '3px solid #fff5e6',
          boxShadow: isLiked
            ? '0 0 0 3px #d4a574, 0 8px 24px rgba(212, 165, 116, 0.35)'
            : '0 8px 24px rgba(152, 121, 103, 0.2)',
          transition: 'all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
          cursor: 'pointer',
          width: '90px',
          height: '90px',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '13px',
          fontWeight: 'bold',
          color: '#fff5e6',
          textAlign: 'center',
          padding: '8px'
        }
      };
    }
    
    // 멘티 노드 (중앙)
    return {
      ...node,
      style: {
        background: 'linear-gradient(135deg, #6f5a47 0%, #5d4a3a 100%)',
        border: '4px solid #fff5e6',
        boxShadow: '0 0 0 3px #6f5a47, 0 12px 32px rgba(95, 74, 58, 0.4)',
        width: '100px',
        height: '100px',
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '14px',
        fontWeight: 'bold',
        color: '#fff5e6',
        textAlign: 'center',
        padding: '8px'
      }
    };
  });
});

// 엣지를 직선으로 변경 (커피 테마 색상)
const enhancedEdges = computed(() => {
  return props.edges.map(edge => ({
    ...edge,
    animated: false,
    style: {
      stroke: '#d9c9b8',
      strokeWidth: 2,
      strokeDasharray: 'none'
    },
    type: 'straight'
  }));
});

// 처음 그릴 때 노드가 가장자리에 붙지 않도록 여백을 두고 화면에 맞춘다
const onPaneReady = (instance) => {
  requestAnimationFrame(() => instance.fitView({ padding: 0.2 }));
};

const onNodeClick = (event) => {
  emit('node-click', event.node);
};
</script>

<style scoped>
.network-graph {
  width: 100%;
  height: 100%;
  background: #f4e2ce 
}

/* VueFlow 커스터마이징 */
:deep(.vue-flow) {
  background: linear-gradient(135deg, #fef8f3 0%, #fef5ee 100%);
}

:deep(.vue-flow__minimap) {
  background-color: #fff5e6;
  border: 2px solid #e8d7c3;
  border-radius: 12px;
}

:deep(.vue-flow__controls) {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  background: white;
  border: 1px solid #e8d7c3;
}

:deep(.vue-flow__controls button) {
  border: 1px solid #e8d7c3;
  color: #6f5a47;
}

:deep(.vue-flow__controls button:hover) {
  background-color: #fef5ee;
  border-color: #a8846f;
}

/* 좁은 화면에서는 미니맵이 그래프를 가리므로 숨김 */
@media (max-width: 768px) {
  :deep(.graph-minimap) { display: none; }
}

/* 노드 선택 상태 */
:deep(.vue-flow__node.selected) {
  filter: drop-shadow(0 0 0 4px rgba(212, 165, 116, 0.2));
}
</style>