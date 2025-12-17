<template>
  <div class="register-form-container">
    <!-- 상단 단계 표시줄 -->
    <div class="step-indicator">
      <div class="step-item" :class="{ active: step >= 1 }">
        <div class="circle">1</div>
        <span>기본 정보</span>
      </div>
      <div class="line" :class="{ active: step >= 2 }"></div>
      <div class="step-item" :class="{ active: step >= 2 }">
        <div class="circle">2</div>
        <span>멘토링 스타일</span>
      </div>
      <div class="line" :class="{ active: step >= 3 }"></div>
      <div class="step-item" :class="{ active: step >= 3 }">
        <div class="circle">3</div>
        <span>최종 가입</span>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-content">
      
      <!-- [STEP 1] 멘토 기본 정보 입력 + 증빙서류 -->
      <div v-if="step === 1" class="step-section fade-in">
        <h3>👨‍🏫 멘토님, 프로필을 등록해주세요</h3>
        
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
          <label>소속 (회사)</label>
          <input type="text" v-model="form.company" placeholder="예: 삼성전자, 네이버" required>
        </div>
        <div class="form-group">
          <label>직무 (부서)</label>
          <input type="text" v-model="form.team" placeholder="예: AI 개발팀, 마케팅전략팀" required>
        </div>
        <div class="form-group">
          <label>총 경력 (년)</label>
          <input type="number" v-model="form.experienceYears" min="0" placeholder="숫자만 입력" required>
        </div>
        <div class="form-group">
          <label>전문 분야 (쉼표로 구분)</label>
          <!-- 💡 [수정] 정확한 매칭을 위해 구체적 키워드 유도 -->
          <input type="text" v-model="form.topics" placeholder="예: 백엔드, Spring Boot, 리더십, 이직 상담 (기술 스택 필수)" required>
        </div>
        
        <!-- 증빙 서류 업로드 -->
        <div class="form-group upload-box">
          <label>증빙 서류 (필수)</label>
          <input type="file" @change="handleFileChange" accept=".pdf,.jpg,.png,.jpeg" />
          <p class="small-text">* 재직증명서, 명함 등 (관리자 승인용, 비공개)</p>
          <p v-if="!proofFile && showFileError" class="error-text">⚠️ 증빙 서류를 반드시 첨부해주세요.</p>
        </div>

        <div class="form-group">
          <label>자기소개 키워드 (초안)</label>
          <!-- 💡 [수정] 성과 위주의 입력을 유도하는 프롬프트 -->
          <textarea 
            v-model="form.introduction_draft" 
            rows="3" 
            placeholder="주요 경력 성과(수치), 거쳐온 회사들, 자랑하고 싶은 프로젝트 경험 등을 키워드로 나열해주세요. (AI가 이 내용을 바탕으로 프로필을 작성합니다!)"
          ></textarea>
        </div>
        
        <button type="button" class="btn-primary full-width" @click="goToStep2">
          다음 (스타일 분석) →
        </button>
      </div>

      <!-- [STEP 2] 멘토 전용 성향 질문 (AI 매칭 최적화) -->
      <div v-if="step === 2" class="step-section fade-in">
        <h3>💡 어떤 스타일의 멘토이신가요?</h3>
        <p class="sub-desc">답변을 바탕으로 멘티에게 어필할 매력적인 소개글을 만듭니다.</p>
        
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
            <span v-if="isGenerating">🤖 AI가 프로필 작성 중...</span>
            <span v-else>✨ AI 자기소개 생성하기</span>
          </button>
        </div>
      </div>

      <!-- [STEP 3] 최종 확인 -->
      <div v-if="step === 3" class="step-section fade-in">
        <h3>📝 완성된 멘토 프로필</h3>
        <p class="sub-desc">전문성이 돋보이는지 확인하고 수정해주세요.</p>

        <div class="ai-result-box">
          <label>최종 자기소개</label>
          <textarea 
            v-model="form.final_introduction" 
            rows="12" 
            class="final-textarea"
          ></textarea>
        </div>

        <div class="btn-group">
          <button type="button" class="btn-secondary" @click="step = 2">다시 생성</button>
          <button type="submit" class="btn-primary flex-grow" :disabled="isLoading">
            {{ isLoading ? '가입 처리 중...' : '✅ 멘토 가입 신청 완료' }}
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
const showFileError = ref(false);

