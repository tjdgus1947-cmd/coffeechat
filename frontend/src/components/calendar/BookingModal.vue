<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <button @click="$emit('close')" class="close-button" aria-label="닫기">X</button>
      
      <h3>커피챗 예약하기</h3>
      <p v-if="mentorName" class="mentor-info">
        <strong>{{ mentorName }}</strong> 멘토님과의 1:1 커피챗
      </p>
      
      <BookingCalendar 
        :mentor-id="mentorId"
        @booking-confirmed="handleBookingConfirmed" 
      />
    </div>
  </div>
</template>

<script setup>
// 3단계에서 만든 파일을 임포트
import BookingCalendar from './BookingCalendar.vue';

defineProps({
  show: {
    type: Boolean,
    required: true,
  },
  mentorId: String,
  mentorName: String,
});

const emit = defineEmits(['close', 'booking-confirmed']);

const handleBookingConfirmed = () => {
  // BookingCalendar에서 예약이 완료되면,
  // 이 모달을 닫도록 부모(NetworkView)에게 알립니다.
  emit('booking-confirmed');
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
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
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

.close-button:hover {
  color: #333;
}

.mentor-info {
  font-size: 16px;
  color: #333;
  margin-bottom: 20px;
}

h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
}
</style>