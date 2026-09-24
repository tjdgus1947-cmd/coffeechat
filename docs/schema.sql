-- =====================================================================
-- CoffeeChat DB 스키마 (Supabase / PostgreSQL)
--
-- 운영 DB의 information_schema, pg_constraint, pg_indexes, pg_proc 조회 결과로
-- 재구성한 DDL이다. pg_dump 원본이 아니므로 아래 항목은 포함되지 않았다.
--   - RLS 정책, 트리거 바인딩, 권한(GRANT)
--   - ENUM 값 목록 (user_role, verification_status): 코드 기준으로 적었음
-- =====================================================================

-- ---------- Extensions ----------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;   -- geography, ST_DWithin
CREATE EXTENSION IF NOT EXISTS vector;    -- pgvector: embedding, <=> 연산자

-- ---------- Enums ----------
CREATE TYPE user_role AS ENUM ('mentor', 'mentee');                 -- 코드 기준
CREATE TYPE verification_status AS ENUM ('pending' /* , ... */);   -- 기본값만 확인됨

-- ---------- 사용자 / 프로필 ----------
CREATE TABLE users (
    id         uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name  text      NOT NULL,
    role       user_role NOT NULL
);

CREATE TABLE mentor_profiles (
    id                  uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    career_info         text,
    profile_image_url   text,
    location            geography,
    embedding           vector,           -- bge-m3, 1024차원
    verification_status verification_status DEFAULT 'pending'
);

CREATE TABLE mentee_profiles (
    id                uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id           uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    current_situation text,
    career_goal       text,
    location          geography,
    embedding         vector
);

