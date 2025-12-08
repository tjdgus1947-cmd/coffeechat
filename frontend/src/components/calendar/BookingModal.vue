<template>

  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">

    <div class="receipt-paper">

      <div class="receipt-header">

        <h3>🧾 COFFEE CHAT ORDER</h3>

        <span class="date">{{ new Date().toLocaleDateString() }}</span>

      </div>

     

      <div class="receipt-body">

        <p v-if="mentorName" class="order-item">

          <span class="label">Mentor:</span>

          <span class="value">{{ mentorName }}</span>

        </p>

       

        <BookingCalendar

          :mentor-id="mentorId"

          @booking-confirmed="handleBookingConfirmed"

        />

      </div>



      <div class="receipt-footer">

        <p class="thank-you">Thank you for ordering!</p>

        <button @click="$emit('close')" class="close-btn">닫기 (Close)</button>

      </div>

     

      <div class="jagged-edge"></div>

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

  top: 0; left: 0; width: 100vw; height: 100vh;

 

  /* ☕️ 수정된 부분: 답답한 갈색 대신 화사한 크림 베이지 적용 */

  background-color: rgba(247, 244, 232, 0.85); /* --bg-cream 색상의 반투명 버전 */

  backdrop-filter: blur(5px); /* 배경을 흐리게 해서 '아늑한' 느낌 추가 */

 

  display: flex;

  justify-content: center;

  align-items: center;

  z-index: 1000;

}



/* 🧾 영수증 스타일 컨테이너 */

.receipt-paper {

  background: white;

  width: 380px;

  max-width: 90vw;

  padding: 30px 20px 50px 20px; /* 하단 여백 충분히 */

  position: relative;box-shadow: 0 15px 40px rgba(54, 18, 5, 0.15);

  font-family: 'Courier New', Courier, monospace; /* 영수증 폰트 (고정폭) */

  color: #333;

}



.receipt-header {

  text-align: center;

  border-bottom: 2px dashed #333;

  padding-bottom: 15px;

  margin-bottom: 20px;

}



.receipt-header h3 {

  font-size: 1.2rem;

  font-weight: 900;

  margin: 0;

  letter-spacing: -1px;

}



.date {

  font-size: 0.8rem;

  color: #666;

}



.order-item {

  display: flex;

  justify-content: space-between;

  font-size: 1.1rem;

  margin-bottom: 20px;

  font-weight: bold;

}



/* 영수증 하단 지그재그(톱니) 효과 */

.jagged-edge {

  position: absolute;

  bottom: 0;

  left: 0;

  width: 100%;

  height: 20px;

  background:

    linear-gradient(45deg, transparent 33.333%, #ffffff 33.333%, #ffffff 66.667%, transparent 66.667%),

    linear-gradient(-45deg, transparent 33.333%, #ffffff 33.333%, #ffffff 66.667%, transparent 66.667%);

  background-size: 20px 40px;

  background-position: 0 10px; /* 위치 조정 */

  transform: translateY(10px); /* 밖으로 살짝 뺌 */

}



.receipt-footer {

  text-align: center;

  margin-top: 30px;

  border-top: 2px dashed #333;

  padding-top: 15px;

}



.thank-you {

  font-size: 0.8rem;

  text-transform: uppercase;

  margin-bottom: 15px;

}



.close-btn {

  background: transparent;

  border: 1px solid #333;

  padding: 5px 15px;

  cursor: pointer;

  font-family: inherit;

  font-size: 0.9rem;

}

.close-btn:hover {

  background: #eee;

}

</style>