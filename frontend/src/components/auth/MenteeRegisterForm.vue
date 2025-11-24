<template>
  <div class="register-form">
    <div class="step-indicator">
      <span :class="{ active: step >= 1 }">1. 정보 입력</span>
      <span class="line"></span>
      <span :class="{ active: step >= 2 }">2. 성향 분석</span>
      <span class="line"></span>
      <span :class="{ active: step >= 3 }">3. 최종 확인</span>
    </div>

    <form @submit.prevent="handleSubmit">
      
      <div v-if="step === 1" class="step-section">
        <h3>기본 정보를 입력해주세요</h3>
        <div class="form-group">
          <label>이메일</label>
          <input type="email" v-model="form.email" required>
        </div>
        <div class="form-group">
          <label>비밀번호</label>
          <input type="password" v-model="form.password" required>
        </div>
        <div class="form-group">
          <label>이름</label>
          <input type="text" v-model="form.name" required>
        </div>
        <div class="form-group">
          <label>현재 상황 (학교, 학년, 직무 등)</label>
          <input type="text" v-model="form.situation" placeholder="예: OO대학교 경영학과 4학년" required>
        </div>
        <div class="form-group">
          <label>관심 분야 (쉼표로 구분)</label>
          <input type="text" v-model="form.topics" placeholder="예: CPA, 재무, 회계" required>
        </div>
        <div class="form-group">
          <label>자기 소개 초안 (키워드만 적으셔도 됩니다)</label>
          <textarea v-model="form.introduction_draft" rows="3" placeholder="AI가 이 내용을 바탕으로 멋진 소개를 만들어드릴 거예요."></textarea>
        </div>
        
        <button type="button" class="next-btn" @click="goToStep2">다음 (성향 분석) →</button>
      </div>

      <div v-if="step === 2" class="step-section">
        <h3>더 나은 매칭을 위해 5가지 질문에 답해주세요</h3>
        
        <div class="survey-question" v-for="(q, index) in questions" :key="index">
          <label class="q-label">Q{{ index + 1 }}. {{ q.text }}</label>
          <select v-model="surveyAnswers[q.key]" class="q-select">
            <option disabled value="">선택해주세요</option>
            <option v-for="opt in q.options" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>

        <div class="btn-group">
          <button type="button" class="prev-btn" @click="step = 1">이전</button>
          <button type="button" class="next-btn" @click="handleGenerateAI">
            {{ isGenerating ? 'AI가 작성 중...' : 'AI 자기소개 생성하기 ✨' }}
          </button>
        </div>
      </div>

      <div v-if="step === 3" class="step-section">
        <h3>AI가 작성한 자기소개입니다</h3>
        <p class="guide-text">내용을 확인하고 필요하면 직접 수정한 뒤 가입을 완료하세요.</p>

        <div class="form-group">
          <label>최종 자기소개 (이 내용으로 임베딩됩니다)</label>
          <textarea v-model="form.final_introduction" rows="10" class="final-textarea"></textarea>
        </div>

        <div class="btn-group">
          <button type="button" class="prev-btn" @click="step = 2">이전 (다시 생성)</button>
          <button type="submit" class="submit-btn" :disabled="isLoading">
            {{ isLoading ? '가입 처리 중...' : '멘티로 가입 완료 ✅' }}
          </button>
        </div>
      </div>

      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useAuthStore } from '@/store/auth';
import { useRouter } from 'vue-router';
import api from '@/services/api'; // axios instance

const authStore = useAuthStore();
const router = useRouter();

const step = ref(1);
const isLoading = ref(false);
const isGenerating = ref(false);
const errorMessage = ref('');

// 폼 데이터
const form = reactive({
  email: '',
  password: '',
  name: '',
  situation: '',
  topics: '',
  introduction_draft: '', // 사용자가 처음에 쓴 초안
  final_introduction: '', // AI가 써준 최종본
});

// 설문 데이터 (질문지)
const surveyAnswers = reactive({
  q1: '', q2: '', q3: '', q4: '', q5: ''
});

const questions = [
  { 
    key: 'q1', 
    text: '선호하는 멘토링 방식은?', 
    options: ['체계적인 커리큘럼 기반', '자유로운 Q&A 및 대화', '실무 과제 및 피드백 위주', '경험 공유 및 상담 위주'] 
  },
  { 
    key: 'q2', 
    text: '현재 가장 큰 고민은 무엇인가요?', 
    options: ['진로 방향성 설정', '구체적인 직무 스킬 부족', '취업/이직 준비 노하우', '업계 현황 및 정보 부족'] 
  },
  { 
    key: 'q3', 
    text: '멘토에게 가장 바라는 점은?', 
    options: ['따끔한 충고와 현실적 조언', '따뜻한 격려와 동기부여', '구체적인 정보와 자료 제공', '네트워킹 기회'] 
  },
  { 
    key: 'q4', 
    text: '현재 본인의 학습/준비 상태는?', 
    options: ['이제 막 관심을 가진 입문 단계', '기초 지식은 있으나 실무 경험 없음', '관련 프로젝트/인턴 경험 있음', '현직자 수준에 가까움'] 
  },
  { 
    key: 'q5', 
    text: '목표 달성 희망 기간은?', 
    options: ['1개월 이내 (단기)', '3개월 이내', '6개월 이내', '1년 이상 (장기)'] 
  }
];

