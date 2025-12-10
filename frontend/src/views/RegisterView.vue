<template>
  <div class="register-page-container cafe-theme">
    <!-- 선택 화면 -->
    <div v-if="!role" class="selection-wrapper">
      <div class="cafe-header">
        <div class="coffee-bean-icon">☕</div>
        <h1 class="handwritten-title">Welcome to CoffeeChat</h1>
        <p class="subtitle">당신의 성장 파트너를 선택해주세요</p>
        <div class="vintage-divider"></div>
      </div>

      <div class="menu-board">
        <div class="board-header">
          <span class="chalk-text">TODAY'S SPECIAL</span>
        </div>

        <div class="choice-cards">
          <!-- 멘티 카드 (크림색 종이컵) -->
          <div class="choice-card guest-card" @click="goRegister('mentee')">
            <div class="card-inner">
              <div class="cup-illustration">
                <div class="cup-body mentee-cup">
                  <div class="cup-sleeve">GUEST</div>
                </div>
                <div class="cup-lid"></div>
                <div class="steam">
                  <span></span><span></span><span></span>
                </div>
              </div>
              
              <div class="card-content">
                <h3>멘티 가입</h3>
                <p class="desc">따뜻한 조언이 필요하신가요?</p>
                <ul class="features">
                  <li>✨ AI 기반 맞춤 멘토 추천</li>
                  <li>🗺️ 가까운 멘토 찾기</li>
                  <li>💬 편안한 커피챗 예약</li>
                </ul>
                <button class="order-btn">
                  <span>주문하기</span>
                  <span class="arrow">→</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 멘토 카드 (다크 브라운 컵) -->
          <div class="choice-card barista-card" @click="goRegister('mentor')">
            <div class="card-inner">
              <div class="cup-illustration">
                <div class="cup-body mentor-cup">
                  <div class="cup-sleeve barista">BARISTA</div>
                </div>
                <div class="cup-lid"></div>
                <div class="steam">
                  <span></span><span></span><span></span>
                </div>
              </div>
              
              <div class="card-content">
                <h3>멘토 가입</h3>
                <p class="desc">당신의 경험을 나눠주세요</p>
                <ul class="features">
                  <li>🎯 성장하는 멘티 만나기</li>
                  <li>📅 유연한 일정 관리</li>
                  <li>🏆 멘토 레벨업 시스템</li>
                </ul>
                <button class="order-btn barista-btn">
                  <span>신청하기</span>
                  <span class="arrow">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="bottom-napkin">
        <p class="napkin-text">
          이미 계정이 있으신가요?
          <router-link to="/login" class="ink-link">로그인</router-link>
        </p>
      </div>
    </div>

    <!-- 가입 폼 화면 -->
    <div v-else class="form-wrapper">
      <div class="form-receipt-header">
        <button @click="router.push('/register')" class="back-btn">
          ← 다시 선택
        </button>
        <div class="receipt-title">
          <h2>가입 신청서</h2>
          <span class="role-badge" :class="role">
            {{ role === 'mentee' ? '☕ GUEST' : '👨‍🏫 BARISTA' }}
          </span>
        </div>
        <!-- 빈 공간 유지 (양쪽 균형) -->
        <div style="width: 100px;"></div>
      </div>

      <div class="form-content-area">
        <MenteeRegisterForm v-if="role === 'mentee'" />
        <MentorRegisterForm v-if="role === 'mentor'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MenteeRegisterForm from '@/components/auth/MenteeRegisterForm.vue';
import MentorRegisterForm from '@/components/auth/MentorRegisterForm.vue';

const route = useRoute();
const router = useRouter();

const role = computed(() => {
  const r = route.params.role;
  if (!r) return null;
  return r === 'mentor' ? 'mentor' : 'mentee';
});

function goRegister(selected) {
  router.push({ path: `/register/${selected}` });
}
</script>

<style scoped>
/* ========================================
   전체 컨테이너 & 배경
======================================== */
.register-page-container {
  min-height: 100vh;
  background-color: #F7F4E8; /* 크림색 배경 */
  background-image: 
    radial-gradient(circle at 20px 20px, rgba(209, 168, 114, 0.05) 1px, transparent 1px);
  background-size: 40px 40px;
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ========================================
   선택 화면 레이아웃
======================================== */
.selection-wrapper {
  max-width: 1000px;
  width: 100%;
}

/* 헤더 */
.cafe-header {
  text-align: center;
  margin-bottom: 50px;
}

.coffee-bean-icon {
  font-size: 4rem;
  margin-bottom: 10px;
  animation: rotate 10s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.handwritten-title {
  font-family: serif;
  font-size: 3rem;
  font-weight: 900;
  color: #361205;
  margin: 0 0 10px 0;
  letter-spacing: -1px;
}

.subtitle {
  font-size: 1.1rem;
  color: #8A5A34;
  margin-bottom: 20px;
}

.vintage-divider {
  width: 120px;
  height: 3px;
  background-color: #D1A872;
  margin: 0 auto;
  opacity: 0.6;
}

/* 메뉴판 보드 */
.menu-board {
  background: #3E2723; /* 칠판색 */
  border: 8px solid #6D4C41;
  border-radius: 16px;
  padding: 40px 30px;
  box-shadow: 0 10px 40px rgba(54, 18, 5, 0.3);
  position: relative;
}

.board-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 2px dashed #D7CCC8;
}

.chalk-text {
  font-family: 'Courier New', monospace;
  font-size: 1.5rem;
  font-weight: 900;
  color: #FFE082; /* 노란 분필 */
  text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
  letter-spacing: 3px;
}

/* ========================================
   카드 컨테이너
======================================== */
.choice-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 30px;
}