// 폼 데이터 (멘토용)
const form = reactive({
  email: '',
  password: '',
  name: '',
  company: '',
  team: '',
  experienceYears: '',
  topics: '',
  introduction_draft: '', 
  final_introduction: '',
});

// 설문 데이터
const surveyAnswers = reactive({
  q1: '', q2: '', q3: '', q4: '', q5: ''
});

// 💡 [수정] 멘토용 핵심 5대 질문 (매칭 알고리즘 최적화)
const questions = [
  { 
    key: 'q1', 
    text: '멘티에게 줄 수 있는 가장 확실한 도움은?', 
    options: [
      '합격 노하우 전수 (서류 통과/면접 팁)', 
      '하드 스킬 코칭 (코드 리뷰/실무 기술)', 
      '커리어 로드맵 설계 (장기적 방향성)', 
      '조직 적응 가이드 (처세술/리더십)', 
      '업계 인사이트 (현장 이야기/트렌드)'
    ] 
  },
  { 
    key: 'q2', 
    text: '평소 후배를 가르칠 때 어떤 스타일인가요?', 
    options: [
      '팩트 중심 (문제점 명확히 지적)', 
      '동기 부여 (장점 찾아 자신감 UP)', 
      '솔루션 지향 (구체적 액션플랜 제시)', 
      '코칭형 (질문으로 스스로 답 찾게 함)', 
      '스토리텔러 (경험담으로 쉽게 설명)'
    ] 
  },
  { 
    key: 'q3', 
    text: '어떤 단계의 멘티와 대화가 잘 통하나요?', 
    options: [
      '완전 입문자 (비전공자/학생 기초)', 
      '성장하는 주니어 (하나를 알려주면 열을 앎)', 
      '간절한 취업 준비생 (당장 취업이 목표)', 
      '고민 많은 현직자 (실무 고충/스킬업)', 
      '경력직/이직러 (커리어 점프/시니어)'
    ] 
  },
  { 
    key: 'q4', 
    text: '커피챗을 어떻게 이끌어가고 싶으신가요?', 
    options: [
      'Q&A 해결사 (궁금증 속 시원히 해결)', 
      '면접관 모드 (실력 검증 및 피드백)', 
      '첨삭 지도 (자소서/코드 디테일 수정)', 
      '편안한 티타임 (형/누나처럼 대화)', 
      '미니 세미나 (인사이트 체계적 전달)'
    ] 
  },
  { 
    key: 'q5', 
    text: '멘토링 이후 어떤 관계를 지향하시나요?', 
    options: [
      '깔끔한 해결 (1회성 임팩트 중시)', 
      '열린 문 (언제든 편하게 연락 환영)', 
      '장기 코칭 (성장을 오래 지켜봄)', 
      '후배 양성 (배우려는 멘티에 애정)', 
      '업계 동료 (수평적 정보 공유)'
    ] 
  }
];

// 파일 선택 핸들러
const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    proofFile.value = file;
    showFileError.value = false;
  } else {
    proofFile.value = null;
  }
};

// Step 1 검증
const goToStep2 = () => {
  if (!form.email || !form.password || !form.name || !form.company || !form.topics) {
    errorMessage.value = '필수 정보를 모두 입력해주세요.';
    return;
  }
  
  if (!proofFile.value) {
    showFileError.value = true;
    errorMessage.value = '증빙 서류를 업로드해주세요.';
    return;
  }

  errorMessage.value = '';
  step.value = 2;
};