// Step 1 -> Step 2 이동 검증
const goToStep2 = () => {
  if (!form.email || !form.password || !form.name || !form.situation || !form.topics) {
    errorMessage.value = '모든 필수 정보를 입력해주세요.';
    return;
  }
  errorMessage.value = '';
  step.value = 2;
};

// AI 생성 요청 (Step 2 -> Step 3)
const handleGenerateAI = async () => {
  // 설문 다 했는지 체크
  if (Object.values(surveyAnswers).some(val => !val)) {
    errorMessage.value = '모든 설문 문항을 선택해주세요.';
    return;
  }

  isGenerating.value = true;
  errorMessage.value = '';

  try {
    // 1. 백엔드에 AI 생성 요청
    const response = await api.post('/ai/generate-intro', {
      original_intro: form.introduction_draft,
      situation: form.situation,
      topics: form.topics,
      survey_answers: surveyAnswers
    });

    // 2. 결과 받아서 최종 텍스트에 넣기
    form.final_introduction = response.data.generated_text;
    
    // 3. 다음 단계로 이동
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
    // 실제 가입 API 호출 (최종 자기소개를 introduction 필드로 전송)
    // FormData 객체 생성 (FileUploader를 안 쓰더라도 기존 로직 유지를 위해 FormData 사용 권장)
    const formData = new FormData();
    formData.append('email', form.email);
    formData.append('password', form.password);
    formData.append('name', form.name);
    formData.append('situation', form.situation);
    formData.append('topics', form.topics);
    // ⭐️ 중요: AI가 만든 최종 소개를 'introduction'(또는 백엔드가 받는 필드명)으로 보냄
    // auth.py의 sign_up_mentee는 'situation', 'topics'는 받지만 
    // 'introduction' 필드가 없습니다. 
    // 대신 'career_goal'이나 'situation'에 합쳐서 넣거나,
    // 백엔드 api/auth.py의 sign_up_mentee 함수에 introduction 파라미터를 추가해야 합니다.
    
    // 여기서는 'situation' 필드에 합쳐서 보내는 예시를 들겠습니다. (또는 백엔드 수정 필요)
    // 하지만 가장 좋은 건 백엔드에 introduction 필드를 살리는 것입니다.
    // 현재 auth.py를 보면 'situation', 'topics'만 받습니다.
    // 임베딩은 `text_to_embed = f"현재 상황: {situation}. 희망 진로: {topics}"` 로 생성됩니다.
    
    // 🔥 솔루션: 'situation' 필드에 최종 자기소개를 통째로 넣거나,
    // auth.py를 수정해서 introduction을 별도로 받아 text_to_embed에 포함시키는 것이 좋습니다.
    // 여기선 일단 situation 필드를 활용합니다.
    formData.append('situation', form.final_introduction); 
    formData.append('topics', form.topics);

    await authStore.registerMentee(formData);
    
    alert('회원가입이 완료되었습니다! 멋진 자기소개로 멘토를 만나보세요.');
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
.step-indicator {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30px;
  font-weight: bold;
  color: #999;
}
.step-indicator span.active {
  color: #6d28d9;
}
.step-indicator .line {
  width: 30px;
  height: 2px;
  background: #ddd;
  margin: 0 10px;
}

.step-section {
  animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #333; }
.form-group input, .form-group textarea, .q-select { 
  width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem;
}
.form-group textarea { resize: vertical; }

.survey-question { margin-bottom: 20px; }
.q-label { display: block; margin-bottom: 8px; font-weight: 600; color: #444; }

.btn-group { display: flex; gap: 10px; margin-top: 20px; }
.next-btn, .submit-btn { 
  flex: 1; background-color: #6d28d9; color: white; padding: 12px; 
  border: none; border-radius: 6px; font-weight: bold; cursor: pointer; 
}
.prev-btn { 
  width: 80px; background-color: #f3f4f6; color: #555; padding: 12px; 
  border: none; border-radius: 6px; font-weight: bold; cursor: pointer; 
}
.next-btn:hover, .submit-btn:hover { background-color: #5b21b6; }
.prev-btn:hover { background-color: #e5e7eb; }

.error { color: #dc2626; margin-top: 10px; text-align: center; }
.guide-text { color: #666; font-size: 0.9rem; margin-bottom: 15px; }
.final-textarea { border-color: #6d28d9; background-color: #fdfaff; }
</style>