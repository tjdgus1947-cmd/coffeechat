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
          <input type="text" v-model="form.topics" placeholder="예: 마케팅, 데이터 분석, 해외 취업" required>
        </div>
        
        <div class="form-group">
          <label>자기소개 키워드 (초안)</label>
          <textarea 
            v-model="form.introduction_draft" 
            rows="3" 
            placeholder="멘토에게 어필하고 싶은 키워드나 내용을 간단히 적어주세요. (AI가 멋지게 다듬어 드립니다!)"
          ></textarea>
        </div>
        
        <button type="button" class="btn-primary full-width" @click="goToStep2">
          다음 (성향 분석) →
        </button>
      </div>

      <!-- [STEP 2] 5가지 성향 질문 -->
      <div v-if="step === 2" class="step-section fade-in">
        <h3>🤔 멘토링 스타일을 선택해주세요</h3>
        <p class="sub-desc">답변을 바탕으로 AI가 자기소개서를 작성합니다.</p>
        
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
            <span v-if="isGenerating">🤖 AI가 작성 중...</span>
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
const proofFile = ref(null);

// 입력 폼 데이터
const form = reactive({
  email: '',
  password: '',
  name: '',
  situation: '', // 학교/학년 등 짧은 정보
  topics: '',
  introduction_draft: '', // 사용자가 쓴 초안 (Step 1)
  final_introduction: '', // AI가 써준 최종본 (Step 3)
});

// 설문 데이터 (Step 2)
const surveyAnswers = reactive({
  q1: '', q2: '', q3: '', q4: '', q5: ''
});

// 질문 목록
const questions = [
  { key: 'q1', text: '선호하는 멘토링 방식은?', options: ['체계적인 커리큘럼 기반', '자유로운 Q&A 및 대화', '실무 과제 및 피드백', '경험 공유 및 상담'] },
  { key: 'q2', text: '현재 가장 큰 고민은?', options: ['진로 방향성 설정', '직무 스킬 부족', '취업/이직 노하우', '업계 정보 부족'] },
  { key: 'q3', text: '멘토에게 바라는 점은?', options: ['현실적인 조언', '따뜻한 격려', '정보/자료 공유', '네트워킹'] },
  { key: 'q4', text: '현재 준비 상태는?', options: ['막 관심을 가진 단계', '기초 지식 보유', '관련 경험/인턴 있음', '실무자 수준'] },
  { key: 'q5', text: '목표 달성 희망 기간은?', options: ['1개월 이내', '3개월 이내', '6개월 이내', '1년 이상'] }
];

// 파일 선택 핸들러
const handleFileChange = (e) => {
  proofFile.value = e.target.files[0];
};

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
    // ⭐️ 백엔드 AI 생성 API 호출
    const response = await api.post('/ai/generate-intro', {
      original_intro: form.introduction_draft,
      situation: form.situation,
      topics: form.topics,
      survey_answers: surveyAnswers
    });

    form.final_introduction = response.data.generated_text;
    step.value = 3; // 성공 시 다음 단계로
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
    // ⭐️ FormData 생성 (auth.py 수정사항 반영)
    const formData = new FormData();
    
    formData.append('email', form.email);
    formData.append('password', form.password);
    formData.append('name', form.name);
    formData.append('topics', form.topics);
    
    // ✅ 1. situation: 원래의 짧은 정보 (학교, 학년)
    formData.append('situation', form.situation);
    
    // ✅ 2. introduction: AI가 써준 긴 자기소개
    formData.append('introduction', form.final_introduction);

    // (선택) 위치 정보 임시값 (지도 기능을 위해 필요할 수 있음)
  

    

    // 가입 요청
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

/* 단계 표시줄 (Step Indicator) */
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
  margin-bottom: 20px; /* 텍스트 높이 고려 */
  position: relative;
  top: -13px; /* 원의 중간에 맞춤 */
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

/* 입력 필드 스타일 */
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

/* 버튼 스타일 */
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

/* AI 결과 텍스트박스 */
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