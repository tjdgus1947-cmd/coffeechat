<template>
<div class="mypage-container">
    <h1>마이페이지</h1>

    <div class="profile-card card">
      <h2>내 프로필</h2>
      <div v-if="authStore.user">
        <div class="profile-item" v-if="authStore.userName">
          <strong>이름:</strong>
          {{ authStore.userName }}
        </div>
        <div class="profile-item" v-if="authStore.userRole">
          <strong>역할:</strong>
          {{ authStore.userRole === 'mentee' ? '멘티' : '멘토' }}
        </div>
        <div class="profile-item">
          <strong>아이디(Test):</strong>
          {{ authStore.userId }}
        </div>
        
        <div class="profile-update-section">
          <label for="selfIntro">
            자기소개 (AI 매칭도에 반영됩니다)
          </label>
          <div v-if="isLoadingIntro">
            <p>자기소개 로딩 중...</p>
          </div>
          <textarea 
            v-else
            id="selfIntro"
            v-model="selfIntroText" 
            placeholder="멘티/멘토에게 자신을 어필할 수 있는 자기소개, 현재 상황, 경력 등을 입력하세요."
            rows="8"
          ></textarea>
          <button @click="handleUpdateProfile" :disabled="isUpdating" class="update-button">
            {{ isUpdating ? '저장 중...' : '자기소개 저장 (임베딩 갱신)' }}
          </button>
          <p v-if="updateSuccess" class="success-message">
            ✅ 성공적으로 업데이트되었습니다!
          </p>
          <p v-if="updateError" class="error-message">
            ❌ {{ updateError }}
          </p>
        </div>
        </div>
    </div>

    <div class="requests-card card" v-if="authStore.userRole === 'mentee'">
      <h2>커피챗 신청 목록</h2>
      <p>내가 멘토에게 보낸 신청 현황입니다.</p>
      <BookingList />
    </div>
    
    <div class="requests-card card" v-if="authStore.userRole === 'mentor'">
      <h2>받은 커피챗 신청</h2>
      <p>멘티들이 나에게 보낸 신청 현황입니다.</p>
      <MentorRequestList />
   </div>

    <div class="schedule-card card" v-if="authStore.userRole === 'mentor'">
        <h2>내 일정 관리</h2>
        <p>멘티가 예약할 수 있는 시간을 등록/관리합니다.</p>
        <MentorAvailability />
    </div>

    <LocationUpdater />
  </div>
</template>

<script setup>
// ⭐️ 2. onMounted와 ref를 추가합니다.
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import LocationUpdater from '@/components/profile/LocationUpdater.vue';
import MentorRequestList from '@/components/profile/MentorRequestList.vue';
import BookingList from '@/components/profile/BookingList.vue';
import MentorAvailability from '@/components/profile/MentorAvailability.vue';
// ⭐️ 3. auth.js에서 사용한 'api' (axios)를 가져옵니다.
import api from '@/services/api'; 

const authStore = useAuthStore();
// (isProfileModalOpen은 사용되지 않아 삭제)

// ⭐️ 4. 자기소개 수정 폼을 위한 변수들
const selfIntroText = ref('');
const isLoadingIntro = ref(false);
const isUpdating = ref(false);
const updateSuccess = ref(false);
const updateError = ref(null);

// ⭐️ 5. (중요) 페이지가 로드될 때, 1단계에서 만든 API를 호출해
//         현재 자기소개를 불러옵니다.
onMounted(async () => {
  if (authStore.userId && authStore.userRole) {
    isLoadingIntro.value = true;
    try {
      const response = await api.get('/profile/introduction', {
        params: {
          user_id: authStore.userId,
          role: authStore.userRole
        }
      });
      selfIntroText.value = response.data.introduction_text || '';
    } catch (err) {
      console.error("자기소개 로드 실패:", err);
      updateError.value = "자기소개 정보를 불러오는 데 실패했습니다.";
    } finally {
      isLoadingIntro.value = false;
    }
  }
});

// ⭐️ 6. "자기소개 저장" 버튼이 호출할 함수
async function handleUpdateProfile() {
  if (!selfIntroText.value.trim()) {
    updateError.value = "자기소개를 입력해주세요.";
    return;
  }
  
  isUpdating.value = true;
  updateSuccess.value = false;
  updateError.value = null;

  try {
    // ⭐️ 7. 1단계에서 만든 API를 호출합니다.
    await api.post('/profile/update-introduction', {
      user_id: authStore.userId,
      role: authStore.userRole,
      introduction_text: selfIntroText.value // ⭐️ textarea의 텍스트를 전송
    });
    
    updateSuccess.value = true; // 성공!

  } catch (error) {
    console.error('프로필 업데이트 실패:', error);
    updateError.value = error.response?.data?.detail || '업데이트 중 오류가 발생했습니다.';
  } finally {
    isUpdating.value = false;
  }
}
</script>

<style scoped>
.mypage-container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  margin-bottom: 20px;
}

.card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.profile-item {
  margin-bottom: 10px;
  font-size: 1.1rem;
}

.profile-item strong {
  display: inline-block;
  width: 100px;
  color: #555;
}

/* ⭐️ 8. 새로 추가된 폼 스타일 */
.profile-update-section {
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}
.profile-update-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 1.1rem;
}
.profile-update-section textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
  line-height: 1.6;
  resize: vertical; /* 세로 크기만 조절 가능 */
}
.update-button { /* ⭐️ 기존 edit-button 대신 새 스타일 */
  margin-top: 12px;
  padding: 10px 16px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.update-button:hover:not(:disabled) {
  background-color: #5b21b6;
}
.update-button:disabled {
  background-color: #ccc;
}
.success-message {
  color: green;
  margin-top: 10px;
}
.error-message {
  color: red;
  margin-top: 10px;
}
/* ⭐️ 8. 여기까지 ⭐️ */

.requests-card {
  margin-top: 20px;
}

.schedule-card {
  margin-top: 20px;
}
</style>