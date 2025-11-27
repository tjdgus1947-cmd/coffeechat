# backend/regenerate_embeddings_enhanced.py
"""
전처리 + 키워드 강화가 적용된 새 임베딩으로 재생성
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from app.core.config import supabase
from app.services.ml_service import generate_embedding
import json
from tqdm import tqdm  # 진행 바 표시

def regenerate_all_embeddings():
    """모든 멘토/멘티의 임베딩을 새 버전으로 재생성"""
    
    print("=" * 60)
    print("🔄 임베딩 재생성 시작 (전처리 + 키워드 강화 적용)")
    print("=" * 60)
    
    # 1. 멘토 임베딩 재생성
    print("\n[1/2] 멘토 프로필 처리 중...")
    mentor_profiles = supabase.table('mentor_profiles') \
        .select('user_id, career_info') \
        .not_.is_('career_info', 'null') \
        .execute()
    
    mentor_count = 0
    mentor_failed = 0
    
    if mentor_profiles.data:
        for profile in tqdm(mentor_profiles.data, desc="멘토", unit="명"):
            try:
                user_id = profile['user_id']
                text = profile['career_info']
                
                # 🔥 새 임베딩 생성 (전처리 + 키워드 강화)
                new_embedding = generate_embedding(text, use_enhancement=True)
                
                # DB 업데이트
                supabase.table('mentor_profiles') \
                    .update({'embedding': json.dumps(new_embedding)}) \
                    .eq('user_id', user_id) \
                    .execute()
                
                mentor_count += 1
            
            except Exception as e:
                mentor_failed += 1
                print(f"\n  ❌ 멘토 {user_id[:8]}... 실패: {e}")
    
    print(f"\n멘토 완료: {mentor_count}명 성공, {mentor_failed}명 실패")
    
    # 2. 멘티 임베딩 재생성
    print("\n[2/2] 멘티 프로필 처리 중...")
    mentee_profiles = supabase.table('mentee_profiles') \
        .select('user_id, current_situation, career_goal') \
        .not_.is_('current_situation', 'null') \
        .execute()
    
    mentee_count = 0
    mentee_failed = 0
    
    if mentee_profiles.data:
        for profile in tqdm(mentee_profiles.data, desc="멘티", unit="명"):
            try:
                user_id = profile['user_id']
                situation = profile.get('current_situation', '')
                goal = profile.get('career_goal', '')
                
                # 전체 텍스트 결합
                full_text = f"{situation} {goal}".strip()
                
                if full_text:
                    # 🔥 새 임베딩 생성
                    new_embedding = generate_embedding(full_text, use_enhancement=True)
                    
                    # DB 업데이트
                    supabase.table('mentee_profiles') \
                        .update({'embedding': json.dumps(new_embedding)}) \
                        .eq('user_id', user_id) \
                        .execute()
                    
                    mentee_count += 1
            
            except Exception as e:
                mentee_failed += 1
                print(f"\n  ❌ 멘티 {user_id[:8]}... 실패: {e}")
    
    print(f"\n멘티 완료: {mentee_count}명 성공, {mentee_failed}명 실패")
    
    # 최종 결과
    print("\n" + "=" * 60)
    print(f"✅ 재생성 완료!")
    print(f"   - 멘토: {mentor_count}명 (실패 {mentor_failed}명)")
    print(f"   - 멘티: {mentee_count}명 (실패 {mentee_failed}명)")
    print(f"   - 총: {mentor_count + mentee_count}명")
    print("=" * 60)
    
    # 샘플 검증
    print("\n🔍 샘플 검증 중...")
    if mentor_profiles.data and len(mentor_profiles.data) > 0:
        sample = mentor_profiles.data[0]
        verify_response = supabase.table('mentor_profiles') \
            .select('embedding') \
            .eq('user_id', sample['user_id']) \
            .execute()
        
        if verify_response.data:
            emb = json.loads(verify_response.data[0]['embedding'])
            print(f"✅ 검증 통과: 임베딩 차원 = {len(emb)} (예상: 1024)")

if __name__ == "__main__":
    try:
        # tqdm 설치 확인
        try:
            from tqdm import tqdm
        except ImportError:
            print("⚠️ tqdm 미설치. 진행 바 없이 실행됩니다.")
            print("   설치: pip install tqdm")
            tqdm = lambda x, **kwargs: x  # 더미 함수
        
        regenerate_all_embeddings()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨")
    except Exception as e:
        print(f"\n❌ 치명적 오류: {e}")
        import traceback
        traceback.print_exc()