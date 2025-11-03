// frontend/src/store/network.js
// (최종 수정본: MOCK_DATA 끄기 + API 주소 수정 + 데이터 파싱 추가)

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import api from '@/services/api';

// 1. ⭐️ (수정) MOCK_DATA 스위치를 false로 변경 ⭐️
const MOCK_DATA = false;

// 5. ⭐️ (신규) career_info 텍스트를 파싱하는 헬퍼 함수
function parseCareerInfo(text) {
  if (!text) return { company: '정보 없음', team: '정보 없음', experienceYears: '0', topics: '', introduction: '정보 없음' };

  try {
    // "회사: 삼성전자, 직무: 보안팀, 경력: 2년, 전문분야: 보안, IT, 소개: 보안의 신"
    const info = {
      company: text.match(/회사:\s*([^,]+)/)?.[1]?.trim() || '정보 없음',
      team: text.match(/직무:\s*([^,]+)/)?.[1]?.trim() || '정보 없음',
      experienceYears: text.match(/경력:\s*(\d+)\s*년/)?.[1] || '0',
      topics: text.match(/전문분야:\s*([^,]+)/)?.[1]?.trim() || '',
      introduction: text.match(/소개:\s*(.*)/)?.[1]?.trim() || text,
    };
    return info;
  } catch(e) {
    console.error("career_info 파싱 실패:", e);
    // 파싱 실패 시 원본 텍스트 반환
    return { company: '정보 없음', team: '정보 없음', experienceYears: '0', topics: '', introduction: text };
  }
}


export const useNetworkStore = defineStore('network', () => {
  // --- State ---
  const nodes = ref([]);
  const edges = ref([]);
  const isLoading = ref(false); 

  // --- Actions ---
  async function fetchNetworkData() {
    const authStore = useAuthStore();
    
    // 2. ⭐️ (수정) 멘티 ID(auth.userId)가 있는지 확인
    if (!authStore.userId) {
      console.log('네트워크 데이터 로드 중단: 사용자 ID 없음 (로그인 필요)');
      return;
    }

    isLoading.value = true;
    
    if (MOCK_DATA) {
      // (이 부분은 이제 실행되지 않음)
      console.warn('!!! MOCK DATA (Network) 활성 상태 !!!');
      setMockData(); 
      isLoading.value = false;
    } 
    else {
      try {
        // 3. ⭐️ (수정) 님의 실제 AI 매칭 API 호출 (/api prefix 추가)
        const response = await api.get(`/mentors/recommended/${authStore.userId}`);
        
        const recommendedMentors = response.data; 
        
        // 4.1. 멘티 노드 (중앙)
        const menteeNode = {
          id: 'mentee-main',
          type: 'input',
          label: authStore.user?.full_name || '김성현 (나)',
          position: { x: 400, y: 300 },
          data: { type: 'mentee' },
          style: { background: '#6d28d9', color: 'white', width: '80px', height: '80px', borderRadius: '50%' }
        };

        // 4.2. 추천된 멘토 노드
        const mentorNodes = recommendedMentors.map((mentor, index) => {
          // 5. ⭐️ (수정) DB에서 온 career_info 텍스트를 파싱
          const parsedInfo = parseCareerInfo(mentor.career_info);

          return {
            id: mentor.id, 
            type: 'output',
            label: mentor.full_name, 
            position: { 
              x: 400 + Math.cos((index / recommendedMentors.length) * 2 * Math.PI) * 300,
              y: 300 + Math.sin((index / recommendedMentors.length) * 2 * Math.PI) * 300,
            },
            data: { // 👈 사이드바에 표시될 실제 데이터
              type: 'mentor',
              id: mentor.id,
              user_id: mentor.user_id,
              name: mentor.full_name,
              matchingScore: (mentor.similarity * 100).toFixed(1), // 👈 실제 AI 유사도
              company: parsedInfo.company,        // 👈 파싱된 "회사"
              team: parsedInfo.team,              // 👈 파싱된 "직무"
              experienceYears: parsedInfo.experienceYears, // 👈 파싱된 "경력"
              tags: parsedInfo.topics.split(',').map(t => t.trim()), // 👈 파싱된 "전문분야"
              introduction: parsedInfo.introduction, // 👈 파싱된 "소개"
            },
            style: { background: '#22c55e', color: 'black', border: '2px solid #16a34a' } 
          };
        });

        // 4.3. 멘티 -> 멘토 연결선
        const mentorEdges = recommendedMentors.map(mentor => ({
          id: `e-m-${mentor.id}`,
          source: menteeNode.id,
          target: mentor.id,
          animated: true,
          style: { stroke: '#adb5bd' }
        }));
        
        nodes.value = [menteeNode, ...mentorNodes];
        edges.value = mentorEdges;
        
        console.log('네트워크 데이터를 API에서 성공적으로 로드했습니다.');

      } catch (error) {
        console.error('네트워크 데이터 로딩 실패:', error);
        nodes.value = [];
        edges.value = [];
      } finally {
        isLoading.value = false;
      }
    }
  }

  /**
   * 로그아웃 시 네트워크 데이터를 비우는 액션
   */
  function clearNetworkData() {
    nodes.value = [];
    edges.value = [];
  }

// ... (setMockData 함수 생략) ...

  return { 
    nodes, 
    edges, 
    isLoading, 
    fetchNetworkData,
    clearNetworkData
  };
});