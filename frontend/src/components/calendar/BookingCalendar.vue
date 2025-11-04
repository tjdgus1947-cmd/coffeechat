<template>
  <div class="calendar-container">
    <div v-if="isLoading" class="loading-spinner">
      <p>예약 가능한 시간을 불러오는 중...</p>
    </div>
    
    <div v-else>
      <!-- v-calendar 플러그인이 필요합니다 (npm install v-calendar) -->
      <v-date-picker
        v-model="selectedDate"
        :min-date="new Date()"
        :attributes="calendarAttributes"
        title-position="left"
        trim-weeks
      />

      <div v-if="selectedDate" class="time-slots">
        <h4>선택 가능한 시간</h4>
        <div v-if="availableTimesForSelectedDate.length > 0" class="slots-grid">
          <button
            v-for="time in availableTimesForSelectedDate"
            :key="time"
            @click="selectedTime = time"
            :class="{ selected: selectedTime === time }"
            class="slot-button"
          >
            {{ time }}
          </button>
        </div>
        <p v-else class="no-slots">
          아쉽지만, 이 날짜에는 예약 가능한 시간이 없습니다.
        </p>
      </div>

      <button 
        @click="confirmBooking" 
        :disabled="!selectedDate || !selectedTime || isSubmitting"
        class="confirm-button"
      >
        {{ isSubmitting ? '예약 중...' : '이 시간으로 예약 확정' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
// (v-calendar 임포트가 필요할 수 있습니다)
// import 'v-calendar/style.css'; 

const props = defineProps({
  mentorId: String,
});
const emit = defineEmits(['booking-confirmed']);

// --- 1. State (변수) ---
const isLoading = ref(true);
const isSubmitting = ref(false);
const selectedDate = ref(null); 
const selectedTime = ref(null); 

// ⭐️ (가짜 데이터) 멘토가 막아놓은 날짜/시간
const mockDisabledDates = ref([
  { repeat: { weekdays: [1, 7] } }, 
  new Date(2025, 10, 20),
]);
const mockAvailableSlots = ref({
  '2025-11-18': ['14:00', '15:00', '16:00'],
  '2025-11-19': ['10:00', '11:00'],
  '2025-11-21': ['14:00', '15:00'],
});

// --- 2. Computed (계산된 속성) ---
const calendarAttributes = computed(() => {
  return [
    {
      key: 'disabled',
      dates: mockDisabledDates.value,
      popover: { label: '예약 불가능' },
      highlight: { color: 'gray', fillMode: 'light' },
      order: 100 
    },
    {
      key: 'available',
      dates: Object.keys(mockAvailableSlots.value).map(d => new Date(d)),
      dot: { color: 'purple' },
    }
  ];
});

const availableTimesForSelectedDate = computed(() => {
  if (!selectedDate.value) return [];
  const key = selectedDate.value.toISOString().split('T')[0];
  return mockAvailableSlots.value[key] || [];
});

// --- 3. Functions (함수) ---

// (가짜) 데이터 로드
onMounted(() => {
  isLoading.value = true;
  setTimeout(() => {
    console.log(`(가짜) ${props.mentorId} 멘토의 전체 시간표 로드`);
    isLoading.value = false;
  }, 500);
});

// (가짜) 예약 확정 함수
const confirmBooking = async () => {
  if (!selectedDate.value || !selectedTime.value) {
    alert('날짜와 시간을 모두 선택해주세요.');
    return;
  }
  isSubmitting.value = true;

  const [hours, minutes] = selectedTime.value.split(':');
  const finalBookingDateTime = new Date(selectedDate.value);
  finalBookingDateTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);

  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    console.log('(가짜) 예약 완료:', {
      mentorId: props.mentorId,
      dateTime: finalBookingDateTime.toISOString(), 
    });
    
    alert('예약이 완료되었습니다.');
    emit('booking-confirmed'); 

  } catch (error) {
    console.error('예약 실패:', error);
    alert('예약에 실패했습니다. 다시 시도해주세요.');
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<style scoped>
:deep(.vc-container) {
  border: none;
  border-radius: 0;
  width: 100%;
}

:deep(.vc-header) {
  margin-bottom: 10px;
}

:deep(.vc-title) {
  font-size: 1.1rem;
  font-weight: bold;
}

:deep(.vc-weekday) {
  color: #666;
}

:deep(.vc-day.is-today .vc-day-content) {
  background-color: #f0ebff;
  color: #6d28d9;
}

:deep(.vc-day-content:focus) {
  background-color: #6d28d9;
  color: #fff;
}

:deep(.vc-day.is-disabled .vc-day-content) {
  color: #ccc;
  text-decoration: line-through;
  pointer-events: none;
}

.time-slots {
  margin-top: 20px;
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.time-slots h4 {
  font-weight: bold;
  margin-bottom: 10px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 10px;
}

.slot-button {
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background-color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.slot-button:hover {
  border-color: #6d28d9;
}

.slot-button.selected {
  background-color: #6d28d9;
  color: white;
  font-weight: bold;
  border-color: #6d28d9;
}

.no-slots {
  color: #777;
  font-size: 0.9rem;
}

.confirm-button {
  width: 100%;
  margin-top: 20px;
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

.loading-spinner {
  text-align: center;
  padding: 20px;
  color: #666;
}
</style>