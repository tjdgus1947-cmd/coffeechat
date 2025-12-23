<template>
  <div class="main-container">
    
    <!-- 1. Hero Section -->
    <section class="hero-section">
      <div class="content-wrapper hero-grid">
        
        <!-- Hero Text -->
        <div class="hero-text">
          
          <div class="badge">
            <span class="icon">☕</span>
            <span>AI 바리스타의 오늘의 추천 블렌딩</span>
          </div>

          <!-- H1: 간격 조정 클래스 적용 및 이모티콘 변경 -->
          <h1 class="h1-line-spacing">
            햇살 가득한 공간에서,<br />
            당신의 성장을 블렌딩하세요 
            <span class="emoji-accent">💬💖</span>
          </h1>
          
          <div class="vintage-divider"></div>

          <!-- 설명 텍스트 -->
          <p class="hero-description">
            AI 바리스타가 당신의 커리어 목표와 성장 취향을 분석하여<br />
            가장 완벽한 '커피챗' 레시피를 만들어 드립니다. 
          </p>

          <div class="hero-buttons">
            <router-link to="/register" class="btn btn-primary">
              <span>💬</span> 바리스타에게 주문하기
            </router-link>
            <router-link to="/network?tab=list" class="btn btn-outline">
              오늘의 메뉴판 둘러보기 <span>▶</span>
            </router-link>
          </div>
        </div>

        <!-- Hero Image -->
        <div class="hero-image-wrapper">
          <div class="image-frame-border"></div>
          <img
            src="https://images.unsplash.com/photo-1517048676732-d65bc937f952?q=80&w=800&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
            alt="Coffee chat meeting scene"
            class="hero-image"
          />
        </div>
      </div>
    </section>

    <!-- 2. Steps Section (AI 바리스타의 추천 블렌딩) -->
    <section id="how-it-works" class="steps-section">
      <div class="content-wrapper">
        <div class="section-header">
          <h2>AI 바리스타의 추천 블렌딩 레시피</h2>
          <div class="vintage-divider mx-auto"></div>
          <p>✨ 최고의 커피챗 경험을 위한 3단계 레시피 ✨</p>
        </div>

        <div class="steps-grid">
          
          <div class="step-card">
            <div class="step-icon">
              <span>📝</span>
            </div>
            <h3>원두 선택 (프로필)</h3>
            <p>당신의 커리어 취향과 목표를 알려주세요</p>
          </div>

          <div class="step-card">
            <div class="step-icon">
              <span>💡</span>
            </div>
            <h3>최적의 레시피 블렌딩</h3>
            <p>AI가 가장 잘 맞는 멘토를 추출해 드립니다</p>
          </div>

          <div class="step-card">
            <div class="step-icon">
              <span>🫂</span>
            </div>
            <h3>따뜻한 한 잔의 대화</h3>
            <p>멘토와 만나 성장의 향을 음미하세요</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 3. Footer (밝은 톤과 부드러운 색상 유지) -->
    <footer class="main-footer">
      <div class="content-wrapper">
        <div class="footer-grid">
          
          <!-- Brand -->
          <div class="footer-brand">
            <div class="brand-title">CoffeeChat AI</div>
            <div class="brand-slogan">Connect. Share. Grow.</div>
            <p class="brand-desc">
              AI 기반 스마트 매칭으로 당신의 성장을 돕는 커피챗 플랫폼
            </p>
          </div>

          <!-- Service Links -->
          <div class="footer-links">
            <h4>서비스</h4>
            <ul>
              <li><a href="#mentors">멘토 찾기</a></li>
              <li><a href="#">멘토 지원하기</a></li>
              <li><a href="#">AI 매칭</a></li>
              <li><a href="#how-it-works">이용 가이드</a></li>
            </ul>
          </div>

          <!-- Company Links -->
          <div class="footer-links">
            <h4>회사</h4>
            <ul>
              <li><a href="#">회사 소개</a></li>
              <li><a href="#">채용</a></li>
              <li><a href="#">블로그</a></li>
              <li><a href="#">공지사항</a></li>
            </ul>
          </div>

          <!-- Contact -->
          <div class="footer-links">
            <h4>문의</h4>
            <ul class="contact-list">
              <li><span>✉️</span> coffeechat@pknu.ai</li>
              <li><span>📞</span> 051-000-0000</li>
              <li><span>📍</span> 부경대학교 스마트 아카데미 5조</li>
            </ul>
          </div>
        </div>

        <!-- Footer Bottom -->
        <div class="footer-bottom">
          <p>© 2025 CoffeeChat AI. All rights reserved.</p>
          <div class="bottom-links">
            <a href="#">이용약관</a>
            <a href="#">개인정보처리방침</a>
            <a href="#">FAQ</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
