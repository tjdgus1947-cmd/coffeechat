// frontend/src/components/ConnectionLine.jsx
// (MainView.jsx[cite: frontend/src/pages/MainView.jsx]가 import하는 커스텀 연결선 스타일)

import React from 'react';

export default ({
  fromX,
  fromY,
  toX,
  toY,
}) => {
  // SVG 경로(path)를 사용하여 꺾이는 선을 그립니다.
  const path = `M${fromX},${fromY} C${fromX},${(fromY + toY) / 2} ${toX},${(fromY + toY) / 2} ${toX},${toY}`;

  return (
    <g>
      <path
        fill="none"
        stroke="#555"
        strokeWidth={1.5}
        className="react-flow__connection-path"
        d={path}
      />
    </g>
  );
};