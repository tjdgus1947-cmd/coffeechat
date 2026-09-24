<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 왼쪽: 카페 간판 -->
      <aside class="cafe-panel">
        <div class="cup" aria-hidden="true">
          <div class="steam"><span></span><span></span><span></span></div>
          <div class="cup-body"></div>
          <div class="cup-handle"></div>
          <div class="saucer"></div>
        </div>

        <div class="panel-text">
          <h1 class="panel-title">다시 오셨네요!</h1>
          <p class="panel-sub">오늘도 따뜻한 커피챗 한 잔 준비해 둘게요.</p>
        </div>

        <ul class="menu-list">
          <li><span>☕</span> AI 바리스타의 맞춤 멘토 추천</li>
          <li><span>📍</span> 가까운 멘토와 커피챗 예약</li>
          <li><span>💬</span> 승인되면 바로 대화 시작</li>
        </ul>
      </aside>

      <!-- 오른쪽: 로그인 폼 -->
      <section class="form-panel">
        <p class="eyebrow">WELCOME BACK</p>
        <h2 class="form-title">로그인</h2>
        <div class="divider"></div>

        <LoginForm />

        <p class="register-link">
          아직 계정이 없으신가요?
          <router-link to="/register">회원가입</router-link>
        </p>
      </section>
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue';
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

.login-page {
  min-height: calc(100vh - 80px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  background-color: #F8F7F3;
}

.login-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  max-width: 880px;
  background: #FFFFFF;
  border: 2px solid #D4C3A3;
  border-radius: 16px;
  box-shadow: 4px 4px 0 #D4C3A3;
  overflow: hidden;
}

/* ---------- 왼쪽 카페 패널 ---------- */
.cafe-panel {
  position: relative;
  padding: 48px 40px;
  background: #4A352D;
  color: #F8F7F3;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.panel-title {
  font-family: 'Gowun Dodum', sans-serif;
  font-size: 2rem;
  margin: 24px 0 8px;
  color: #FFFFFF;
}

.panel-sub {
  margin: 0 0 32px;
  color: #E5DCC8;
  line-height: 1.6;
}

.menu-list {
  list-style: none;
  margin: 0;
  padding: 20px 0 0;
  border-top: 1px dashed rgba(229, 220, 200, 0.4);
}
.menu-list li {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  color: #E5DCC8;
  font-size: 0.95rem;
}

/* 커피잔 일러스트 */
.cup {
  position: relative;
  width: 96px;
  height: 96px;
}
.cup-body {
  position: absolute;
  bottom: 18px;
  left: 14px;
  width: 58px;
  height: 46px;
  background: #CC9966;
  border-radius: 0 0 22px 22px;
}
.cup-handle {
  position: absolute;
  bottom: 30px;
  left: 66px;
  width: 20px;
  height: 22px;
  border: 5px solid #CC9966;
  border-left: none;
  border-radius: 0 12px 12px 0;
}
.saucer {
  position: absolute;
  bottom: 8px;
  left: 2px;
  width: 84px;
  height: 10px;
  background: #D4C3A3;
  border-radius: 50%;
}
.steam {
  position: absolute;
  top: 0;
  left: 24px;
  display: flex;
  gap: 10px;
}
.steam span {
  width: 5px;
  height: 22px;
  background: rgba(248, 247, 243, 0.7);
  border-radius: 4px;
  animation: steam 2.4s ease-in-out infinite;
}
.steam span:nth-child(2) { animation-delay: 0.4s; }
.steam span:nth-child(3) { animation-delay: 0.8s; }

@keyframes steam {
  0%   { transform: translateY(8px) scaleY(0.6); opacity: 0; }
  50%  { opacity: 1; }
  100% { transform: translateY(-10px) scaleY(1); opacity: 0; }
}

/* ---------- 오른쪽 폼 패널 ---------- */
.form-panel {
  padding: 48px 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.eyebrow {
  margin: 0 0 6px;
  font-size: 0.8rem;
  letter-spacing: 0.15em;
  color: #CC9966;
  font-weight: 700;
}

.form-title {
  font-family: 'Gowun Dodum', sans-serif;
  font-size: 1.9rem;
  margin: 0;
  color: #4A352D;
}

.divider {
  width: 48px;
  height: 3px;
  margin: 16px 0 28px;
  background: #CC9966;
  border-radius: 2px;
}

.register-link {
  margin: 24px 0 0;
  text-align: center;
  color: #6B4423;
  font-size: 0.95rem;
}
.register-link a {
  margin-left: 4px;
  color: #CC9966;
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.register-link a:hover { color: #4A352D; }

/* ---------- 모바일 ---------- */
@media (max-width: 720px) {
  .login-card { grid-template-columns: 1fr; }
  .cafe-panel {
    padding: 28px 24px;
    flex-direction: row;
    align-items: center;
    gap: 16px;
  }
  .cup { transform: scale(0.7); flex-shrink: 0; margin: -12px; }
  .panel-text { flex: 1; min-width: 0; }
  .panel-title { font-size: 1.4rem; margin: 0 0 4px; word-break: keep-all; }
  .panel-sub { margin: 0; font-size: 0.9rem; }
  .menu-list { display: none; }
  .form-panel { padding: 32px 24px; }
}
</style>
