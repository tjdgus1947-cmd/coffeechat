import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/css/main.css'
import VCalendar from 'v-calendar';
import 'v-calendar/style.css';

// ⭐️ 1. auth 스토어를 여기서 직접 import 합니다.
import { useAuthStore } from '@/store/auth';

const app = createApp(App)
const pinia = createPinia() // 2. Pinia 인스턴스 생성

app.use(pinia) // 3. Pinia를 *먼저* 등록합니다.

// 4. 앱을 마운트하기 전에 인증을 완료하는 async 함수를 만듭니다.
async function initializeApp() {
  // 5. auth 스토어를 사용합니다.
  const authStore = useAuthStore(); 

  try {
    // 6. ⭐️ auth.js의 initializeAuth() 함수가 완료될 때까지 "기다립니다".
    await authStore.initializeAuth(); 
  } catch (e) {
    console.error("인증 초기화 실패:", e);
  }

  // 7. ⭐️ 인증이 완료된 "후에" 라우터를 등록합니다.
  app.use(router) 

  // 8. 캘린더 등록
  app.use(VCalendar, {}) 

  // 9. ⭐️ 모든 것이 준비된 "후에" 앱을 마운트합니다.
  app.mount('#app')
}

// 10. 앱 초기화 함수를 실행합니다.
initializeApp();