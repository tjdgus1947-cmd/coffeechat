import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import api from '@/services/api';

// MOCK_DATA 스위치를 false로 변경
const MOCK_DATA = false;

// career_info 텍스트를 파싱하는 헬퍼 함수
function parseCareerInfo(text) {
  if (!text) return { company: '정보 없음', team: '정보 없음', experienceYears: '0', topics: '', introduction: '정보 없음' };
  try {
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
    
    if (!authStore.userId) {
      console.log('네트워크 데이터 로드 중단: 사용자 ID 없음 (로그인 필요)');
      return;
    }

    isLoading.value = true;
    
    if (MOCK_DATA) {
      // (이 부분은 이제 실행되지 않음)
    } 
    else {
      try {
        // (수정) /api prefix 추가
        const response = await api.get(`/mentors/recommended/${authStore.userId}`);
        
        const recommendedMentors = response.data; 
        
        const menteeNode = {
          id: 'mentee-main',
          type: 'input',
          // (수정) authStore.userName 사용
          label: authStore.userName || '김성현 (나)', 
          position: { x: 400, y: 300 },
          data: { type: 'mentee' },
          style: { background: '#6d28d9', color: 'white', width: '80px', height: '80px', borderRadius: '50%' }
        };

        const mentorNodes = recommendedMentors.map((mentor, index) => {
          const parsedInfo = parseCareerInfo(mentor.career_info);
          return {
            id: mentor.id, 
            type: 'output',
            label: mentor.full_name, 
            position: { 
              x: 400 + Math.cos((index / recommendedMentors.length) * 2 * Math.PI) * 300,
              y: 300 + Math.sin((index / recommendedMentors.length) * 2 * Math.PI) * 300,
            },
            data: { 
              type: 'mentor',
              id: mentor.id,
              user_id: mentor.user_id,
              name: mentor.full_name,
              matchingScore: (mentor.similarity * 100).toFixed(1),
              company: parsedInfo.company,      
              team: parsedInfo.team,            
              experienceYears: parsedInfo.experienceYears,
              tags: parsedInfo.topics.split(',').map(t => t.trim()),
              introduction: parsedInfo.introduction,
            },
            style: { background: '#22c55e', color: 'black', border: '2px solid #16a34a' } 
          };
        });

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

  function clearNetworkData() {
    nodes.value = [];
    edges.value = [];
  }

  return { 
    nodes, 
    edges, 
    isLoading, 
    fetchNetworkData,
    clearNetworkData
  };
});