// Vue 컴포넌트의 script setup은 비어 있습니다.
</script>

<style>
/* Google Font Import (Gowun Dodum) */
@import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');
</style>

<style scoped>

/* ---------------------------------------------------- */
/* Global / Layout Reset */
/* ---------------------------------------------------- */

.main-container {
    font-family: 'Gowun Dodum', sans-serif;
    color: #4A352D;
    background-color: #E5DCC8;
    width: 100%;
    overflow-x: hidden;
    min-height: 100vh;
}

.content-wrapper {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* ---------------------------------------------------- */
/* Typography & Decoratives */
/* ---------------------------------------------------- */

h1, h2, h3, h4 { 
    font-family: 'Gowun Dodum', sans-serif;
    font-weight: 700; 
} 

/* H1 스타일 */
.hero-text h1 {
    font-size: 3.5rem; 
    font-weight: 800;
    color: #4A352D;
    margin-bottom: 0;
}

.h1-line-spacing {
    line-height: 1.5; /* 요청하신 줄 간격 */
}

.emoji-accent {
    font-size: 3.5rem; 
    color: #CC9966;
}

@media (max-width: 768px) {
    .hero-text h1, .emoji-accent { font-size: 2.5rem; }
    .hero-grid {
        grid-template-columns: 1fr;
        text-align: center;
    }
    .hero-text {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
}

.hero-description {
    font-size: 1.125rem; 
    color: #4A352D;
    line-height: 1.6;
    margin-bottom: 40px;
    max-width: 560px;
    font-weight: 400;
}

/* Vintage Divider */
.vintage-divider {
    width: 100px;
    height: 2px;
    background-color: #D4C3A3;
    opacity: 0.8;
    margin-top: 20px;
    margin-bottom: 20px;
}

.vintage-divider.mx-auto {
    margin-left: auto;
    margin-right: auto;
}

/* Badge */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    padding: 8px 16px;
    border-radius: 12px; 
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    border: 1px solid #D4C3A3;
    margin-bottom: 24px;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge .icon { 
    color: #CC9966; 
}

/* ---------------------------------------------------- */
/* Buttons */
/* ---------------------------------------------------- */

.hero-buttons {
    display: flex;
    gap: 16px;
    margin-bottom: 48px;
}

@media (max-width: 480px) {
    .hero-buttons { flex-direction: column; width: 100%; }
}

.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px 24px;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.125rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.2s ease;
    text-decoration: none;
    box-shadow: 2px 2px 0 #D4C3A3;
    font-family: 'Gowun Dodum', sans-serif;
}

.btn-primary {
    background: #CC9966;
    color: white;
    border: 2px solid #CC9966;
}
.btn-primary:hover {
    transform: translate(0, 0);
    background: #DDAA66;
    box-shadow: 1px 1px 0 #D4C3A3;
}

.btn-outline {
    border: 2px solid #CC9966;
    color: #4A352D;
    background: #FFFFFF;
}
.btn-outline:hover {
    border-color: #CC9966;
    color: white;
    background: #CC9966;
}

/* ---------------------------------------------------- */
/* Sections Layout */
/* ---------------------------------------------------- */

.hero-section {
    padding: 80px 0;
    background-color: #F8F7F3;
    overflow: hidden;
}

.hero-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 60px;
    align-items: center;
}

