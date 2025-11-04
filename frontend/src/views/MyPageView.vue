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
          <strong>아이디(Test):</strong> {{ authStore.userId }}
        </div>
        <button class="edit-button">프로필 수정 (구현 필요)</button>
      </div>
    </div>

    <div class="requests-card card" v-if="authStore.userRole === 'mentee'">
      <h2>커피챗 신청 목록</h2>
      <p>내가 멘토에게 보낸 신청 현황입니다.</p>
      <!-- (BookingList 컴포넌트가 없어서 임시 주석 처리) -->
      <!-- <BookingList /> -->
    </div>
    
    <div class="requests-card card" v-if="authStore.userRole === 'mentor'">
      <h2>받은 커피챗 신청</h2>
      <p>멘티들이 나에게 보낸 신청 현황입니다.</p>
    </div>

  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
// import BookingList from '@/components/profile/BookingList.vue';

const authStore = useAuthStore();
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

.edit-button {
  margin-top: 15px;
  padding: 8px 12px;
  background-color: #f0f0f0;
  border: 1px solid #ccc;
  border-radius: 6px;
  cursor: pointer;
}

.edit-button:hover {
  background-color: #e0e0e0;
}

.requests-card {
  margin-top: 20px;
}
</style>