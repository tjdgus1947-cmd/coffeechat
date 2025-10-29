// frontend/src/App.jsx

// 1. useState와 useEffect를 임포트합니다.
import React, { useState, useEffect } from 'react';

// 2. (중요) 12단계 api.js에서 signUpUser와 getMentors 함수를 가져옵니다.
import { signUpUser, getMentors } from '../services/api.js'; 

function App() {
  // 3. 멘토 목록을 저장할 "장바구니"(state)를 만듭니다.
  const [mentors, setMentors] = useState([]); // 처음엔 빈 배열

  // 4. (중요) 컴포넌트가 처음 로드될 때 멘토 목록을 불러옵니다.
  useEffect(() => {
    console.log('멘토 목록 불러오기 시도...');
    
    getMentors() // 12단계에서 만든 멘토 목록 API 함수 호출
      .then(response => {
        console.log('멘토 목록 불러오기 성공:', response.data);
        setMentors(response.data); // 성공 시, 멘토 데이터를 "장바구니"에 담습니다.
      })
      .catch(error => {
        console.error('멘토 목록 불러오기 실패:', error.response ? error.response.data : error.message);
      });
  }, []); // [] (빈 배열) = "이 컴포넌트가 처음 뜰 때 딱 한 번만 실행"

  // (회원가입 테스트 함수들은 그대로 둡니다)
  const handleTestMenteeSignUp = async () => {
    try {
      const email = 'mentee-test-03@example.com';
      const password = 'mypassword123';
      const role = 'mentee';
      const fullName = '김멘티3';

      console.log('멘티 회원가입 테스트 시작...');
      const response = await signUpUser(email, password, role, fullName);
      console.log('멘티 회원가입 성공:', response.data);
      alert('멘티 회원가입 성공! Supabase 대시보드를 확인하세요.');

    } catch (error) {
      console.error('멘티 회원가입 실패:', error.response ? error.response.data : error.message);
      alert('멘티 회원가입 실패! 브라우저 콘솔(F12)을 확인하세요.');
    }
  };

  const handleTestMentorSignUp = async () => {
    console.log('멘토 3명 대량 등록 테스트 시작...');
    
    const mentorsToCreate = [
      { email: 'mentor-test-01@example.com', fullName: '이멘토' },
      { email: 'mentor-test-02@example.com', fullName: '박멘토' },
      { email: 'mentor-test-03@example.com', fullName: '최멘토' }
    ];

    try {
      for (const mentor of mentorsToCreate) {
        console.log(`-> ${mentor.fullName} 등록 시도...`);
        await signUpUser(
          mentor.email,
          'mypassword123',
          'mentor',
          mentor.fullName
        );
        console.log(`-> ${mentor.fullName} 등록 성공!`);
      }
      console.log('멘토 3명 대량 등록 완료!');
      alert('멘토 3명 등록 성공! Supabase 대시보드를 확인하세요.');
    } catch (error) {
      console.error('멘토 대량 등록 중 실패:', error.response ? error.response.data : error.message);
      alert('멘토 등록 실패! 브라우저 콘솔(F12)을 확인하세요.');
    }
  };

  return (
    <div className="App">
      <h1>커피챗 플랫폼 (React)</h1>

      {/* 테스트 버튼들 */}
      <button onClick={handleTestMenteeSignUp} style={{ padding: '10px', fontSize: '16px' }}>
        멘티 1명 회원가입 테스트
      </button>
      <button onClick={handleTestMentorSignUp} style={{ padding: '10px', fontSize: '16px', marginLeft: '10px' }}>
        멘토 3명 대량 등록 테스트
      </button>

      <hr style={{ margin: '20px 0' }} />

      {/* 5. (새로 추가) 멘토 목록 표시 */}
      <h2>멘토 목록 (DB에서 불러옴)</h2>
      {mentors.length === 0 ? (
        <p>멘토가 없거나 DB에서 불러오는 중입니다...</p>
      ) : (
        <ul>
          {/* "장바구니"에 담긴 멘토들을 순회하며 이름 표시 */}
          {mentors.map(mentor => (
            <li key={mentor.id}>
              {mentor.full_name} (ID: {mentor.id})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;