// frontend/src/services/supabaseClient.js

import { createClient } from '@supabase/supabase-js'

// 1단계에서 .env에 저장한 VITE_ 변수들을 불러옵니다.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY 

// Supabase 클라이언트 인스턴스 생성
export const supabase = createClient(supabaseUrl, supabaseAnonKey)