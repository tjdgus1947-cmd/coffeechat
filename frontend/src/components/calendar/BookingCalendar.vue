<template>
  <div class="calendar-container">
    <div v-if="isLoading" class="loading-spinner">
      <p>예약 가능한 시간을 불러오는 중...</p>
    </div>
    
    <div v-else>
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
            :key="time.slotId" 
            @click="selectTimeSlot(time)" 
            :class="{ selected: selectedTimeSlot?.slotId === time.slotId }"
            class="slot-button"
          >
            {{ time.timeLabel }}
          </button>
        </div>
        <p v-else class="no-slots">
          아쉽지만, 이 날짜에는 예약 가능한 시간이 없습니다.
        </p>
      </div>

      <button 
        @click="confirmBooking" 
        :disabled="!selectedDate || !selectedTimeSlot || isSubmitting" 
        class="confirm-button"
      >
        {{ isSubmitting ? '예약 중...' : '이 시간으로 예약 확정' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api';

const props = defineProps({
  mentorId: String,
});
const emit = defineEmits(['booking-confirmed']);

// --- 1. State (변수) ---
const isLoading = ref(true);
const isSubmitting = ref(false);
const selectedDate = ref(null); 
const selectedTimeSlot = ref(null); 
const availableSlotsMap = ref({});

// --- 2. Computed (계산된 속성) ---
const calendarAttributes = computed(() => {
  return [
    {
      key: 'available',
      dates: Object.keys(availableSlotsMap.value).map(d => new Date(d)),
      dot: { color: 'purple' },
    }
  ];
});

const availableTimesForSelectedDate = computed(() => {
  if (!selectedDate.value) return [];
  const key = selectedDate.value.toISOString().split('T')[0];
  return availableSlotsMap.value[key] || [];
});

// --- 3. Functions (함수) ---

function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function formatDate(isoString) {
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function processSlots(slots) {
  const map = {};
  slots.forEach(slot => {
    const dateKey = formatDate(slot.start_time);
    const timeLabel = formatTime(slot.start_time);
    
    if (!map[dateKey]) {
      map[dateKey] = [];
    }
    
    map[dateKey].push({
      slotId: slot.id,
      timeLabel: timeLabel 
    });
  });
  return map;
}

async function fetchAvailability() {
  if (!props.mentorId) return;
  isLoading.value = true;
  try {
    const response = await api.get(`/availability/${props.mentorId}`);
    availableSlotsMap.value = processSlots(response.data);
    console.log(`멘토(${props.mentorId})의 ${response.data.length}개 슬롯 로드 완료`);
  } catch(e) {
    console.error("멘토 가능 시간 로딩 실패:", e);
    availableSlotsMap.value = {};
  } finally {
    isLoading.value = false;
  }
}

function selectTimeSlot(timeSlot) {
  selectedTimeSlot.value = timeSlot;
}

onMounted(() => {
  fetchAvailability();
});

const confirmBooking = async () => {
  if (!selectedTimeSlot.value) { 
    alert('시간을 선택해주세요.');
    return;
  }
  
  isSubmitting.value = true;
  try {
    await api.post('/bookings/create', {
      mentor_id: props.mentorId,
      availability_slot_id: selectedTimeSlot.value.slotId
    });
    
    alert('예약 신청이 완료되었습니다. 멘토의 승인을 기다려주세요.');
    emit('booking-confirmed');

    fetchAvailability(); 
    selectedDate.value = null;
    selectedTimeSlot.value = null;

  } catch (error) {
    console.error('예약 신청 실패:', error);
    let detail = error.message;
    if (error.response?.data?.detail) {
      const errorDetail = error.response.data.detail;
      if (typeof errorDetail === 'object') {
        detail = JSON.stringify(errorDetail);
      } else {
        detail = errorDetail;
      }
    }
    alert('예약 신청에 실패했습니다: ' + detail);
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
:deep(.vc-header) { margin-bottom: 10px; }
:deep(.vc-title) { font-size: 1.1rem; font-weight: bold; }
:deep(.vc-weekday) { color: #666; }
:deep(.vc-day.is-today .vc-day-content) { background-color: #f0ebff; color: #6d28d9; }
:deep(.vc-day-content:focus) { background-color: #6d28d9; color: #fff; }
:deep(.vc-day.is-disabled .vc-day-content) { color: #ccc; text-decoration: line-through; pointer-events: none; }
.time-slots { margin-top: 20px; border-top: 1px solid #eee; padding-top: 15px; }
.time-slots h4 { font-weight: bold; margin-bottom: 10px; }
.slots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 10px; }
.slot-button { padding: 8px 10px; border: 1px solid #ccc; border-radius: 6px; background-color: #fff; cursor: pointer; transition: all 0.2s; }
.slot-button:hover { border-color: #6d28d9; }
.slot-button.selected { background-color: #6d28d9; color: white; font-weight: bold; border-color: #6d28d9; }
.no-slots { color: #777; font-size: 0.9rem; }
.confirm-button { width: 100%; margin-top: 20px; padding: 12px; background-color: #6d28d9; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; }
.confirm-button:disabled { background-color: #ccc; cursor: not-allowed; }
.loading-spinner { text-align: center; padding: 20px; color: #666; }
</style>