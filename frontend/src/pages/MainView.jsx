// frontend/src/pages/MainView.jsx

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge } from 'reactflow';

// ReactFlow에 필요한 CSS
import 'reactflow/dist/style.css';

// 28단계에서 만든 커스텀 컴포넌트 임포트 (파일 경로 확인!)
import MentorNode from '../components/MentorNode.jsx';
import MenteeNode from '../components/MenteeNode.jsx';
import ConnectionLine from '../components/ConnectionLine.jsx';

// MainView가 임시로 사용하는 파일 (경로 확인!)
import { fetchNetworkData } from '../api/networkApi.js';
import { useAuth } from '../hooks/useAuth.js';

// ReactFlow 커스텀 노드 타입 정의
const nodeTypes = {
  mentor: MentorNode,
  mentee: MenteeNode,
};

function MainView({ mentors: mentorsFromApp }) { // App.jsx로부터 mentors 데이터를 prop으로 받음
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedMentor, setSelectedMentor] = useState(null); // 선택된 멘토 정보 저장 state

  // App.jsx로부터 받은 mentors 데이터가 변경될 때마다 노드와 엣지를 다시 계산
  useEffect(() => {
    console.log('[MainView]가 멘토 데이터를 받았습니다:', mentorsFromApp);

    if (!mentorsFromApp || mentorsFromApp.length === 0) {
      // 멘토 데이터가 없으면 기본 멘티 노드만 표시
      setNodes([{ id: 'mentee-main', type: 'mentee', data: { label: '김멘티 (나)' }, position: { x: 0, y: 0 } }]);
      setEdges([]);
      return;
    }

    // 1. 멘티 노드 생성 (고정)
    const menteeNode = {
      id: 'mentee-main',
      type: 'mentee',
      data: { label: '김멘티 (나)' },
      position: { x: 250, y: 50 }, // 중앙 상단 위치
    };

    // 2. App.jsx에서 받은 멘토 데이터로 멘토 노드 생성
    const mentorNodes = mentorsFromApp.map((mentor, index) => ({
      id: mentor.id, // Supabase DB의 멘토 ID 사용
      type: 'mentor',
      data: {
        label: mentor.full_name, // 멘토 이름
        // (WBS 5.3)[cite: wbs.md] 사이드바에 표시할 추가 정보
        similarity: mentor.similarity, // AI 유사도 점수
        career_info: mentor.career_info, // 경력 요약 (DB에 추가 필요)
      },
      // 노드 위치를 원형으로 배치 (간단한 예시)
      position: {
        x: 250 + Math.cos((index / mentorsFromApp.length) * 2 * Math.PI) * 200,
        y: 250 + Math.sin((index / mentorsFromApp.length) * 2 * Math.PI) * 200,
      },
    }));

    // 3. 멘티와 각 멘토를 연결하는 엣지 생성
    const mentorEdges = mentorsFromApp.map(mentor => ({
      id: `e-${menteeNode.id}-${mentor.id}`,
      source: menteeNode.id, // 시작: 멘티 노드
      target: mentor.id,     // 끝: 멘토 노드
      // (선택) 엣지에 유사도 표시
      // label: `${(mentor.similarity * 100).toFixed(1)}%`,
      animated: mentor.similarity > 0.8 // 유사도 높으면 애니메이션 효과 (예시)
    }));

    // 4. 계산된 노드와 엣지로 state 업데이트
    setNodes([menteeNode, ...mentorNodes]);
    setEdges(mentorEdges);

  }, [mentorsFromApp, setNodes, setEdges]); // mentorsFromApp이 바뀔 때마다 이 useEffect 실행


  // 노드 클릭 이벤트 핸들러 (WBS 5.3)[cite: wbs.md]
  const onNodeClick = useCallback((event, node) => {
    console.log('클릭된 노드:', node);
    if (node.type === 'mentor') {
      // 클릭된 노드가 멘토 타입이면, 해당 멘토 정보를 state에 저장
      setSelectedMentor(node.data);
    } else {
      setSelectedMentor(null); // 멘티나 빈 공간 클릭 시 사이드바 숨김
    }
  }, []);

  return (
    // 전체 화면을 차지하도록 div 설정
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      {/* ReactFlow 캔버스 영역 */}
      <div style={{ flexGrow: 1, height: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange} // 노드 이동/삭제 등 변경 처리
          onEdgesChange={onEdgesChange} // 엣지 변경 처리
          onNodeClick={onNodeClick} // 노드 클릭 이벤트 연결
          nodeTypes={nodeTypes} // 커스텀 노드 타입 적용
          connectionLineComponent={ConnectionLine} // 커스텀 연결선 적용
          fitView // 모든 노드가 보이도록 자동 줌 조절
        >
          <Controls /> {/* 줌인/아웃 컨트롤 */}
          <MiniMap />  {/* 미니맵 */}
          <Background variant="dots" gap={12} size={1} /> {/* 배경 */}
        </ReactFlow>
      </div>

      {/* 멘토 상세 정보 사이드바 (WBS 5.3)[cite: wbs.md] */}
      {selectedMentor && ( // selectedMentor가 있을 때만 사이드바 표시
        <div style={{
          width: '300px',
          height: '100%',
          padding: '20px',
          borderLeft: '1px solid #eee',
          background: '#f9f9f9',
          boxSizing: 'border-box' // 패딩 포함 크기 계산
        }}>
          <h2>{selectedMentor.label} (멘토)</h2>
          <p>
            <strong>매칭 점수:</strong>
            {/* AI 유사도를 퍼센트로 표시 */}
            {selectedMentor.similarity ? `${(selectedMentor.similarity * 100).toFixed(1)}%` : 'N/A'}
          </p>
          <p>
            <strong>추천 이유:</strong> <br />
            {/* (임시 텍스트 - 나중에 OpenAI API 연동) [cite: wbs.md] */}
            AI 기반 경력/관심사 일치율 분석
          </p>
          <p>
            <strong>경력 요약:</strong> <br />
            {/* (임시 텍스트 - 실제 career_info 표시 필요) */}
            {selectedMentor.career_info || '삼성전자 5년 (데이터 분석), 네이버 (AI 모델링)'}
          </p>
          <button style={{ marginTop: '20px', padding: '8px 12px' }}>
            커피챗 신청하기
          </button>
        </div>
      )}
    </div>
  );
}

export default MainView;