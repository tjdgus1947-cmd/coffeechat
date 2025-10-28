import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { networkAPI, mentorsAPI } from '../services/api';

// 노드 스타일 계산
const getNodeStyle = (chatHistory, isTag = false, weight = 1) => {
  if (isTag) {
    return {
      background: 'white',
      border: `${2 + weight * 2}px solid #6366f1`,
      borderRadius: '8px',
      padding: '12px 20px',
      fontSize: '13px',
      fontWeight: weight > 2 ? 'bold' : 'normal',
      opacity: 0.6 + (weight * 0.1),
    };
  }
  
  const opacity = chatHistory > 0 ? 0.9 : 0.6;
  const scale = 1 + (chatHistory * 0.15);
  
  return {
    background: chatHistory > 0 ? '#10b981' : '#94a3b8',
    border: '2px solid white',
    borderRadius: '50%',
    width: `${60 * scale}px`,
    height: `${60 * scale}px`,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'white',
    fontWeight: 'bold',
    fontSize: '14px',
    opacity: opacity,
    boxShadow: chatHistory > 0 ? '0 4px 12px rgba(16, 185, 129, 0.4)' : 'none',
  };
};

// 네트워크 그래프 노드/엣지 생성
const generateNetworkNodes = (networkData) => {
  if (!networkData) return { nodes: [], edges: [] };
  
  const nodes = [];
  const edges = [];
  
  // 중앙 멘티 노드
  nodes.push({
    id: 'mentee-center',
    type: 'default',
    position: { x: 400, y: 300 },
    data: { 
      label: (
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '16px', fontWeight: 'bold' }}>👤</div>
          <div style={{ fontSize: '12px', marginTop: '4px' }}>{networkData.mentee.name}</div>
        </div>
      ) 
    },
    style: {
      background: '#6366f1',
      border: '3px solid white',
      borderRadius: '50%',
      width: '100px',
      height: '100px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontWeight: 'bold',
      boxShadow: '0 8px 24px rgba(99, 102, 241, 0.5)',
    },
    draggable: false,
  });

  // 태그 노드들
  const tagNodes = networkData.nodes.filter(n => n.type === 'tag');
  tagNodes.forEach((tagNode, idx) => {
    const angle = (idx / tagNodes.length) * 2 * Math.PI;
    const radius = 200;
    const x = 400 + radius * Math.cos(angle);
    const y = 300 + radius * Math.sin(angle);
    
    nodes.push({
      id: tagNode.id,
      type: 'default',
      position: { x, y },
      data: { label: tagNode.label },
      style: getNodeStyle(0, true, tagNode.weight),
    });
  });

  // 멘토 노드들
  const mentorNodes = networkData.nodes.filter(n => n.type === 'mentor');
  mentorNodes.forEach((mentorNode, idx) => {
    const angle = (idx / mentorNodes.length) * 2 * Math.PI + Math.PI / 6;
    const radius = 350;
    const x = 400 + radius * Math.cos(angle);
    const y = 300 + radius * Math.sin(angle);

    nodes.push({
      id: mentorNode.id,
      type: 'default',
      position: { x, y },
      data: { 
        label: (
          <div style={{ textAlign: 'center', fontSize: '11px' }}>
            <div>{mentorNode.data.name}</div>
            <div style={{ fontSize: '9px', opacity: 0.8 }}>{mentorNode.data.company}</div>
            <div style={{ fontSize: '9px', color: '#fff', marginTop: '2px' }}>
              {mentorNode.data.match_score}%
            </div>
          </div>
        ),
        ...mentorNode.data
      },
      style: getNodeStyle(mentorNode.data.chat_history),
    });
  });

  // 엣지 생성
  networkData.edges.forEach(edge => {
    if (edge.type === 'interest') {
      edges.push({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: true,
        style: { stroke: '#6366f1', strokeWidth: 2 },
      });
    } else if (edge.type === 'connection') {
      edges.push({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        animated: edge.animated,
        style: { 
          stroke: edge.animated ? '#10b981' : '#cbd5e1',
          strokeWidth: edge.animated ? 3 : 1,
        },
      });
    } else if (edge.type === 'expertise') {
      edges.push({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        style: { 
          stroke: '#94a3b8',
          strokeWidth: 1,
          opacity: 0.3,
        },
      });
    }
  });

  return { nodes, edges };
};

