<template>
  <div class="main-container">
    
    <section class="hero-section">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>

      <div class="content-wrapper hero-grid">
        <div class="hero-text">
          <div class="badge">
            <span class="icon">✨</span>
            <span>AI 기반 스마트 매칭</span>
          </div>

          <h1>
            당신의 성장을 위한<br />
            <span class="gradient-text">완벽한 멘토</span>를 만나세요
          </h1>

          <p class="hero-description">
            AI가 당신의 목표와 관심사를 분석하여 최적의 멘토를 추천합니다.
            전문가들과의 진솔한 대화로 커리어의 새로운 기회를 발견하세요.
          </p>

          <div class="hero-buttons">
            <router-link to="/register" class="btn btn-primary">
              <span>✨</span> AI 매칭 시작하기
            </router-link>
            <router-link to="/network?tab=list" class="btn btn-outline">
              멘토 둘러보기 <span>→</span>
            </router-link>
          </div>
        </div>

        <div class="hero-image-wrapper">
          <div class="image-backdrop"></div>
          <img
            src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"
            alt="Coffee Chat Meeting"
            class="hero-image"
          />
        </div>
      </div>
    </section>

    <section id="how-it-works" class="steps-section">
      <div class="content-wrapper">
        <div class="section-header">
          <h2>이용 방법</h2>
          <p>간단한 3단계로 시작하세요</p>
        </div>

        <div class="steps-grid">
          <div class="step-card">
            <div class="step-icon bg-blue">1️⃣</div>
            <h3>프로필 작성</h3>
            <p>관심사와 목표를 입력하세요</p>
          </div>

          <div class="step-card">
            <div class="step-icon bg-purple">2️⃣</div>
            <h3>멘토 매칭</h3>
            <p>AI가 최적의 멘토를 추천합니다</p>
          </div>

          <div class="step-card">
            <div class="step-icon bg-blue">3️⃣</div>
            <h3>커피챗 시작</h3>
            <p>멘토와 만나 성장하세요</p>
          </div>
        </div>
      </div>
    </section>

    <footer class="main-footer">
      <div class="content-wrapper">
        <div class="footer-grid">
          <div class="footer-brand">
            <div class="brand-title">CoffeeChat AI</div>
            <div class="brand-slogan">Connect. Share. Grow.</div>
            <p class="brand-desc">
              AI 기반 스마트 매칭으로 당신의 성장을 돕는 커피챗 플랫폼
            </p>
          </div>

          <div class="footer-links">
            <h4>서비스</h4>
            <ul>
              <li><a href="#mentors">멘토 찾기</a></li>
              <li><a href="#">멘토 지원하기</a></li>
              <li><a href="#">AI 매칭</a></li>
              <li><a href="#how-it-works">이용 가이드</a></li>
            </ul>
          </div>

          <div class="footer-links">
            <h4>회사</h4>
            <ul>
              <li><a href="#">회사 소개</a></li>
              <li><a href="#">채용</a></li>
              <li><a href="#">블로그</a></li>
              <li><a href="#">공지사항</a></li>
            </ul>
          </div>

          <div class="footer-links">
            <h4>문의</h4>
            <ul class="contact-list">
              <li><span>✉️</span> support@coffeechat.ai</li>
              <li><span>📞</span> 02-1234-5678</li>
              <li><span>📍</span> 서울시 강남구</li>
            </ul>
          </div>
        </div>

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
// 삭제된 섹션에 사용되던 popularTags는 더 이상 필요 없으므로 제거했습니다.
</script>