.steps-section {
    padding: 80px 0;
    background-color: #FFFFFF;
    border-top: 1px solid #D4C3A3;
    border-bottom: 1px solid #D4C3A3;
}

.section-header {
    text-align: center;
    margin-bottom: 48px;
}

.section-header h2 {
    font-size: 1.875rem;
    font-weight: 700;
    color: #4A352D;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

.section-header p {
    color: #4A352D;
    font-style: italic;
    font-size: 1rem;
}

.steps-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 32px;
}
@media (max-width: 768px) {
    .steps-grid { grid-template-columns: 1fr; }
}


/* ---------------------------------------------------- */
/* Component Specific Styles */
/* ---------------------------------------------------- */

/* Hero Image */
.hero-image-wrapper {
    position: relative;
    padding: 20px;
}
.image-frame-border {
    position: absolute;
    inset: 0;
    border: 4px solid #D4C3A3;
    border-radius: 12px;
    transform: rotate(-1deg);
    z-index: 10;
    box-shadow: 1px 1px 4px rgba(0, 0, 0, 0.08);
}
.hero-image {
    width: 100%;
    height: 450px;
    object-fit: cover;
    border-radius: 8px;
    filter: brightness(1.05) contrast(1.0);
    position: relative;
    z-index: 20;
}

/* Steps */
.step-card {
    text-align: center;
    padding: 24px;
    background-color: #F8F7F3;
    border: 1px solid #D4C3A3;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.step-card h3 {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 8px;
    color: #4A352D;
}

.step-card p {
    color: #4A352D;
    font-size: 1rem;
}

.step-icon {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    margin: 0 auto 20px;
    border: 3px solid #CC9966;
    box-shadow: 1px 1px 0 #D4C3A3;
    background-color: #FFFFFF;
}

/* Footer */
.main-footer {
    background-color: #FFFFFF;
    color: #4A352D;
    padding: 60px 0 20px;
    border-top: 1px solid #D4C3A3;
}

.footer-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr 1fr 1fr;
    gap: 40px;
    margin-bottom: 40px;
    padding-bottom: 40px;
    border-bottom: 1px solid #D4C3A3;
}

@media (max-width: 900px) {
    .footer-grid { grid-template-columns: 1fr 1fr; }
}

@media (max-width: 600px) {
    .footer-grid { grid-template-columns: 1fr; }
}

.brand-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #4A352D;
}

.brand-slogan {
    font-size: 0.9rem;
    color: #4A352D;
    margin-bottom: 16px;
}

.brand-desc {
    font-size: 0.9rem;
    color: #4A352D;
    line-height: 1.5;
}

.footer-links h4 {
    color: #4A352D;
    font-weight: 600;
    margin-bottom: 20px;
    font-size: 1.125rem;
}

.footer-links ul {
    list-style: none;
    padding: 0;
}

.footer-links li {
    margin-bottom: 12px;
}

.footer-links a {
    color: #4A352D;
    text-decoration: none;
    font-size: 1rem;
    transition: color 0.2s;
}

.footer-links a:hover {
    color: #CC9966;
}

.contact-list li { 
    display: flex; 
    gap: 8px; 
    align-items: center; 
    font-size: 0.9rem; 
    color: #4A352D;
}

.footer-bottom {
    padding-top: 24px;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    font-size: 0.9rem;
    color: #4A352D;
}

.bottom-links {
    display: flex;
    gap: 24px;
}

.bottom-links a {
    color: #4A352D;
    text-decoration: none;
    transition: color 0.2s;
}

.bottom-links a:hover {
    color: #CC9966;
}
</style>