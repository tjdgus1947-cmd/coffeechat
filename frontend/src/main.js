
import { createApp } from 'vue'
import { createPinia } from 'pinia'// 1. Pinia 임포트
import App from './App.vue'
import router from './router'
import './assets/css/main.css'// (이 파일이 없다면 생성하시거나 지우셔도 됩니다)

// 1. v-calendar 임포트
import VCalendar from 'v-calendar';
// 2. v-calendar CSS 임포트
import 'v-calendar/style.css';

const app = createApp(App)
const pinia = createPinia()// 2. Pinia 인스턴스 생성

app.use(pinia) // 3. Pinia 등록
app.use(router)

// 3. v-calendar를 앱에 등록
app.use(VCalendar, {}) 

app.mount('#app')

