    // frontend/src/utils/mockData.js

    // ReactFlow에 사용할 테스트용 목업 데이터입니다.
    // 실제 데이터는 App.jsx에서 Prop으로 받습니다.
    export const mockNetworkData = {
        // 멘토/멘티 노드 (테스트용)
        nodes: [
            { id: 'mentee-1', data: { label: '김멘티 (나)' }, role: 'mentee', position: { x: 0, y: 0 } },
            { id: 'mentor-1', data: { label: '이멘토' }, role: 'mentor', position: { x: 100, y: 100 } },
            { id: 'mentor-2', data: { label: '박멘토' }, role: 'mentor', position: { x: 400, y: 100 } },
        ],
        // 연결선 (테스트용)
        edges: [
            { id: 'e1-1', source: 'mentee-1', target: 'mentor-1', data: { similarity: 0.85 } },
            { id: 'e1-2', source: 'mentee-1', target: 'mentor-2', data: { similarity: 0.72 } },
        ],
    };