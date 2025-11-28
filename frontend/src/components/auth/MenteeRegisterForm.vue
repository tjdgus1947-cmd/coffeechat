<template>
  <div class="register-form-container">
    <!-- 상단 단계 표시줄 (Step Indicator) -->
    <div class="step-indicator">
      <div class="step-item" :class="{ active: step >= 1 }">
        <div class="circle">1</div>
        <span>기본 정보</span>
      </div>
      <div class="line" :class="{ active: step >= 2 }"></div>
      <div class="step-item" :class="{ active: step >= 2 }">
        <div class="circle">2</div>
        <span>성향 분석</span>
      </div>
      <div class="line" :class="{ active: step >= 3 }"></div>
      <div class="step-item" :class="{ active: step >= 3 }">
        <div class="circle">3</div>
        <span>최종 가입</span>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-content">
      
      <!-- [STEP 1] 기본 정보 입력 -->
      <div v-if="step === 1" class="step-section fade-in">
        <h3>👋 멘티님, 기본 정보를 알려주세요</h3>
        
        <div class="form-group">
          <label>이메일</label>
          <input type="email" v-model="form.email" placeholder="example@email.com" required>
        </div>
        
        <div class="form-group">
          <label>비밀번호</label>
          <input type="password" v-model="form.password" placeholder="비밀번호 입력" required>
        </div>
        
        <div class="form-group">
          <label>이름</label>
          <input type="text" v-model="form.name" placeholder="본명 입력" required>
        </div>
        
        <div class="form-group">
          <label>현재 상황 (학교, 학년, 직무 등)</label>
          <input type="text" v-model="form.situation" placeholder="예: OO대학교 경영학과 4학년, 취업 준비생" required>
        </div>
        
        <div class="form-group">
          <label>관심 분야 (쉼표로 구분)</label>
          <!-- 💡 [수정] 구체적인 기술 스택이나 직무명을 유도 -->
          <input type="text" v-model="form.topics" placeholder="예: Java, Spring, 마케팅, 데이터 분석 (구체적인 기술/직무명)" required>
        </div>
        
        <div class="form-group">
          <label>자기소개 키워드 (초안)</label>
          <!-- 💡 [수정] 팩트 위주의 입력을 유도하는 프롬프트 -->
          <textarea 
            v-model="form.introduction_draft" 
            rows="3" 
            placeholder="현재 집중해서 공부 중인 것, 가고 싶은 목표 기업/산업, 본인의 성격 장점 등을 키워드로 나열해주세요. (AI가 이 내용을 바탕으로 자기소개를 작성합니다!)"
          ></textarea>
        </div>
        
        <button type="button" class="btn-primary full-width" @click="goToStep2">
          다음 (성향 분석) →
        </button>
      </div>

      <!-- [STEP 2] 5가지 성향 질문 (AI 매칭 최적화) -->
      <div v-if="step === 2" class="step-section fade-in">
        <h3>🤔 멘토링 스타일을 선택해주세요</h3>
        <p class="sub-desc">답변을 바탕으로 멘토와 핏(Fit)이 딱 맞는 자기소개서를 만듭니다.</p>
        
        <div class="survey-list">
          <div class="survey-item" v-for="(q, index) in questions" :key="q.key">
            <label class="q-label">Q{{ index + 1 }}. {{ q.text }}</label>
            <select v-model="surveyAnswers[q.key]" class="q-select">
              <option disabled value="">선택해주세요</option>
              <option v-for="opt in q.options" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>

        <div class="btn-group">
          <button type="button" class="btn-secondary" @click="step = 1">이전</button>
          <button type="button" class="btn-primary flex-grow" @click="handleGenerateAI" :disabled="isGenerating">
            <span v-if="isGenerating">🤖 AI가 분석 중...</span>
            <span v-else>✨ AI 자기소개 생성하기</span>
          </button>
        </div>
      </div>

      <!-- [STEP 3] AI 결과 확인 및 최종 가입 -->
      <div v-if="step === 3" class="step-section fade-in">
        <h3>📝 최종 자기소개 확인</h3>
        <p class="sub-desc">AI가 작성한 내용을 확인하고, 필요하면 직접 수정하세요.</p>

        <div class="ai-result-box">
          <label>완성된 자기소개서</label>
          <textarea 
            v-model="form.final_introduction" 
            rows="12" 
            class="final-textarea"
            placeholder="AI 생성 결과가 여기에 표시됩니다."
          ></textarea>
        </div>

        <div class="btn-group">
          <button type="button" class="btn-secondary" @click="step = 2">다시 생성</button>
          <button type="submit" class="btn-primary flex-grow" :disabled="isLoading">
            {{ isLoading ? '가입 처리 중...' : '✅ 멘티로 가입 완료' }}
          </button>
        </div>
      </div>

      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const authStore = useAuthStore();