@media (max-width: 768px) {
  .choice-cards {
    grid-template-columns: 1fr;
  }
}

.choice-card {
  background: #FFFFFF;
  border-radius: 20px;
  padding: 30px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 8px 20px rgba(54, 18, 5, 0.15);
  border: 3px solid transparent;
}

.choice-card:hover {
  transform: translateY(-8px);
  border-color: #DF8723;
  box-shadow: 0 15px 35px rgba(223, 135, 35, 0.25);
}

.card-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 25px;
}

/* ========================================
   컵 일러스트레이션
======================================== */
.cup-illustration {
  position: relative;
  width: 120px;
  height: 140px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.cup-lid {
  width: 80px;
  height: 12px;
  background: #E0E0E0;
  border-radius: 50%;
  margin-bottom: 5px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.cup-body {
  width: 90px;
  height: 110px;
  background: #FFFFFF;
  border-radius: 0 0 15px 15px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 
    inset -5px 0 10px rgba(0,0,0,0.05),
    0 5px 15px rgba(0,0,0,0.1);
}

.mentee-cup {
  background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
}

.mentor-cup {
  background: linear-gradient(135deg, #6D4C41 0%, #5D4037 100%);
}

.cup-sleeve {
  position: absolute;
  top: 50%; /* 중앙으로 이동 */
  transform: translateY(-50%);
  width: 100%;
  height: 35px;
  background: #A1887F;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 900;
  color: white;
  letter-spacing: 1px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.cup-sleeve.barista {
  background: #3E2723;
}

/* 김 (스팀) */
.steam {
  position: absolute;
  top: -30px;
  display: flex;
  gap: 5px;
}

.steam span {
  width: 4px;
  height: 20px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  animation: steam-rise 2s infinite ease-in-out;
}

.steam span:nth-child(2) { animation-delay: 0.3s; }
.steam span:nth-child(3) { animation-delay: 0.6s; }

@keyframes steam-rise {
  0% { transform: translateY(0) scaleX(1); opacity: 0; }
  50% { opacity: 0.6; }
  100% { transform: translateY(-25px) scaleX(1.5); opacity: 0; }
}

/* ========================================
   카드 콘텐츠
======================================== */
.card-content {
  text-align: center;
  width: 100%;
}

.card-content h3 {
  font-size: 1.6rem;
  font-weight: 800;
  color: #361205;
  margin-bottom: 8px;
}

.desc {
  font-size: 0.95rem;
  color: #8A5A34;
  margin-bottom: 20px;
}

.features {
  list-style: none;
  padding: 0;
  margin: 0 0 25px 0;
  text-align: left;
}

.features li {
  padding: 8px 0;
  font-size: 0.9rem;
  color: #5D4037;
  border-bottom: 1px dotted #E0E0E0;
}

.features li:last-child {
  border-bottom: none;
}

/* 주문 버튼 */
.order-btn {
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #DF8723 0%, #B15408 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.3s;
  box-shadow: 0 4px 10px rgba(223, 135, 35, 0.3);
}

.order-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 15px rgba(223, 135, 35, 0.5);
}

.order-btn.barista-btn {
  background: linear-gradient(135deg, #3E2723 0%, #230100 100%);
}

.order-btn .arrow {
  transition: transform 0.3s;
}

.order-btn:hover .arrow {
  transform: translateX(5px);
}

/* ========================================
   하단 냅킨
======================================== */
.bottom-napkin {
  margin-top: 40px;
  text-align: center;
  background: #FFFDF5;
  padding: 20px;
  border-radius: 4px;
  transform: rotate(-1deg);
  box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #E0E0E0;
}

.napkin-text {
  font-family: serif;
  font-size: 1rem;
  color: #5D4037;
  margin: 0;
}

.ink-link {
  color: #DF8723;
  font-weight: 800;
  text-decoration: none;
  border-bottom: 2px solid #DF8723;
  transition: color 0.2s;
}

.ink-link:hover {
  color: #B15408;
}

/* ========================================
   가입 폼 화면
======================================== */
.form-wrapper {
  max-width: 700px;
  width: 100%;
}

.form-receipt-header {
  background: #FFFFFF;
  padding: 25px 30px;
  border-radius: 12px 12px 0 0;
  border: 1px solid #D1A872;
  border-bottom: 2px dashed #D1A872;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  background: #F5E8D8;
  border: 1px solid #D1A872;
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  color: #5D4037;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #E8D7C3;
  transform: translateX(-3px);
}

.receipt-title {
  flex: 1;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.receipt-title h2 {
  font-size: 1.8rem;
  font-weight: 800;
  color: #361205;
  margin: 0;
  font-family: serif;
  order: 1; /* 제목이 먼저 */
}

.role-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 800;
  order: 2; /* 배지가 나중에 */
}

.role-badge.mentee {
  background: linear-gradient(135deg, #FFE082 0%, #FFD54F 100%);
  color: #5D4037;
}

.role-badge.mentor {
  background: linear-gradient(135deg, #6D4C41 0%, #5D4037 100%);
  color: #FFE082;
}

.form-content-area {
  background: #FFFFFF;
  padding: 40px 30px;
  border-radius: 0 0 12px 12px;
  border: 1px solid #D1A872;
  border-top: none;
  box-shadow: 0 8px 20px rgba(54, 18, 5, 0.1);
}
</style>