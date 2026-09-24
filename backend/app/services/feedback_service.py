# backend/app/services/feedback_service.py
"""
사용자 피드백 기반 개인화 매칭
- 좋아요/커피챗 신청 데이터 학습
- 개인별 선호도 반영
"""
from app.core.config import supabase
from typing import Dict, List

def get_user_feedback_profile(user_id: str) -> Dict:
    """
    사용자의 과거 피드백 데이터 분석
    
    Returns:
        {
            'preferred_keywords': [...],  # 선호하는 키워드
            'preferred_distance': float,   # 선호하는 평균 거리
            'interaction_count': int       # 총 상호작용 수
        }
    """
    try:
        # 1. 커피챗 신청 내역 조회
        bookings = supabase.table('coffee_chats') \
            .select('mentor_id, status') \
            .eq('mentee_id', user_id) \
            .in_('status', ['approved', 'pending']) \
            .execute()
        
        if not bookings.data or len(bookings.data) < 3:
            return None  # 데이터 부족
        
        # 2. 상호작용한 멘토들의 프로필 분석
        mentor_ids = [b['mentor_id'] for b in bookings.data]
        
        mentors = supabase.table('mentor_profiles') \
            .select('career_info, location') \
            .in_('user_id', mentor_ids) \
            .execute()
        
        # 3. 키워드 추출
        from app.services.ml_service import extract_career_keywords
        
        all_keywords = []
        for mentor in mentors.data:
            keywords = extract_career_keywords(mentor.get('career_info', ''))
            all_keywords.extend(keywords)
        
        # 빈도 계산
        keyword_freq = {}
        for kw in all_keywords:
            keyword_freq[kw] = keyword_freq.get(kw, 0) + 1
        
        # 상위 10개 키워드
        top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        preferred_keywords = [kw for kw, _ in top_keywords]
        
        return {
            'preferred_keywords': preferred_keywords,
            'interaction_count': len(bookings.data),
            'confidence': min(len(bookings.data) / 10, 1.0)  # 신뢰도 (최대 1.0)
        }
    
    except Exception as e:
        print(f"⚠️ 피드백 프로필 생성 실패: {e}")
        return None


def personalize_match_scores(
    user_id: str,
    matches: List[Dict],
    role: str = 'mentee'
) -> List[Dict]:
    """
    사용자 피드백 기반으로 매칭 점수 조정
    """
    if role != 'mentee':  # 현재는 멘티만 지원
        return matches
    
    feedback_profile = get_user_feedback_profile(user_id)
    
    if not feedback_profile or feedback_profile['interaction_count'] < 3:
        print(f"ℹ️ 피드백 데이터 부족 (n={feedback_profile['interaction_count'] if feedback_profile else 0})")
        return matches
    
    print(f"✅ 개인화 적용: 선호 키워드 = {feedback_profile['preferred_keywords'][:3]}...")
    
    from app.services.ml_service import extract_career_keywords
    
    # 각 후보의 키워드와 비교
    for match in matches:
        candidate_text = match.get('text', '')
        candidate_keywords = set(extract_career_keywords(candidate_text))
        
        # 선호 키워드와의 일치도
        preferred_set = set(feedback_profile['preferred_keywords'])
        intersection = len(candidate_keywords & preferred_set)
        
        if intersection > 0:
            # 보너스 점수 (신뢰도에 비례)
            bonus = intersection * 5 * feedback_profile['confidence']
            match['personalized_bonus'] = round(bonus, 2)
            match['final_score'] = min(match['final_score'] + bonus, 100)
    
    # 재정렬
    matches.sort(key=lambda x: x['final_score'], reverse=True)
    
    return matches
