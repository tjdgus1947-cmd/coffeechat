-- =====================================================================
-- 000_precheck.sql : 마이그레이션 전 데이터 점검 (읽기 전용, DB 변경 없음)
-- 결과가 모두 "0행"이면 001을 그대로 실행해도 된다.
-- 행이 나오면 001이 실패(전체 롤백)하므로, 결과를 보고 데이터를 먼저 정리한다.
-- =====================================================================

-- 1) 같은 슬롯에 걸린 예약이 2건 이상인가? (UNIQUE 추가 전 확인)
select availability_id, count(*)
from coffee_chats
where availability_id is not null
group by availability_id
having count(*) > 1;

-- 2) 허용 목록 밖의 status 값이 있는가? (CHECK 추가 전 확인)
select status, count(*)
from coffee_chats
where status is null or status not in ('pending', 'approved', 'rejected')
group by status;

-- 3) 임베딩 차원이 1024가 아닌 행이 있는가? (vector(1024) 변환 전 확인)
select 'mentor' as tbl, vector_dims(embedding) as dims, count(*)
from mentor_profiles where embedding is not null and vector_dims(embedding) <> 1024
group by 2
union all
select 'mentee', vector_dims(embedding), count(*)
from mentee_profiles where embedding is not null and vector_dims(embedding) <> 1024
group by 2;

-- 4) 존재하지 않는 멘토를 가리키는 슬롯이 있는가? (FK 추가 전 확인)
select a.id, a.mentor_id
from mentor_availability a
left join mentor_profiles m on m.id = a.mentor_id
where m.id is null;

-- 5) 존재하지 않는 사용자를 가리키는 찜이 있는가? (FK 추가 전 확인)
select l.id, l.user_id, l.liked_mentor_id
from user_likes l
left join users u1 on u1.id = l.user_id
left join users u2 on u2.id = l.liked_mentor_id
where u1.id is null or u2.id is null;

-- 6) 종료 시각이 시작 시각보다 빠르거나 같은 슬롯이 있는가?
select id, start_time, end_time
from mentor_availability
where end_time <= start_time;
