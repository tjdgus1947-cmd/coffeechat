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
            :key="time.slotId" @click="selectTimeSlot(time)" :class="{ selected: selectedTimeSlot?.slotId === time.slotId }"
            class="slot-button"
          >
            {{ time.timeLabel }} </button>
        </div>
        <p v-else class="no-slots">
          아쉽지만, 이 날짜에는 예약 가능한 시간이 없습니다.
        </p>
      </div>

      <button 
        @click="confirmBooking" 
        :disabled="!selectedDate || !selectedTimeSlot || isSubmitting" class="confirm-button"
      >
        {{ isSubmitting ? '예약 중...' : '이 시간으로 예약 확정' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '@/services/api'; // ⭐️ (신규) API 임포트

// import 'v-calendar/style.css'; 

const props = defineProps({
  mentorId: String,
});
const emit = defineEmits(['booking-confirmed']);

// --- 1. State (변수) ---
const isLoading = ref(true);
const isSubmitting = ref(false);
const selectedDate = ref(null); 
// (수정) 단순 '14:00'이 아닌, { slotId: 1, timeLabel: '14:00' } 객체를 저장
const selectedTimeSlot = ref(null); 

// ⭐️ (신규) API 응답을 v-calendar 형식으로 가공한 맵
// 형식: {'2025-11-18': [{ slotId: 1, timeLabel: '14:00' }, ...]}
const availableSlotsMap = ref({});

// --- (삭제) ---
// const mockDisabledDates = ref([...]);
// const mockAvailableSlots = ref({...});

// --- 2. Computed (계산된 속성) ---
const calendarAttributes = computed(() => {
  return [
    {
      key: 'available',
      // (수정) 'availableSlotsMap'의 key (날짜) 목록을 달력에 점으로 표시
      dates: Object.keys(availableSlotsMap.value).map(d => new Date(d)),
      dot: { color: 'purple' },
    }
    // (참고) 멘토가 등록한 '휴무일' API가 있다면 'disabled' dates로 추가 가능
  ];
});

const availableTimesForSelectedDate = computed(() => {
  if (!selectedDate.value) return [];
  // (수정) 날짜 키를 'YYYY-MM-DD' 형식으로 변환
  const key = selectedDate.value.toISOString().split('T')[0];
  // (수정) 맵에서 해당 날짜의 시간 슬롯 배열을 반환
  return availableSlotsMap.value[key] || [];
});

// --- 3. Functions (함수) ---

// ⭐️ (신규) ISO 날짜 문자열을 '14:00' 형식으로 바꾸는 헬퍼
function formatTime(isoString) {
  const date = new Date(isoString);
  return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
}
// ⭐️ (신규) ISO 날짜 문자열을 'YYYY-MM-DD' 형식으로 바꾸는 헬퍼
function formatDate(isoString) {
  const date = new Date(isoString);
  return date.toISOString().split('T')[0];
}

// ⭐️ (신규) API 응답을 가공하여 availableSlotsMap을 채우는 함수
function processSlots(slots) {
  const map = {};
  slots.forEach(slot => {
    const dateKey = formatDate(slot.start_time);
    const timeLabel = formatTime(slot.start_time);
    
    if (!map[dateKey]) {
      map[dateKey] = [];
    }
    
    map[dateKey].push({
      slotId: slot.id, // ⭐️ DB의 'mentor_availability' 테이블 'id'
      timeLabel: timeLabel 
    });
  });
  return map;
}

// (수정) 실제 데이터 로드
async function fetchAvailability() {
  if (!props.mentorId) return;
  isLoading.value = true;
  try {
    // ⭐️ (신규) 백엔드 API (availability.py) 호출
    const response = await api.get(`/availability/${props.mentorId}`);
    
    // ⭐️ (신규) API 응답 (slot 목록)을 캘린더용 맵으로 가공
    availableSlotsMap.value = processSlots(response.data);
    
    console.log(`멘토(${props.mentorId})의 ${response.data.length}개 슬롯 로드 완료`);
  } catch(e) {
    console.error("멘토 가능 시간 로딩 실패:", e);
    availableSlotsMap.value = {}; // 실패 시 비우기
  } finally {
    isLoading.value = false;
  }
}

// ⭐️ (신규) 시간 버튼 클릭 시
function selectTimeSlot(timeSlot) {
  selectedTimeSlot.value = timeSlot;
}

onMounted(() => {
  // (수정) 가짜 setTimeout 대신 실제 fetch 함수 호출
  fetchAvailability();
});

// (가짜) 예약 확정 함수
const confirmBooking = async () => {
  if (!selectedTimeSlot.value) { // (수정)
    alert('시간을 선택해주세요.');
    return;
  }
  
  // ⭐️ (다음 단계)
  // 이 함수는 5단계에서 '실제 예약 API'를 호출하도록 수정되어야 합니다.
  
  isSubmitting.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000)); // 가짜 딜레이
    
    console.log('⭐️ (가짜) 예약 시도:', {
      mentorId: props.mentorId,
      availabilitySlotId: selectedTimeSlot.value.slotId, // ⭐️ DB에 넘길 슬롯 ID
      time: selectedTimeSlot.value.timeLabel
    });
    
    alert('예약이 완료되었습니다. (가짜)');
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
/* (기존 스타일과 동일 ... ) */
:deep(.vc-container) {
  border: none;
  border-radius: 0;
  width: 100%;
}

/* ( ... 나머지 스타일 ... ) */
.slot-button.selected {
  background-color: #6d28d9;
  color: white;
  font-weight: bold;
  border-color: #6d28d9;
}
.confirm-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
