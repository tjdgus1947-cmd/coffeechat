<template>
  <div class="min-h-screen bg-white">
    <!-- Hero Section -->
    <section class="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div class="max-w-7xl mx-auto px-4 py-20 lg:py-32">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="space-y-8">
            <div class="inline-flex items-center gap-2 bg-white shadow-sm px-4 py-2 rounded-full border">
              <span class="text-blue-600">✨</span>
              <span class="text-sm">AI 기반 스마트 매칭</span>
            </div>

            <h1 class="leading-tight">
              당신의 성장을 위한<br />
              <span class="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                완벽한 멘토
              </span>를 만나세요
            </h1>

            <p class="text-gray-600 text-lg max-w-xl">
              AI가 당신의 목표와 관심사를 분석하여 최적의 멘토를 추천합니다.
              전문가들과의 진솔한 대화로 커리어의 새로운 기회를 발견하세요.
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <router-link 
                to="/register" 
                class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg text-lg font-semibold flex items-center justify-center gap-2 transition-all"
              >
                <span>✨</span>
                AI 매칭 시작하기
              </router-link>
              <router-link 
                to="/network" 
                class="border-2 border-gray-300 hover:border-blue-600 px-8 py-4 rounded-lg text-lg font-semibold flex items-center justify-center gap-2 transition-all"
              >
                멘토 둘러보기
                <span>→</span>
              </router-link>
            </div>

            <div class="flex items-center gap-8 pt-4">
              <div>
                <div class="text-2xl font-bold text-blue-600">2,500+</div>
                <p class="text-gray-600 text-sm">검증된 멘토</p>
              </div>
              <div class="w-px h-12 bg-gray-200"></div>
              <div>
                <div class="text-2xl font-bold text-blue-600">15,000+</div>
                <p class="text-gray-600 text-sm">성공적인 매칭</p>
              </div>
              <div class="w-px h-12 bg-gray-200"></div>
              <div>
                <div class="text-2xl font-bold text-blue-600">4.9/5.0</div>
                <p class="text-gray-600 text-sm">평균 만족도</p>
              </div>
            </div>
          </div>

          <div class="relative">
            <div class="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-400 rounded-3xl blur-3xl opacity-20"></div>
            <img
              src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800"
              alt="Coffee Chat Meeting"
              class="relative rounded-3xl shadow-2xl object-cover w-full h-[500px]"
            />
          </div>
        </div>
      </div>

      <!-- Decorative elements -->
      <div class="absolute top-20 left-10 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob"></div>
      <div class="absolute top-40 right-10 w-72 h-72 bg-purple-400 rounded-full mix-blend-multiply filter blur-3xl opacity-10 animate-blob animation-delay-2000"></div>
    </section>

    <!-- Search Section -->
    <section id="mentors" class="py-12 px-4 bg-white border-b">
      <div class="max-w-6xl mx-auto">
        <div class="flex flex-col lg:flex-row gap-4 mb-6">
          <div class="flex-1 relative">
            <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
            <input
              type="text"
              placeholder="멘토 이름, 회사, 관심 분야를 검색하세요..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <select class="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="">분야 선택</option>
            <option value="tech">기술/개발</option>
            <option value="business">비즈니스</option>
            <option value="design">디자인</option>
            <option value="marketing">마케팅</option>
            <option value="startup">스타트업</option>
          </select>

          <router-link 
            to="/register" 
            class="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:from-blue-700 hover:to-purple-700 transition-all flex items-center gap-2"
          >
            <span>✨</span>
            AI 매칭
          </router-link>
        </div>

        <div class="flex flex-wrap gap-2">
          <span class="text-gray-600 text-sm mr-2">인기 키워드:</span>
          <span v-for="tag in popularTags" :key="tag" class="px-3 py-1 border border-gray-300 rounded-full text-sm cursor-pointer hover:bg-blue-50 hover:text-blue-700 hover:border-blue-300 transition-colors">
            {{ tag }}
          </span>
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-20 px-4 bg-gray-50">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-4xl font-bold text-center mb-4">이용 방법</h2>
        <p class="text-gray-600 text-center mb-12">간단한 3단계로 시작하세요</p>

        <div class="grid md:grid-cols-3 gap-8">
          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">1️⃣</div>
            <h3 class="text-xl font-bold mb-2">프로필 작성</h3>
            <p class="text-gray-600">관심사와 목표를 입력하세요</p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">2️⃣</div>
            <h3 class="text-xl font-bold mb-2">멘토 매칭</h3>
            <p class="text-gray-600">AI가 최적의 멘토를 추천합니다</p>
          </div>

          <div class="text-center">
            <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">3️⃣</div>
            <h3 class="text-xl font-bold mb-2">커피챗 시작</h3>
            <p class="text-gray-600">멘토와 만나 성장하세요</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="py-20 px-4 bg-white">
      <div class="max-w-6xl mx-auto grid md:grid-cols-4 gap-8 text-center">
        <div>
          <div class="text-4xl font-bold text-blue-600 mb-2">2,500+</div>
          <p class="text-gray-600">활동 중인 멘토</p>
        </div>
        <div>
          <div class="text-4xl font-bold text-purple-600 mb-2">15,000+</div>
          <p class="text-gray-600">성공적인 매칭</p>
        </div>
        <div>
          <div class="text-4xl font-bold text-blue-600 mb-2">98%</div>
          <p class="text-gray-600">만족도</p>
        </div>
        <div>
          <div class="text-4xl font-bold text-purple-600 mb-2">50+</div>
          <p class="text-gray-600">다양한 분야</p>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12 px-4">
      <div class="max-w-6xl mx-auto">
        <div class="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <div class="mb-4">
              <div class="text-2xl font-bold text-white mb-1">CoffeeChat AI</div>
              <div class="text-sm text-gray-400">Connect. Share. Grow.</div>
            </div>
            <p class="text-sm text-gray-400">
              AI 기반 스마트 매칭으로 당신의 성장을 돕는 커피챗 플랫폼
            </p>
          </div>

          <div>
            <h4 class="text-white mb-4 font-semibold">서비스</h4>
            <ul class="space-y-2 text-sm">
              <li>
                <a href="#mentors" class="hover:text-blue-400 transition">멘토 찾기</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition">멘토 지원하기</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition">AI 매칭</a>
              </li>
              <li>
                <a href="#how-it-works" class="hover:text-blue-400 transition">이용 가이드</a>
              </li>
            </ul>
          </div>

          <div>
            <h4 class="text-white mb-4 font-semibold">회사</h4>
            <ul class="space-y-2 text-sm">
              <li>
                <a href="#" class="hover:text-blue-400 transition">회사 소개</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition">채용</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition">블로그</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition">공지사항</a>
              </li>
            </ul>
          </div>

          <div>
            <h4 class="text-white mb-4 font-semibold">문의</h4>
            <ul class="space-y-3 text-sm">
              <li class="flex items-center gap-2">
                <span>✉️</span>
                <span>support@coffeechat.ai</span>
              </li>
              <li class="flex items-center gap-2">
                <span>📞</span>
                <span>02-1234-5678</span>
              </li>
              <li class="flex items-center gap-2">
                <span>📍</span>
                <span>서울시 강남구</span>
              </li>
            </ul>
          </div>
        </div>

        <div class="pt-8 border-t border-gray-800">
          <div class="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-400">
            <p>© 2025 CoffeeChat AI. All rights reserved.</p>
            <div class="flex gap-6">
              <a href="#" class="hover:text-blue-400 transition">이용약관</a>
              <a href="#" class="hover:text-blue-400 transition">개인정보처리방침</a>
              <a href="#" class="hover:text-blue-400 transition">FAQ</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import logoUrl from '@/assets/images/logo.png';

const popularTags = ref([
  '스타트업',
  '마케팅',
  '개발',
  '디자인',
  '창업',
  '커리어전환',
  '투자유치',
  '제품기획',
]);
</script>