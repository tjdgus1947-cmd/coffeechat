<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button @click="$emit('close')" class="close-button" aria-label="닫기">X</button>
      
      <h3>커피챗 신청하기</h3>
      <p v-if="mentorName" class="mentor-info">
        <strong>{{ mentorName }}</strong> 멘토님에게
        1:1 커피챗을 신청하시겠습니까?
      </p>
      
      <div class="notice">
        <p>✅ 신청이 수락되면, 멘토님과 직접 시간과 장소(대면/비대면)를 조율하게 됩니다.</p>
      </div>

      <textarea 
        v-model="message"
        class="message-input"
        placeholder="멘토님에게 간단한 자기소개나 궁금한 점을 남겨주세요. (선택)"
      />

      <button 
        @click="confirmBookingRequest" 
        :disabled="isSubmitting"
        class="confirm-button"
      >
        {{ isSubmitting ? '신청 중...' : '신청 보내기' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
// import BookingCalendar from './BookingCalendar.vue'; // <-- 삭제

const props = defineProps({
  show: Boolean,
  mentorId: String,
  mentorName: String,
});
const emit = defineEmits(['close', 'booking-confirmed']);

const isSubmitting = ref(false);
const message = ref(''); // (신규) 멘티가 남길 메시지

// (수정) 예약 확정 함수
const confirmBookingRequest = async () => {
  isSubmitting.value = true;
  try {
    // (wbs_detail.md) 실제 API 호출: POST /api/matching/request (가상)
    // await api.post('/api/matching/request', {
    //   mentorId: props.mentorId,
    //   message: message.value,
    // });
    
    // 백엔드가 없으므로, 1초간 '신청 중...'을 보여주고 성공 처리
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log('(가짜) 커피챗 신청 완료:', {
      mentorId: props.mentorId,
      message: message.value,
    });
    
    alert('커피챗 신청이 완료되었습니다. 멘토의 연락을 기다려주세요.');
    emit('booking-confirmed'); // 부모(NetworkView)에게 완료 이벤트 전달

  } catch (error) {
    console.error('신청 실패:', error);
    alert('신청에 실패했습니다. 다시 시도해주세요.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  min-width: 400px;
  max-width: 90vw;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  position: relative;
}
.close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
}
.mentor-info {
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 15px;
}
.notice {
  background-color: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 15px;
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 15px;
}
.message-input {
  width: 100%;
  min-height: 80px;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box; /* padding이 width를 넘지 않게 */
  resize: vertical;
  margin-bottom: 15px;
  font-family: inherit;
}
.confirm-button {
  width: 100%;
  padding: 12px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: bold;
}
.confirm-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>