// AI 생성
const handleGenerateAI = async () => {
  if (Object.values(surveyAnswers).some(v => !v)) {
    errorMessage.value = '모든 성향 질문에 답해주세요.';
    return;
  }

  isGenerating.value = true;
  errorMessage.value = '';

  try {
    const response = await api.post('/ai/generate-intro', {
      original_intro: form.introduction_draft,
      situation: `${form.company} ${form.team} (${form.experienceYears}년차)`, 
      topics: form.topics,
      survey_answers: surveyAnswers,
      role: 'mentor' 
    });

    form.final_introduction = response.data.generated_text;
    step.value = 3;
  } catch (error) {
    console.error('AI 생성 실패:', error);
    errorMessage.value = 'AI 생성 중 오류가 발생했습니다.';
  } finally {
    isGenerating.value = false;
  }
};

// 최종 가입
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
    formData.append('company', form.company);
    formData.append('team', form.team);
    formData.append('experienceYears', form.experienceYears || 0);
    formData.append('topics', form.topics);
    formData.append('introduction', form.final_introduction);
    
    // (임시 위치값)
    formData.append('latitude', '37.5665');
    formData.append('longitude', '126.9780');

    if (proofFile.value) {
      formData.append('proofFile', proofFile.value);
    }

    await authStore.registerMentor(formData);
    
    alert('멘토 가입 신청이 완료되었습니다. 관리자 승인 후 활동 가능합니다.');
    router.push({ name: 'login' });

  } catch (error) {
    console.error('가입 실패:', error);
    const detail = error.response?.data?.detail;
    errorMessage.value = `가입 실패: ${typeof detail === 'object' ? JSON.stringify(detail) : detail || error.message}`;
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* 동일한 스타일 유지 */
.register-form-container {
  max-width: 600px;
  margin: 40px auto;
  padding: 0 20px;
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 40px;
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
.step-item.active { color: #8B4513; font-weight: 700; }
.circle {
  width: 32px; height: 32px; border-radius: 50%;
  background-color: #e5e7eb; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: bold; margin-bottom: 6px; transition: background-color 0.3s;
}
.step-item.active .circle { background-color: #8B4513; }
.line {
  flex-grow: 1; height: 2px; background-color: #e5e7eb;
  margin: 0 10px; margin-bottom: 20px; position: relative; top: -13px; z-index: 1;
}
.line.active { background-color: #8B4513; }

.form-content {
  background: white; padding: 30px; border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #f3f4f6;
}

h3 { font-size: 22px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }
.sub-desc { color: #6b7280; font-size: 14px; margin-bottom: 24px; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-weight: 600; margin-bottom: 8px; color: #374151; font-size: 14px; }
input, textarea, select {
  width: 100%; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px;
  font-size: 15px; outline: none; transition: border-color 0.2s; box-sizing: border-box;
}
input:focus, textarea:focus, select:focus { border-color: #8B4513; box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1); }

.btn-primary {
  background-color: #8B4513; color: white; border: none; padding: 14px;
  border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background-color 0.2s;
}
.btn-primary:hover:not(:disabled) { background-color: #6B3410; }
.btn-primary:disabled { background-color: #cbd5e1; cursor: not-allowed; }

.btn-secondary {
  background-color: #f3f4f6; color: #4b5563; border: none; padding: 14px 20px;
  border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer;
}
.btn-secondary:hover { background-color: #e5e7eb; }

.full-width { width: 100%; }
.flex-grow { flex-grow: 1; }
.btn-group { display: flex; gap: 12px; margin-top: 30px; }

.survey-list { display: flex; flex-direction: column; gap: 20px; }
.q-label { display: block; font-weight: 600; margin-bottom: 8px; color: #111; }

.final-textarea { background-color: #FFF8F0; border-color: #F5E6D3; line-height: 1.6; }
.error-msg { color: #dc2626; margin-top: 20px; text-align: center; font-size: 14px; font-weight: 500; }
.error-text { color: #dc2626; font-size: 13px; margin-top: 5px; }
.fade-in { animation: fadeIn 0.3s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

.upload-box {
  background-color: #f9fafb;
  padding: 15px;
  border-radius: 8px;
  border: 1px dashed #d1d5db;
}
.small-text {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}
</style>