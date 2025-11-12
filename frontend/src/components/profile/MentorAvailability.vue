<template>
  <div class="availability-manager">
    <p>달력에서 날짜를 선택하고, 원하는 시간을 추가하세요.</p>
    
    <v-date-picker
      v-model="selectedDate"
      :attributes="calendarAttributes"
      @dayclick="onDayClick"
      trim-weeks
    />
    
    <div v-if="selectedDate" class="slot-form">
      <h4>{{ selectedDate.toLocaleDateString() }} 일정 추가</h4>
      <div class="form-grid">
        <select v-model="newSlotTime">
          <option value="10:00">10:00</option>
          <option value="11:00">11:00</option>
          <option value="13:00">13:00</option>
          <option value="14:00">14:00</option>
          <option value="15:00">15:00</option>
          <option value="16:00">16:00</option>
        </select>
        <button @click="addSlot" :disabled="isSubmitting">
          {{ isSubmitting ? '추가 중...' : '추가하기' }}
        </button>
      </div>
    </div>

    <div class="slots-list">
      <h4>등록된 내 시간 (클릭하여 삭제)</h4>
      <div v-if="isLoading">등록된 시간 불러오는 중...</div>
      <ul v-else-if="mySlots.length > 0">
        <li 
          v-for="slot in mySlots" 
          :key="slot.id" 
          @click="deleteSlot(slot.id)" 
          class="slot-item"
        >
          {{ new Date(slot.start_time).toLocaleString('ko-KR', { dateStyle: 'short', timeStyle: 'short' }) }}
          <span>(삭제)</span>
        </li>
      </ul>
      <p v-else>등록된 시간이 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '@/store/auth';
import api from '@/services/api'; // ⭐️ 실제 API 호출기

const authStore = useAuthStore();
const mySlots = ref([]);
const isLoading = ref(true);
const isSubmitting = ref(false);
const selectedDate = ref(new Date());
const newSlotTime = ref('10:00'); // 기본 선택 시간

// --- 1. (GET) 내 슬롯 불러오기 ---
// 이 컴포넌트가 마운트되면, 내 ID로 등록된 슬롯을 불러옵니다.
async function fetchMySlots() {
  if (!authStore.userId) {
      console.warn("로그인된 유저 ID가 없습니다.");
      return;
  }
  isLoading.value = true;
  try {
    const response = await api.get(`/availability/${authStore.userId}`);
    console.log("내 슬롯 로드 성공:", response.data); // ⭐️ 로그 확인용
    mySlots.value = response.data;
  } catch (error) {
    console.error("내 슬롯 로딩 실패:", error);
    // 혹시 500 에러가 계속 난다면 터미널의 백엔드 로그를 확인해야 합니다.
  } finally {
    isLoading.value = false;
  }
}

// --- 2. (POST) 새 슬롯 추가하기 ---
async function addSlot() {
  const [hours, minutes] = newSlotTime.value.split(':');
  const startTime = new Date(selectedDate.value);
  startTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
  
  // (예시: 1시간 슬롯)
  const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); 

  isSubmitting.value = true;
  try {
    // ⭐️ (POST) /api/availability/
    await api.post('/availability/', {
      // ❌ 틀린 부분
      // mentor_id: authStore.userId, 
      
      // ✅ 수정된 부분
      user_id: authStore.userId, // ⭐️ 내 ID (UUID)
      
      start_time: startTime.toISOString(),
      end_time: endTime.toISOString()
    });
    alert('시간이 추가되었습니다.');
    fetchMySlots(); // 목록 새로고침
  } catch (error) {
    console.error("슬롯 추가 실패:", error);
    alert("슬롯 추가 실패: " + (error.response?.data?.detail || error.message));
  } finally {
    isSubmitting.value = false;
  }
}
// --- 3. (DELETE) 슬롯 삭제하기 ---
async function deleteSlot(slotId) {
  if (!confirm("이 슬롯을 삭제하시겠습니까? 멘티가 예약했다면 취소될 수 있습니다.")) return;
  try {
    // ⭐️ (DELETE) /api/availability/{slot_id}
    await api.delete(`/availability/${slotId}`);
    alert('삭제되었습니다.');
    fetchMySlots(); // 목록 새로고침
  } catch (error) {
    console.error("슬롯 삭제 실패:", error);
    alert("슬롯 삭제 실패: " + (error.response?.data?.detail || error.message));
  }
}

// (v-calendar용) 달력에 내 슬롯 위치를 점으로 표시
const calendarAttributes = computed(() => [
  {
    key: 'mySlots',
    dot: 'purple',
    dates: mySlots.value.map(slot => new Date(slot.start_time))
  }
]);

// 달력 날짜 클릭 시
const onDayClick = (day) => {
  selectedDate.value = day.date;
};

// 컴포넌트가 켜질 때 내 슬롯을 로드합니다.
onMounted(fetchMySlots);
</script>

<style scoped>
.availability-manager {
  border-top: 1px solid #eee;
  margin-top: 20px;
  padding-top: 20px;
}

/* v-calendar가 부모 너비에 맞도록 강제 */
:deep(.vc-container) {
  width: 100%;
}

.form-grid {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.form-grid select {
  flex-grow: 1;
  padding: 8px;
}
.form-grid button {
  padding: 8px 12px;
  background-color: #6d28d9;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.form-grid button:disabled {
  background-color: #ccc;
}

.slots-list {
  margin-top: 20px;
}
.slots-list h4 {
  margin-bottom: 10px;
}
.slots-list ul {
  list-style: none;
  padding: 0;
}
.slot-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 5px;
  cursor: pointer;
  transition: all 0.2s;
}
.slot-item:hover {
  background-color: #fef2f2; /* Light Red */
  border-color: #dc2626; /* Red */
}
.slot-item span {
  color: #dc2626;
  font-weight: bold;
}
</style>