// frontend/src/components/MenteeNode.jsx
// (MainView.jsx[cite: frontend/src/pages/MainView.jsx]가 import하는 커스텀 멘티 노드)

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

export default memo(({ data, isConnectable }) => {
  return (
    <div style={{
      padding: '12px 25px',
      border: '2px solid #0041d0', // 멘티(나)는 파란색 테두리
      borderRadius: '5px',
      background: '#f0f4ff', // 멘티(나)는 파란색 배경
      fontFamily: 'Arial, sans-serif',
      fontSize: '16px',
      fontWeight: 'bold',
    }}>
      {/* 멘티는 'source' (나가는) 연결점만 가집니다 (하단) */}
      <div>
        {data.label}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        style={{ background: '#0041d0', width: 8, height: 8 }}
      />
    </div>
  );
});