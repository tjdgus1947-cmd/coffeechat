<template>
  <div>
    <h1>마이페이지</h1>
    <div v-if="authStore.isAuthenticated">
      <h2>{{ authStore.user.name }}님 환영합니다.</h2>
      <p>역할: {{ authStore.user.role }}</p>
      
      <MenteeProfileForm v-if="authStore.userRole === 'mentee'" />
      <MentorProfileForm v-if="authStore.userRole === 'mentor'" />
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/store/auth';
// MenteeProfileForm, MentorProfileForm은 멘티/멘토가
// 자신의 상황, 경력 등을 수정하는 컴포넌트입니다. (생성 필요)
// import MenteeProfileForm from '@/components/profile/MenteeProfileForm.vue';
// import MentorProfileForm from '@/components/profile/MentorProfileForm.vue';

const authStore = useAuthStore();
</script>