<style scoped>
/* 공통 설정 */
.main-container {
  width: 100%;
  overflow-x: hidden;
  background-color: #fff;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.content-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

/* 1. Hero Section 스타일 */
.hero-section {
  position: relative;
  padding: 80px 0;
  background: linear-gradient(135deg, #eff6ff 0%, #ffffff 50%, #f5f3ff 100%);
  overflow: hidden;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  position: relative;
  z-index: 1;
}

@media (max-width: 960px) {
  .hero-grid {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .hero-text {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .hero-stats {
    justify-content: center;
  }
}

/* 뱃지 */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: white;
  padding: 8px 16px;
  border-radius: 50px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
  font-size: 14px;
  color: #555;
}
.badge .icon { color: #2563eb; }

/* 헤드라인 */
h1 {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.2;
  color: #111827;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  h1 { font-size: 2.5rem; }
}

.gradient-text {
  background: linear-gradient(to right, #2563eb, #9333ea);
  -webkit-background-clip: text;
  background-clip: text;
  
  -webkit-text-fill-color: transparent;
}

.hero-description {
  font-size: 1.125rem;
  color: #4b5563;
  line-height: 1.6;
  margin-bottom: 40px;
  max-width: 560px;
}

/* 버튼 */
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
  padding: 16px 32px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 1.1rem;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(to right, #2563eb, #9333ea);
  color: white;
  box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
}
.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3);
}

.btn-outline {
  background: white;
  border: 2px solid #e5e7eb;
  color: #374151;
}
.btn-outline:hover {
  border-color: #2563eb;
  color: #2563eb;
}

/* 통계 (Hero 내부) */
.hero-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

.stat-item strong {
  display: block;
  font-size: 1.5rem;
  font-weight: 800;
  color: #2563eb;
}
.stat-item span {
  font-size: 0.9rem;
  color: #6b7280;
}
.divider {
  width: 1px;
  height: 40px;
  background-color: #e5e7eb;
}

/* 오른쪽 이미지 */
.hero-image-wrapper {
  position: relative;
}
.image-backdrop {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, #60a5fa, #c084fc);
  border-radius: 24px;
  filter: blur(40px);
  opacity: 0.3;
  transform: translateY(20px) scale(0.9);
}
.hero-image {
  position: relative;
  width: 100%;
  height: 500px;
  object-fit: cover;
  border-radius: 24px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

/* 배경 애니메이션 Blobs */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: blob-bounce 7s infinite;
  z-index: 0;
}
.blob-1 {
  top: -10%;
  left: -10%;
  width: 500px;
  height: 500px;
  background-color: #bfdbfe; /* blue-200 */
  animation-delay: 0s;
}
.blob-2 {
  bottom: -10%;
  right: -10%;
  width: 500px;
  height: 500px;
  background-color: #e9d5ff; /* purple-200 */
  animation-delay: 2s;
}
@keyframes blob-bounce {
  0% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0, 0) scale(1); }
}


/* 2. Steps Section */
.steps-section {
  padding: 80px 0;
  background-color: #f9fafb;
}
.section-header {
  text-align: center;
  margin-bottom: 48px;
}
.section-header h2 {
  font-size: 2.5rem;
  font-weight: 800;
  color: #111827;
  margin-bottom: 8px;
}
.section-header p { color: #6b7280; }

.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
}
@media (max-width: 768px) {
  .steps-grid { grid-template-columns: 1fr; }
}

.step-card {
  text-align: center;
}
.step-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  margin: 0 auto 20px;
}
.bg-blue { background-color: #dbeafe; }
.bg-purple { background-color: #f3e8ff; }

.step-card h3 { font-size: 1.25rem; font-weight: 700; margin-bottom: 8px; }
.step-card p { color: #6b7280; }


/* 3. Footer */
.main-footer {
  background-color: #111827;
  color: #e5e7eb;
  padding: 60px 0 20px;
}
.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}
@media (max-width: 900px) {
  .footer-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .footer-grid { grid-template-columns: 1fr; }
}

.brand-title { font-size: 1.5rem; font-weight: 800; color: white; }
.brand-slogan { font-size: 0.9rem; color: #9ca3af; margin-bottom: 16px; }
.brand-desc { font-size: 0.9rem; color: #9ca3af; line-height: 1.5; }

.footer-links h4 {
  color: white;
  font-weight: 600;
  margin-bottom: 20px;
}
.footer-links ul {
  list-style: none;
  padding: 0;
}
.footer-links li { margin-bottom: 12px; }
.footer-links a {
  color: #d1d5db;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.2s;
}
.footer-links a:hover { color: #60a5fa; }

.contact-list li { display: flex; gap: 8px; align-items: center; font-size: 0.9rem; }

.footer-bottom {
  border-top: 1px solid #374151;
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 0.9rem;
  color: #9ca3af;
}
.bottom-links { display: flex; gap: 24px; }
.bottom-links a { color: #9ca3af; text-decoration: none; }
.bottom-links a:hover { color: #60a5fa; }
</style>