CREATE TABLE verification_documents (
    id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentor_id  uuid NOT NULL REFERENCES mentor_profiles(id) ON DELETE CASCADE,
    file_url   text NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- ---------- 예약 ----------
CREATE TABLE mentor_availability (
    id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentor_id  uuid NOT NULL,             -- FK 없음
    start_time timestamptz NOT NULL,
    end_time   timestamptz NOT NULL,
    is_booked  boolean DEFAULT false
);

CREATE TABLE coffee_chats (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentee_id       uuid NOT NULL REFERENCES users(id),
    mentor_id       uuid NOT NULL REFERENCES users(id),
    status          text,                 -- pending / approved / rejected (CHECK 없음)
    created_at      timestamptz DEFAULT now(),
    availability_id uuid REFERENCES mentor_availability(id),
    start_time      timestamptz,
    end_time        timestamptz,
    concern         text
);

CREATE TABLE connection_weights (
    id         uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    mentee_id  uuid NOT NULL REFERENCES mentee_profiles(id),
    mentor_id  uuid NOT NULL REFERENCES mentor_profiles(id),
    weight     numeric DEFAULT 1,
    updated_at timestamptz DEFAULT now(),
    CONSTRAINT unique_mentee_mentor_weight UNIQUE (mentee_id, mentor_id)
);

CREATE TABLE reviews (
    id             bigint PRIMARY KEY,
    created_at     timestamptz NOT NULL DEFAULT timezone('utc', now()),
    coffee_chat_id uuid NOT NULL UNIQUE REFERENCES coffee_chats(id),
    mentee_id      uuid NOT NULL REFERENCES auth.users(id),
    mentor_id      uuid NOT NULL REFERENCES auth.users(id),
    rating         integer NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content        text
);

CREATE TABLE user_likes (
    id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         uuid NOT NULL,        -- FK 없음
    liked_mentor_id uuid NOT NULL,        -- FK 없음
    created_at      timestamptz DEFAULT now(),
    UNIQUE (user_id, liked_mentor_id)
);

-- ---------- 채팅 ----------
CREATE TABLE chat_rooms (
    id             uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    coffee_chat_id uuid NOT NULL UNIQUE REFERENCES coffee_chats(id) ON DELETE CASCADE,
    mentor_id      uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    mentee_id      uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at     timestamptz DEFAULT now(),
    updated_at     timestamptz DEFAULT now()
);

CREATE TABLE chat_messages (
    id           uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_room_id uuid NOT NULL REFERENCES chat_rooms(id) ON DELETE CASCADE,
    sender_id    uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    message      text NOT NULL,
    created_at   timestamptz DEFAULT now(),
    is_read      boolean DEFAULT false
);

-- ---------- 기타 (코드에서 미사용) ----------
CREATE TABLE kv_store_8148f72a (
    key   text PRIMARY KEY,
    value jsonb NOT NULL
);

-- ---------- Indexes (PK / UNIQUE 외) ----------
CREATE INDEX idx_chat_messages_created   ON chat_messages (created_at DESC);
CREATE INDEX idx_chat_messages_room      ON chat_messages (chat_room_id);
CREATE INDEX idx_chat_messages_sender    ON chat_messages (sender_id);
CREATE INDEX idx_chat_rooms_coffee_chat  ON chat_rooms (coffee_chat_id);
CREATE INDEX idx_chat_rooms_mentee       ON chat_rooms (mentee_id);
CREATE INDEX idx_chat_rooms_mentor       ON chat_rooms (mentor_id);
CREATE INDEX idx_user_likes_mentor_id    ON user_likes (liked_mentor_id);
CREATE INDEX idx_user_likes_user_id      ON user_likes (user_id);
CREATE INDEX kv_store_8148f72a_key_idx   ON kv_store_8148f72a (key text_pattern_ops);

-- ---------- Functions ----------
-- 멘토 임베딩 유사도 검색 (pgvector 코사인 거리)
CREATE OR REPLACE FUNCTION public.match_mentors(
    query_embedding vector, match_threshold double precision, match_count integer)
RETURNS TABLE(id uuid, user_id uuid, full_name text, career_info text,
              location geography, profile_image_url text, similarity double precision)
LANGUAGE sql STABLE AS $$
  SELECT mp.id, mp.user_id, u.full_name, mp.career_info, mp.location, mp.profile_image_url,
         1 - (mp.embedding <=> query_embedding) AS similarity
  FROM mentor_profiles AS mp
  JOIN public.users AS u ON mp.user_id = u.id
  WHERE mp.embedding IS NOT NULL
    AND 1 - (mp.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;

-- 반경 내 멘토 검색 (PostGIS)
CREATE OR REPLACE FUNCTION public.nearby_mentors(
    mentee_location geography, radius_meters integer)
RETURNS TABLE(id uuid, user_id uuid, full_name text, career_info text,
              location geography, profile_image_url text, distance_meters double precision)
LANGUAGE sql STABLE AS $$
  SELECT mp.id, mp.user_id, u.full_name, mp.career_info, mp.location, mp.profile_image_url,
         ST_Distance(mp.location, mentee_location) AS distance_meters
  FROM mentor_profiles AS mp
  JOIN public.users AS u ON mp.user_id = u.id
  WHERE mp.location IS NOT NULL
    AND ST_DWithin(mp.location, mentee_location, radius_meters)
  ORDER BY distance_meters ASC;
$$;

-- 위치 갱신 (경도, 위도 → geography)
CREATE OR REPLACE FUNCTION public.update_mentee_location(
    target_mentee_id uuid, lon double precision, lat double precision)
RETURNS void LANGUAGE sql AS $$
  UPDATE public.mentee_profiles
  SET location = ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography
  WHERE id = target_mentee_id;
$$;

CREATE OR REPLACE FUNCTION public.update_mentor_location(
    target_mentor_id uuid, lon double precision, lat double precision)
RETURNS void LANGUAGE sql AS $$
  UPDATE public.mentor_profiles
  SET location = ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography
  WHERE id = target_mentor_id;
$$;

-- 멘티-멘토 연결 가중치 누적 (트리거 함수, 바인딩된 테이블은 미확인)
CREATE OR REPLACE FUNCTION public.update_connection_weights()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  INSERT INTO public.connection_weights (mentee_id, mentor_id, weight, updated_at)
  VALUES (NEW.mentee_id, NEW.mentor_id, 1, NOW())
  ON CONFLICT (mentee_id, mentor_id)
  DO UPDATE SET weight = connection_weights.weight + 1, updated_at = NOW();
  RETURN NEW;
END;
$$;
