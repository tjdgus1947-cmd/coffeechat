// mentorNetworkStore.js - 멘토-멘토 네트워크 데이터 관리

import { defineStore } from 'pinia';
import { ref } from 'vue';
import { supabase } from '@/supabaseClient';

// career_info 파싱 함수 (강화 버전)
function parseCareerInfo(text) {
  if (!text) return { 
    company: '정보 없음', 
    role: null, 
    experienceYears: '0', 
    topics: [], 
    introduction: '정보 없음' 
  };
  
  try {
    const info = {
      company: text.match(/회사:\s*([^,\n]+)/)?.[1]?.trim() || '정보 없음',
      role: text.match(/직무:\s*([^,\n]+)/)?.[1]?.trim() || null,
      experienceYears: text.match(/경력:\s*(\d+)\s*년/)?.[1] || '0',
      topics: (text.match(/전문분야:\s*([^,\n]+)/)?.[1] || '')
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0),
      introduction: text.match(/소개:\s*(.*)/)?.[1]?.trim() || text,
    };
    return info;
  } catch(e) {
    console.error("career_info 파싱 실패:", e);
    return { 
      company: '정보 없음', 
      role: null, 
      experienceYears: '0', 
      topics: [], 
      introduction: text 
    };
  }
}

// 🔥 가중치 기반 매칭 점수 계산
// 직무 일치: 50점, 전문분야 유사도: 50점, 총 100점 만점
function calculateMentorMatches(currentMentor, allMentors) {
  const currentParsed = parseCareerInfo(currentMentor.career_info);
  
  console.log('🔍 현재 멘토 career_info:', currentMentor.career_info);
  console.log('🔍 현재 멘토 파싱 결과:', currentParsed);
  
  return allMentors
    .filter(m => m.id !== currentMentor.id)
    .map(mentor => {
      let matchScore = 0;
      const commonTopics = [];
      
      // --- 1. 직무 일치 점수 (50점) ---
      const mentorParsed = parseCareerInfo(mentor.career_info);
      const isRoleMatch = currentParsed.role && mentorParsed.role &&
                          currentParsed.role.toLowerCase() === mentorParsed.role.toLowerCase();
      
      if (isRoleMatch) {
        matchScore += 50;
      }
      
      // --- 2. 전문 분야 유사도 점수 (50점) ---
      const currentTopics = currentParsed.topics;
      const mentorTopics = mentorParsed.topics;
      
      // 공통 키워드 찾기
      const intersection = currentTopics.filter(t =>
        mentorTopics.some(mt =>
          mt.toLowerCase().includes(t.toLowerCase()) ||
          t.toLowerCase().includes(mt.toLowerCase())
        )
      );
      
      commonTopics.push(...intersection);
      
      // 유사도 계산
      const topicSimilarity = intersection.length > 0
        ? (intersection.length / Math.max(currentTopics.length, mentorTopics.length))
        : 0;
      
      const topicScore = topicSimilarity * 50;
      matchScore += topicScore;
      
      // 멘토 정보 반환
      return {
        id: mentor.id,
        user_id: mentor.id,
        name: mentor.full_name,
        company: mentorParsed.company,
        team: mentorParsed.role || '직무 정보 없음',
        experienceYears: mentorParsed.experienceYears,
        tags: mentorParsed.topics,
        introduction: mentorParsed.introduction,
        matchingScore: Math.min(100, matchScore).toFixed(1),
        commonTopics: commonTopics,
        isRoleMatch: isRoleMatch,
        career_info: mentor.career_info,
        type: 'mentor'
      };
    })
    // 매칭 점수가 0이어도 표시 (모든 멘토를 네트워크에 포함)
    .sort((a, b) => b.matchingScore - a.matchingScore);
}

// 노드 생성 (멘티 네트워크 스타일)
function createNodes(currentMentor, relatedMentors) {
  const currentParsed = parseCareerInfo(currentMentor.career_info);
  
  // 중심 노드 (본인 멘토)
  const centerNode = {
    id: 'mentor-center',
    type: 'input',
    label: currentMentor.full_name,
    position: { x: 500, y: 400 },
    data: {
      type: 'mentor-self',
      name: currentMentor.full_name,
      role: currentParsed.role,
      company: currentParsed.company,
      team: currentParsed.role,
      experienceYears: currentParsed.experienceYears,
      tags: currentParsed.topics,
      introduction: currentParsed.introduction,
      user_id: currentMentor.id
    },
    style: {
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      color: 'white',
      width: '120px',
      height: '120px',
      borderRadius: '50%',
      fontSize: '16px',
      fontWeight: 'bold',
      border: '4px solid #fbbf24'
    }
  };

  // 주변 멘토 노드들 (상위 10명만 표시)
  const topMentors = relatedMentors.slice(0, 10);
  const mentorNodes = topMentors.map((mentor, index) => {
    const angle = (index / topMentors.length) * 2 * Math.PI;
    return {
      id: `mentor-${mentor.user_id}`,
      type: 'output',
      label: mentor.name,
      position: {
        x: 500 + Math.cos(angle) * 350,
        y: 400 + Math.sin(angle) * 350
      },
      data: mentor,
      style: {
        background: '#22c55e',
        color: 'white',
        border: '3px solid #16a34a',
        width: '100px',
        height: '100px',
        borderRadius: '50%',
        fontSize: '14px',
        fontWeight: '600'
      }
    };
  });

  return [centerNode, ...mentorNodes];
}

