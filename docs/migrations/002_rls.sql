-- =====================================================================
-- 002_rls.sql : Row Level Security 정리
--
-- 구조
--   - 백엔드(FastAPI)는 service_role 키를 쓰므로 RLS 영향을 받지 않는다.
--   - 프론트는 anon 키로 Supabase에 직접 접근한다 → 여기서 RLS가 유일한 방어선.
--
-- 원칙
--   - public 의 모든 테이블에 RLS를 켠다. 정책이 없으면 anon/authenticated 접근은 전부 거부된다.
--   - 프론트가 직접 쓰는 작업에만 최소 정책을 연다.
--     users / mentor_profiles(SELECT) · reviews(SELECT, INSERT) · user_likes · coffee_chats(SELECT)
--     chat_rooms / chat_messages(SELECT, Realtime 구독용)
--   - 쓰기(예약, 채팅, 프로필 생성)는 백엔드 API만 하도록, 프론트용 INSERT 정책은 제거한다.
-- =====================================================================
begin;

-- 1. 모든 테이블 RLS 활성화 (이미 켜져 있으면 변화 없음)
alter table users                  enable row level security;
alter table mentor_profiles        enable row level security;
alter table mentee_profiles        enable row level security;
alter table verification_documents enable row level security;
alter table mentor_availability    enable row level security;
alter table coffee_chats           enable row level security;
alter table connection_weights     enable row level security;
alter table reviews                enable row level security;
alter table user_likes             enable row level security;
alter table chat_rooms             enable row level security;
alter table chat_messages          enable row level security;
alter table kv_store_8148f72a      enable row level security;

-- 2. 프론트에서 직접 INSERT 할 필요가 없는 정책 제거 (백엔드가 service_role 로 처리)
drop policy if exists "System can insert chat rooms"                 on chat_rooms;
drop policy if exists "Users can send messages in their chat rooms"   on chat_messages;
drop policy if exists "Allow profile insert (mentor)"                on mentor_profiles;

-- 3. 로그인 사용자 공개 정보: 이름·멘토 프로필은 화면에 표시되므로 조회 허용
drop policy if exists "Authenticated can view users" on users;
create policy "Authenticated can view users"
    on users for select to authenticated using (true);

drop policy if exists "Authenticated can view mentor profiles" on mentor_profiles;
create policy "Authenticated can view mentor profiles"
    on mentor_profiles for select to authenticated using (true);

-- 4. 후기: 조회는 로그인 사용자 전체(랭킹 계산), 작성은
--    "본인이 멘티이고 승인된 커피챗"에 대해서만 가능
drop policy if exists "Authenticated can view reviews" on reviews;
create policy "Authenticated can view reviews"
    on reviews for select to authenticated using (true);

drop policy if exists "Mentee can review own approved chat" on reviews;
create policy "Mentee can review own approved chat"
    on reviews for insert to authenticated
    with check (
        auth.uid() = mentee_id
        and exists (
            select 1 from coffee_chats c
            where c.id = coffee_chat_id
              and c.mentee_id = auth.uid()
              and c.mentor_id = reviews.mentor_id
              and c.status = 'approved'
        )
    );

-- 5. 찜: INSERT 정책의 조건을 명시적으로 다시 건다 (본인 것만)
drop policy if exists "Users can insert their own likes" on user_likes;
create policy "Users can insert their own likes"
    on user_likes for insert to authenticated
    with check (auth.uid() = user_id);

commit;

-- 확인용
-- select relname, relrowsecurity from pg_class
-- where relnamespace = 'public'::regnamespace and relkind = 'r' order by 1;
-- select tablename, policyname, cmd, qual, with_check from pg_policies
-- where schemaname = 'public' order by 1, 2;