const router = useRouter();

// 상태 관리
const step = ref(1);
const isLoading = ref(false);
const isGenerating = ref(false);
const errorMessage = ref('');

// 입력 폼 데이터
const form = reactive({
  email: '',
  password: '',
  name: '',
  situation: '', 
  topics: '',
  introduction_draft: '', 
  final_introduction: '', 
});

// 설문 데이터 (Step 2)
const surveyAnswers = reactive({
  q1: '', q2: '', q3: '', q4: '', q5: ''
});

// 💡 [수정] 멘티용 핵심 5대 질문 (매칭 알고리즘 최적화)
const questions = [
  { 
    key: 'q1', 
    text: '지금 가장 해결하고 싶은 문제는 무엇인가요?', 
    options: [
      '취업/이직 합격 (자소서, 면접)', 
      '기술 역량 향상 (코딩, 실무 스킬)', 
      '커리어 방향성 설정 (진로 고민)', 
      '회사 생활/적응 (조직 문화, 인간관계)', 
      '네트워킹/정보 (현직자 이야기, 업계 동향)'
    ] 
  },
  { 
    key: 'q2', 
    text: '선호하는 피드백 방식은 무엇인가요?', 
    options: [
      '팩트 폭격 (냉철하고 직설적인 조언)', 
      '칭찬과 격려 (자존감을 높여주는 응원)', 
      '구체적 대안 (해결책을 딱 정해주는 것)', 
      '스스로 생각 유도 (질문을 던져주는 코칭)', 
      '경험 공유 (멘토님의 실제 실패/성공담)'
    ] 
  },
  { 
    key: 'q3', 
    text: '현재 본인의 준비 상태는 어느 정도인가요?', 
    options: [
      '백지 상태 (기초부터 잡아야 함)', 
      '기본기 장착 (아는데 응용이 안 됨)', 
      '취업 준비 중 (포트폴리오/실전 대비)', 
      '현직 주니어 (사수 없이 고군분투 중)', 
      '이직 준비 (경력 점프업 희망)'
    ] 
  },
  { 
    key: 'q4', 
    text: '커피챗 시간을 어떻게 쓰고 싶나요?', 
    options: [
      'Q&A 위주 (준비한 질문 빠르게 해결)', 
      '모의 면접 (실전 테스트 및 피드백)', 
      '코드/포폴 리뷰 (작업물 디테일 첨삭)', 
      '자유로운 대화 (편안한 수다와 고민 상담)', 
      '강의형 (멘토님의 노하우 지식 듣기)'
    ] 
  },
  { 
    key: 'q5', 
    text: '멘토링을 통해 기대하는 관계는?', 
    options: [
      '원포인트 레슨 (이번 한 번으로 해결)', 
      '가끔 안부 (필요할 때 종종 연락)', 
      '러닝 메이트 (목표 달성까지 꾸준히)', 
      '롤모델 찾기 (태도까지 닮고 싶음)', 
      '인맥 형성 (미래의 업계 동료)'
    ] 
  }
];

// Step 1 -> Step 2 이동
const goToStep2 = () => {
  if (!form.email || !form.password || !form.name || !form.situation || !form.topics) {
    errorMessage.value = '필수 정보를 모두 입력해주세요.';
    return;
  }
  errorMessage.value = '';
  step.value = 2;
};

