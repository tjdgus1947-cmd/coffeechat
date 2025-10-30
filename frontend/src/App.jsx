// frontend/src/App.jsx

import React, { useState, useEffect } from 'react';
// 1. 26단계에서 추가한 getRecommendedMentors 함수를 임포트합니다.
//    (경로가 '../'가 맞는지 다시 확인하세요. image_f9b19d.png[cite: image_f9b19d.png]에서는 services가 src 밖에 있었습니다.)
import { getRecommendedMentors } from '../services/api.js'; 
import MainView from './pages/MainView.jsx';

function App() {
  const [mentors, setMentors] = useState([]); // "장바구니"는 그대로 둡니다.

  // 2. useEffect가 AI 추천 API를 호출하도록 변경
  useEffect(() => {
    // --- (하드코딩) 테스트할 멘티 ID ---
    // ⚠️ (필수) "데이터 완전 초기화" 3단계에서 복사한 
    // "김멘티4"의 *새* ID (image_9f197b.png[cite: image_9f197b.png]에서 확인한 ID)
    const TEST_MENTEE_ID = '220a4bc8-5120-43d5-b3c1-dc86a9e94d0b'; 
    // ------------------------------------

    console.log(`AI 추천 멘토 목록 불러오기 시도 (멘티 ID: ${TEST_MENTEE_ID})...`);
    
    // 3. (수정) getRecommendedMentors()를 호출
    getRecommendedMentors(TEST_MENTEE_ID)
      .then(response => {
        console.log('AI 추천 멘토 목록 불러오기 성공:', response.data);
        // 18단계의 테스트 결과("이멘토" 1명)가 "장바구니"에 담깁니다.
        setMentors(response.data); 
      })
      .catch(error => {
        console.error('AI 추천 멘토 목록 불러오기 실패:', error.response ? error.response.data : error.message);
      });
  }, []); // [] (빈 배열) = "이 컴포넌트가 처음 뜰 때 딱 한 번만 실행"


  // (wbs_detail.md[cite: wbs_detail.md]의 메인 뷰가 렌더링되도록 수정)
  return (
    <div className="App" style={{ width: '100vw', height: '100vh' }}>
      {/* 이제 멘토 목록(mentors)을 MainView 컴포넌트에 'prop'으로 전달합니다.
        MainView는 "이멘토" 1명만 받아서 그래프를 그립니다.
      */}
      <MainView mentors={mentors} />
    </div>
  );
}

export default App;