const MainView = () => {
  const [networkData, setNetworkData] = useState(null);
  const [mentors, setMentors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMentor, setSelectedMentor] = useState(null);
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // 데이터 로딩
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 네트워크 데이터 로딩
        const networkResponse = await networkAPI.getData('mentee-1');
        setNetworkData(networkResponse.data);
        
        // 네트워크 그래프 생성
        const { nodes: newNodes, edges: newEdges } = generateNetworkNodes(networkResponse.data);
        setNodes(newNodes);
        setEdges(newEdges);
        
        // 멘토 리스트 로딩
        const mentorsResponse = await mentorsAPI.getRecommended('mentee-1', 10);
        setMentors(mentorsResponse.data.mentors || []);
        
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [setNodes, setEdges]);

  const onNodeClick = useCallback((event, node) => {
    if (node.data && node.data.company) {
      setSelectedMentor(node.data);
    }
  }, []);

  if (loading) {
    return (
      <div className="w-full h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="text-6xl mb-4">⏳</div>
          <div className="text-xl font-semibold text-slate-700">로딩 중...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-screen bg-slate-50 flex flex-col">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">커피챗 네트워크</h1>
            <p className="text-sm text-slate-500 mt-1">AI 기반 멘토 매칭 플랫폼 (데모)</p>
          </div>
          
          <div className="flex gap-2 bg-slate-100 rounded-lg p-1">
            <button className="px-6 py-2 rounded-md font-medium bg-white text-slate-800 shadow-sm">
              🔗 네트워크
            </button>
            <button className="px-6 py-2 rounded-md font-medium text-slate-600 hover:text-slate-800" disabled>
              📍 지도 (준비 중)
            </button>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 */}
      <div className="flex-1 flex gap-4 p-4">
        {/* 네트워크 그래프 */}
        <div className="flex-1 bg-white rounded-lg shadow-sm overflow-hidden">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            className="bg-slate-50"
          >
            <Background color="#e2e8f0" gap={16} />
            <Controls />
            <MiniMap 
              nodeColor={(node) => {
                if (node.id === 'mentee-center') return '#6366f1';
                if (node.id.startsWith('tag-')) return '#cbd5e1';
                return node.style?.background || '#94a3b8';
              }}
              maskColor="rgba(0, 0, 0, 0.1)"
            />
            <Panel position="top-left" className="bg-white rounded-lg shadow-md p-4 m-2">
              <div className="text-xs space-y-2">
                <div className="font-bold text-slate-700 mb-2">범례</div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-indigo-500 rounded-full"></div>
                  <span>나 (멘티)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-emerald-500 rounded-full"></div>
                  <span>커피챗 경험 멘토</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 bg-slate-400 rounded-full"></div>
                  <span>추천 멘토</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-indigo-500 rounded"></div>
                  <span>관심 분야 태그</span>
                </div>
              </div>
            </Panel>
          </ReactFlow>
        </div>

        {/* 사이드바 - 멘토 상세 정보 */}
        <div className="w-96 bg-white rounded-lg shadow-sm p-6 overflow-y-auto">
          {selectedMentor ? (
            <div className="space-y-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white text-2xl font-bold ${
                    selectedMentor.chat_history > 0 ? 'bg-emerald-500' : 'bg-slate-400'
                  }`}>
                    {selectedMentor.name[0]}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">{selectedMentor.name}</h2>
                    <p className="text-sm text-slate-500">{selectedMentor.field}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedMentor(null)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  ✕
                </button>
              </div>

              {/* 매칭도 표시 */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-slate-700">AI 매칭도</span>
                  <span className="text-2xl font-bold text-indigo-600">{selectedMentor.match_score}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div
                    className="bg-indigo-600 h-2 rounded-full transition-all"
                    style={{ width: `${selectedMentor.match_score}%` }}
                  ></div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase mb-2">소속</div>
                  <div className="text-sm text-slate-700">{selectedMentor.company}</div>
                  <div className="text-sm text-slate-500">{selectedMentor.position}</div>
                </div>

                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase mb-2">경력</div>
                  <div className="text-sm text-slate-700">{selectedMentor.years_of_experience}년</div>
                </div>

                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase mb-2">전문 분야</div>
                  <div className="flex flex-wrap gap-2">
                    {selectedMentor.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase mb-2">거리</div>
                  <div className="text-sm text-slate-700">📍 약 {selectedMentor.distance}km</div>
                </div>

                <div>
                  <div className="text-xs font-semibold text-slate-500 uppercase mb-2">경력 요약</div>
                  <div className="text-sm text-slate-700 leading-relaxed">{selectedMentor.career_summary}</div>
                </div>

                {selectedMentor.chat_history > 0 && (
                  <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
                    <div className="text-sm font-semibold text-emerald-800 mb-1">
                      🎉 커피챗 이력
                    </div>
                    <div className="text-xs text-emerald-700">
                      총 {selectedMentor.chat_history}회 만남
                    </div>
                  </div>
                )}
              </div>

              <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 rounded-lg transition">
                📅 커피챗 예약하기
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-center text-slate-400">
              <div className="text-6xl mb-4">🔍</div>
              <div className="text-lg font-semibold">멘토를 선택해주세요</div>
              <div className="text-sm mt-2">노드를 클릭하면 상세 정보를 볼 수 있습니다</div>
              
              {/* 추천 멘토 리스트 */}
              <div className="w-full mt-8">
                <div className="text-left text-sm font-semibold text-slate-700 mb-3">추천 멘토</div>
                <div className="space-y-2">
                  {mentors.slice(0, 5).map(mentor => (
                    <button
                      key={mentor.id}
                      onClick={() => setSelectedMentor(mentor)}
                      className="w-full text-left p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                          mentor.chat_history > 0 ? 'bg-emerald-500' : 'bg-slate-400'
                        }`}>
                          {mentor.name[0]}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="font-semibold text-sm text-slate-800">{mentor.name}</div>
                          <div className="text-xs text-slate-500 truncate">{mentor.company}</div>
                        </div>
                        <div className="text-sm font-semibold text-indigo-600">{mentor.match_score}%</div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 하단 통계 */}
      <div className="bg-white border-t border-slate-200 px-6 py-4">
        <div className="flex items-center justify-between text-sm">
          <div className="flex gap-6">
            <div>
              <span className="text-slate-500">총 멘토:</span>
              <span className="font-semibold text-slate-800 ml-2">{mentors.length}명</span>
            </div>
            <div>
              <span className="text-slate-500">커피챗 경험:</span>
              <span className="font-semibold text-emerald-600 ml-2">
                {mentors.filter(m => m.chat_history > 0).length}명
              </span>
            </div>
            <div>
              <span className="text-slate-500">평균 매칭도:</span>
              <span className="font-semibold text-indigo-600 ml-2">
                {mentors.length > 0 ? Math.round(mentors.reduce((acc, m) => acc + m.match_score, 0) / mentors.length) : 0}%
              </span>
            </div>
          </div>
          <div className="text-slate-400">
            데모 모드 | AI 매칭 엔진 v1.0
          </div>
        </div>
      </div>
    </div>
  );
};

export default MainView;