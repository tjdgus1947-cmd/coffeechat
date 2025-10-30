// frontend/src/components/MentorNode.jsx
// (MainView.jsx[cite: frontend/src/pages/MainView.jsx]가 import하는 커스텀 멘토 노드)

import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

// React.memo를 사용해 불필요한 리렌더링을 방지합니다.
export default memo(({ data, isConnectable }) => {
  return (
    <div style={{
      padding: '10px 20px',
      border: '1px solid #1a192b',
      borderRadius: '3px',
      background: '#fff',
      fontFamily: 'Arial, sans-serif',
      fontSize: '14px',
    }}>
      {/* Handle: 노드를 연결하는 "점"입니다.
        - type="target": 이 노드로 들어오는 연결점 (상단)
        - type="source": 이 노드에서 나가는 연결점 (하단)
      */}
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
        style={{ background: '#555' }}
      />
      <div>
        {data.label}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
        style={{ background: '#555' }}
      />
    </div>
  );
});
