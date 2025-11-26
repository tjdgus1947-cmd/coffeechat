// frontend/src/services/supabase.js
import { createClient } from '@supabase/supabase-js';

// .env 파일에서 환경변수를 불러옵니다.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('⚠️ Supabase URL or Key is missing in .env file!');
}

// Supabase 클라이언트 생성 및 내보내기
export const supabase = createClient(supabaseUrl, supabaseKey);