// AI 생성 요청 (Step 2 -> Step 3)
const handleGenerateAI = async () => {
  if (Object.values(surveyAnswers).some(v => !v)) {
    errorMessage.value = '모든 질문에 답해주세요.';
    return;
  }

  isGenerating.value = true;
  errorMessage.value = '';

  try {
    const response = await api.post('/ai/generate-intro', {
      original_intro: form.introduction_draft,
      situation: form.situation,
      topics: form.topics,
      survey_answers: surveyAnswers,
      role: 'mentee' // 역할 명시
    });

    form.final_introduction = response.data.generated_text;
    step.value = 3; 
  } catch (error) {
    console.error('AI 생성 실패:', error);
    errorMessage.value = 'AI 자기소개 생성 중 오류가 발생했습니다.';
  } finally {
    isGenerating.value = false;
  }
};

// 최종 가입 요청 (Step 3)
const handleSubmit = async () => {
  if (!form.final_introduction.trim()) {
    errorMessage.value = '자기소개 내용을 확인해주세요.';
    return;
  }

  isLoading.value = true;
  errorMessage.value = '';

  try {
    const formData = new FormData();
    formData.append('email', form.email);
    formData.append('password', form.password);
    formData.append('name', form.name);
    formData.append('topics', form.topics);
    formData.append('situation', form.situation);
    formData.append('introduction', form.final_introduction);
    
    // (임시 위치값)
    formData.append('latitude', '37.5665'); 
    formData.append('longitude', '126.9780');

    await authStore.registerMentee(formData);
    
    alert('가입이 완료되었습니다! 로그인을 진행해주세요.');
    router.push({ name: 'login' });

  } catch (error) {
    console.error('가입 실패:', error);
    errorMessage.value = '가입 실패: ' + (error.response?.data?.detail || error.message);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 전체 레이아웃 */
.register-form-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
}

/* 단계 표시줄 */
.step-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
  position: relative;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 2;
  color: #9ca3af;
  font-size: 14px;
  font-weight: 500;
}
.step-item.active {
  color: #6d28d9;
  font-weight: 700;
}
.circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #e5e7eb;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 6px;
  transition: background-color 0.3s;
}
.step-item.active .circle {
  background-color: #6d28d9;
}
.line {
  flex-grow: 1;
  height: 2px;
  background-color: #e5e7eb;
  margin: 0 10px;
  margin-bottom: 20px;
  position: relative;
  top: -13px;
  z-index: 1;
}
.line.active {
  background-color: #6d28d9;
}

/* 폼 컨텐츠 */
.form-content {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05);
  border: 1px solid #f3f4f6;
}

h3 {
  font-size: 22px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 10px;
}
.sub-desc {
  color: #6b7280;
  font-size: 14px;
  margin-bottom: 24px;
}

/* 입력 필드 */
.form-group {
  margin-bottom: 20px;
}
.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #374151;
  font-size: 14px;
}
input, textarea, select {
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}
input:focus, textarea:focus, select:focus {
  border-color: #6d28d9;
  box-shadow: 0 0 0 3px rgba(109, 40, 217, 0.1);
}

/* 버튼 */
.btn-primary {
  background-color: #6d28d9;
  color: white;
  border: none;
  padding: 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}
.btn-primary:hover:not(:disabled) { background-color: #5b21b6; }
.btn-primary:disabled { background-color: #cbd5e1; cursor: not-allowed; }

.btn-secondary {
  background-color: #f3f4f6;
  color: #4b5563;
  border: none;
  padding: 14px 20px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}
.btn-secondary:hover { background-color: #e5e7eb; }

.full-width { width: 100%; }
.flex-grow { flex-grow: 1; }
.btn-group {
  display: flex;
  gap: 12px;
  margin-top: 30px;
}

/* 설문 항목 */
.survey-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.q-label {
  display: block;
  font-weight: 600;
  margin-bottom: 8px;
  color: #111;
}

/* AI 결과 */
.final-textarea {
  background-color: #fcfaff;
  border-color: #e9d5ff;
  line-height: 1.6;
}

/* 에러 메시지 */
.error-msg {
  color: #dc2626;
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  font-weight: 500;
}

/* 애니메이션 */
.fade-in {
  animation: fadeIn 0.3s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>