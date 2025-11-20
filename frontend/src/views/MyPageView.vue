<template>
  <div class="page-container">
    <div class="content-wrapper">
      <div class="header-section">
        <h1>마이페이지</h1>
        <p>프로필과 위치 정보를 관리하세요</p>
      </div>

      <div class="main-grid">
        
        <aside class="left-column">
          <div class="card profile-card">
            <div class="profile-header">
              <div class="avatar-circle">
                {{ authStore.userName?.charAt(0) || '유' }}
                <span class="role-badge">
                  {{ authStore.userRole === 'mentee' ? '멘티' : '멘토' }}
                </span>
              </div>
              <h2>{{ authStore.userName || '사용자' }}</h2>
              
              <div class="profile-info">
                <p><span class="icon">👤</span> {{ authStore.userName }}</p>
                <p><span class="icon">🆔</span> {{ authStore.userRole === 'mentee' ? '멘티' : '멘토' }}</p>
                <div class="id-box">
                  <span class="icon">🔑</span> {{ authStore.userId }}
                </div>
              </div>
            </div>

            <div class="intro-section">
              <label>자기소개</label>
              <p class="sub-text">AI 매칭도에 반영됩니다</p>
              
              <div v-if="isLoadingIntro" class="loading-box">
                로딩 중...
              </div>
              
              <div v-else>
                <textarea
                  v-model="selfIntroText"
                  placeholder="경력, 관심사, 현재 상황 등을 입력해주세요."
                  rows="8"
                ></textarea>
                <button 
                  @click="handleUpdateProfile" 
                  :disabled="isUpdating || !selfIntroText.trim()"
                  class="purple-btn"
                >
                  {{ isUpdating ? '저장 중...' : '프로필 수정' }}
                </button>
                <p v-if="updateSuccess" class="msg success">✅ 저장되었습니다!</p>
                <p v-if="updateError" class="msg error">❌ {{ updateError }}</p>
              </div>
            </div>
          </div>
        </aside>

        <main class="right-column">
          
          <div class="card location-card">
            <div class="card-header">
               <h3>📍 나의 위치 정보 설정</h3>
            </div>
            <LocationUpdater />
          </div>

          <div class="card schedule-card" v-if="authStore.userRole === 'mentor'">
            <div class="card-header">
              <h3>📅 내 일정 관리</h3>
            </div>
            <MentorAvailability />
          </div>

        </main>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api';

// 컴포넌트 import (BookingList 삭제됨)
import LocationUpdater from '@/components/profile/LocationUpdater.vue';
import MentorAvailability from '@/components/profile/MentorAvailability.vue';

const authStore = useAuthStore();

const selfIntroText = ref('');
const isLoadingIntro = ref(false);
const isUpdating = ref(false);
const updateSuccess = ref(false);
const updateError = ref(null);

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
    } finally {
      isLoadingIntro.value = false;
    }
  }
});

async function handleUpdateProfile() {
  if (!selfIntroText.value.trim()) return;
  
  isUpdating.value = true;
  updateSuccess.value = false;
  updateError.value = null;

  try {
    await api.post('/profile/update-introduction', {
      user_id: authStore.userId,
      role: authStore.userRole,
      introduction_text: selfIntroText.value
    });
    updateSuccess.value = true;
    setTimeout(() => { updateSuccess.value = false; }, 3000);
  } catch (error) {
    updateError.value = '업데이트 실패';
  } finally {
    isUpdating.value = false;
  }
}
</script>

<style scoped>
/* 전체 레이아웃 설정 */
.page-container {
  min-height: 100vh;
  background-color: #f9fafb;
  padding: 40px 20px;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
}

/* 헤더 스타일 */
.header-section {
  margin-bottom: 30px;
}
.header-section h1 {
  font-size: 28px;
  font-weight: 700;
  color: #111;
  margin-bottom: 8px;
}
.header-section p {
  color: #666;
}

/* 그리드 레이아웃 */
.main-grid {
  display: grid;
  grid-template-columns: 340px 1fr; /* 왼쪽 고정, 오른쪽 가변 */
  gap: 24px;
  align-items: start;
}

/* 반응형 */
@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

/* 카드 공통 스타일 */
.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.03);
  border: 1px solid #f3f4f6;
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.card-header h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
}

/* --- 왼쪽 프로필 스타일 --- */
.profile-header {
  text-align: center;
  margin-bottom: 30px;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  background-color: #8b5cf6;
  color: white;
  font-size: 36px;
  font-weight: bold;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
  position: relative;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.role-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background-color: #7c3aed;
  border: 3px solid white;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 20px;
  font-weight: 600;
}

.profile-header h2 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
}

.profile-info {
  text-align: left;
  background-color: #f9fafb;
  padding: 16px;
  border-radius: 12px;
}

.profile-info p {
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
}

.id-box {
  font-size: 12px;
  color: #9ca3af;
  word-break: break-all;
  margin-top: 4px;
}

.icon { margin-right: 6px; }

/* --- 자기소개 폼 스타일 --- */
.intro-section {
  border-top: 1px solid #eee;
  padding-top: 20px;
}

.intro-section label {
  display: block;
  font-weight: 700;
  margin-bottom: 4px;
  color: #333;
}

.sub-text {
  font-size: 12px;
  color: #888;
  margin-bottom: 12px;
}

textarea {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  margin-bottom: 12px;
  outline: none;
  transition: border 0.2s;
}
textarea:focus {
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
}

.purple-btn {
  width: 100%;
  background-color: #8b5cf6;
  color: white;
  border: none;
  padding: 12px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.purple-btn:hover:not(:disabled) {
  background-color: #7c3aed;
}
.purple-btn:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}

.msg {
  margin-top: 10px;
  font-size: 13px;
  font-weight: 500;
}
.success { color: #10b981; }
.error { color: #ef4444; }

/* --- 오른쪽 기능 영역 --- */
.right-column {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
</style>