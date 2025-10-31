import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useAuthStore } from './auth';
import api from '@/services/api';

// 1. ⭐️ 백엔드 연동 시 이 값을 false로 바꾸면 됩니다 ⭐️
const MOCK_DATA = true;

export const useNetworkStore = defineStore('network', () => {
  // --- State ---
  const nodes = ref([]);
  const edges = ref([]);
  const isLoading = ref(false); 

  // --- Actions ---

  /**
   * (wbs_detail.md) /api/network/{mentee_id}
   * 로그인한 사용자의 네트워크 데이터를 API에서 가져옵니다.
   */
  async function fetchNetworkData() {
    const authStore = useAuthStore();
    
    if (!authStore.userId) {
      console.log('네트워크 데이터 로드 중단: 사용자 ID 없음');
      return;
    }

    isLoading.value = true;
    
    // 2. ⭐️ MOCK_DATA가 true이면 가짜 데이터 사용 ⭐️
    if (MOCK_DATA) {
      console.warn('!!! MOCK DATA (Network) 활성 상태 !!!');
      setMockData(); // 4번에서 추가할 가짜 데이터 함수 호출
      isLoading.value = false;
    } 
    // 3. ⭐️ MOCK_DATA가 false이면 실제 API 호출 ⭐️
    else {
      try {
        const response = await api.get(`/network/${authStore.userId}`);
        
        nodes.value = response.data.nodes;
        edges.value = response.data.edges;
        
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

  // 4. ⭐️ 1단계에서 사용했던 'setMockData' 함수 (4-1 위해 data 객체 보강) ⭐️
  function setMockData() {
    console.log('가짜 그래프 데이터를 로드합니다.');
    
    nodes.value = [
      // 멘티 (중앙)
      { id: 'mentee-kim', type: 'input', label: '김멘티 (Test)', position: { x: 400, y: 300 }, 
        data: { type: 'mentee' }, // 멘티 타입 지정
        style: { background: '#6d28d9', color: 'white', width: '80px', height: '80px', borderRadius: '50%' } 
      },

      // 멘토 (초록색) - data 객체에 상세 정보 추가
      { id: 'mentor-han', type: 'output', label: '한법무', position: { x: 750, y: 100 }, 
        data: { type: 'mentor', id: 'mentor-han-id', name: '한법무', matchingScore: 58, company: '삼성전자', team: '법무팀', experienceYears: 11, tags: ['법무', '변호사', '계약'], introduction: '삼성전자 법무팀에서 11년간 계약 검토 및 송무를 담당했습니다...' },
        style: { background: '#22c55e', color: 'black', border: '2px solid #16a34a' } 
      },
      { id: 'mentor-lee', type: 'output', label: '이회계', position: { x: 100, y: 150 }, 
        data: { type: 'mentor', id: 'mentor-lee-id', name: '이회계', matchingScore: 92, company: '삼일회계법인', team: '감사1팀', experienceYears: 8, tags: ['CPA', '회계', '감사'], introduction: '삼일회계법인 감사1팀 8년차...' },
        style: { background: '#22c55e', color: 'black', border: '2px solid #16a34a' }
      },
      
      // 키워드 (보라색 테두리)
      { id: 'kw-cpa', label: 'CPA', position: { x: 300, y: 550 }, data: { type: 'keyword' },
        style: { border: '3px solid #6d28d9', padding: '10px 20px', borderRadius: '8px' } 
      },
      { id: 'kw-tax', label: '세무', position: { x: 300, y: 100 }, data: { type: 'keyword' },
        style: { border: '3px solid #6d28d9', padding: '10px 20px', borderRadius: '8px' } 
      },
    ];

    edges.value = [
      // 멘티 -> 키워드 (파란 점선)
      { id: 'e-m-cpa', source: 'mentee-kim', target: 'kw-cpa', animated: true, style: { stroke: '#6d28d9', strokeDasharray: '5 5' } },
      { id: 'e-m-tax', source: 'mentee-kim', target: 'kw-tax', animated: true, style: { stroke: '#6d28d9', strokeDasharray: '5 5' } },
      
      // 키워드 -> 멘토 (초록 점선)
      { id: 'e-cpa-lee', source: 'kw-cpa', target: 'mentor-lee', style: { stroke: '#22c55e', strokeDasharray: '5 5' } },

      // 멘티 -> 멘토 (회색 실선, 약한 연결)
      { id: 'e-m-han', source: 'mentee-kim', target: 'mentor-han', style: { stroke: '#adb5bd' } },
    ];
  }

  return { 
    nodes, 
    edges, 
    isLoading, 
    fetchNetworkData,
    clearNetworkData
  };
});