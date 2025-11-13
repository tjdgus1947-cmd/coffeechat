import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

let supabaseClient = null;

if (!supabaseUrl || !supabaseAnonKey) {
	console.warn('[supabaseClient] 환경 변수 VITE_SUPABASE_URL 혹은 VITE_SUPABASE_ANON_KEY가 설정되지 않았습니다. Supabase 연동이 비활성화됩니다.');
} else {
	supabaseClient = createClient(supabaseUrl, supabaseAnonKey);
}

export const supabase = supabaseClient;