// 엣지 생성 (멘티 네트워크와 동일한 보라색 애니메이션 스타일)
function createEdges(currentMentor, relatedMentors) {
  const topMentors = relatedMentors.slice(0, 10);
  
  return topMentors.map(mentor => ({
    id: `edge-${mentor.user_id}`,
    source: 'mentor-center',
    target: `mentor-${mentor.user_id}`,
    animated: true,
    style: { 
      stroke: '#8b5cf6',
      strokeWidth: 2
    }
  }));
}

export const useMentorNetworkStore = defineStore('mentorNetwork', () => {
  const nodes = ref([]);
  const edges = ref([]);
  const topMentors = ref([]); // TOP 멘토 리스트 (사이드 패널용)
  const isLoading = ref(false);
  const error = ref(null);

  async function fetchMentorNetwork(currentUserId) {
    isLoading.value = true;
    error.value = null;
    
    try {
      console.log('🔍 멘토 네트워크 로딩 시작:', currentUserId);
      
      // 백엔드 API를 통해 멘토 목록 가져오기
      const response = await fetch(`http://localhost:8000/api/mentors/`);
      
      if (!response.ok) {
        throw new Error(`API 에러: ${response.status}`);
      }
      
      let rawData = await response.json();
      
      console.log('🔍 API 응답 데이터 샘플:', rawData[0]);
      console.log('🔍 현재 사용자 ID:', currentUserId);
      
      // API 응답 데이터 변환 (mentor_profiles 구조를 평탄화)
      const allMentorsData = rawData.map(mentor => ({
        id: mentor.id,
        full_name: mentor.full_name,
        career_info: mentor.mentor_profiles?.[0]?.career_info || '',
        profile_image_url: mentor.mentor_profiles?.[0]?.profile_image_url,
        location: mentor.mentor_profiles?.[0]?.location
      }));
      
      console.log('✅ 전체 멘토 수:', allMentorsData?.length || 0);
      console.log('🔍 전체 멘토 ID 목록:', allMentorsData.map(m => m.id));
      
      // 현재 로그인한 사용자 찾기
      const currentMentorData = allMentorsData.find(m => m.id === currentUserId);
      
      if (!currentMentorData) {
        console.error('❌ 현재 사용자를 멘토 목록에서 찾을 수 없습니다!');
        console.error('현재 사용자 ID:', currentUserId);
        console.error('멘토 목록의 첫 3개 ID:', allMentorsData.slice(0, 3).map(m => ({ id: m.id, name: m.full_name })));
        throw new Error('현재 멘토 정보를 찾을 수 없습니다. 멘토로 등록되어 있는지 확인해주세요.');
      }
      
      console.log('✅ 현재 멘토:', currentMentorData.full_name);
      
      // 3. 매칭 점수 계산
      const relatedMentors = calculateMentorMatches(
        currentMentorData,
        allMentorsData || []
      );
      
      console.log('✅ 매칭된 멘토 수:', relatedMentors.length);
      if (relatedMentors.length > 0) {
        console.log('Top 3 멘토:', relatedMentors.slice(0, 3).map(m => ({
          name: m.name,
          score: m.matchingScore
        })));
      }
      
      // 4. TOP 멘토 리스트 저장 (전체 리스트)
      topMentors.value = relatedMentors;
      console.log('🔍 topMentors 저장 완료:', topMentors.value.slice(0, 3).map(m => ({
        name: m.name,
        matchingScore: m.matchingScore,
        hasScore: !!m.matchingScore
      })));
      
      // 5. 노드와 엣지 생성 (상위 10명만)
      nodes.value = createNodes(currentMentorData, relatedMentors);
      edges.value = createEdges(currentMentorData, relatedMentors);
      
      console.log('🔍 생성된 노드:', nodes.value.length);
      console.log('🔍 생성된 엣지:', edges.value.length);
      console.log('🔍 노드 상세:', nodes.value.map(n => ({ id: n.id, label: n.label })));
      
      console.log('✅ 멘토 네트워크 데이터 로드 완료:', {
        totalMentors: relatedMentors.length,
        displayedNodes: nodes.value.length - 1, // 본인 제외
        topMentors: topMentors.value.length
      });
      
    } catch (err) {
      console.error('❌ 멘토 네트워크 로딩 실패:', err);
      error.value = err.message;
      nodes.value = [];
      edges.value = [];
      topMentors.value = [];
    } finally {
      isLoading.value = false;
    }
  }

  function clearNetwork() {
    nodes.value = [];
    edges.value = [];
    topMentors.value = [];
    error.value = null;
  }

  return {
    nodes,
    edges,
    topMentors,
    isLoading,
    error,
    fetchMentorNetwork,
    clearNetwork
  };
});
