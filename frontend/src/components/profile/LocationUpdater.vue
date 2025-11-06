<template>
  <div class="location-updater-card">
    <h3>나의 위치 정보 설정 (PostGIS)</h3>
    <p class="description">
      지리적 매칭도(거리 30%)를 계산하기 위해 위치 정보가 필요합니다. 
      (나중에는 Google Maps UI로 대체됩니다.)
    </p>

    <form @submit.prevent="handleUpdateLocation" class="location-form">
      <div class="input-group">
        <label for="latitude">위도 (Latitude)</label>
        <input type="number" id="latitude" v-model.number="lat" step="0.000001" required>
      </div>
      
      <div class="input-group">
        <label for="longitude">경도 (Longitude)</label>
        <input type="number" id="longitude" v-model.number="lon" step="0.000001" required>
      </div>

      <button type="submit" :disabled="isLoading">
        {{ isLoading ? '업데이트 중...' : '위치 정보 업데이트' }}
      </button>
    </form>
    
    <p v-if="message" :class="messageType">{{ message }}</p>

    <p class="hint">
      테스트 값 추천: 서울 강남역 근처 (위도: 37.4979, 경도: 127.0276)
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/store/auth';
import userService from '@/services/userService'; // 1.1에서 만든 서비스 임포트

const authStore = useAuthStore();
const isLoading = ref(false);
const message = ref('');
const messageType = ref('');

// 테스트를 위한 초기값 (서울 강남역)
const lat = ref(37.4979); 
const lon = ref(127.0276);

const handleUpdateLocation = async () => {
  if (!authStore.userId || !authStore.userRole) {
    message.value = '오류: 사용자 정보가 유효하지 않습니다.';
    messageType.value = 'error';
    return;
  }
  
  isLoading.value = true;
  message.value = '';
  
  try {
    await userService.updateLocation(
      authStore.userId,
      authStore.userRole,
      lon.value,
      lat.value
    );
    
    message.value = '위치 정보가 성공적으로 업데이트되었습니다!';
    messageType.value = 'success';

  } catch (error) {
    console.error('위치 업데이트 실패:', error);
    message.value = '위치 업데이트에 실패했습니다. 콘솔을 확인해주세요.';
    messageType.value = 'error';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
.location-updater-card {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
  margin-top: 20px;
}
h3 {
  margin-top: 0;
  font-size: 1.2rem;
}
.description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 15px;
}
.location-form {
  display: flex;
  gap: 15px;
  align-items: flex-end;
}
.input-group {
  flex-grow: 1;
}
.input-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}
.input-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  padding: 10px 15px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}
button:disabled {
  background-color: #ccc;
}
.success {
  color: green;
  font-weight: bold;
  margin-top: 10px;
}
.error {
  color: red;
  font-weight: bold;
  margin-top: 10px;
}
.hint {
    font-size: 0.8rem;
    color: #999;
    margin-top: 10px;
}
</style>