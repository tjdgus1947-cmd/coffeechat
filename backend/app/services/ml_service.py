# backend/app/services/ml_service.py
from sentence_transformers import SentenceTransformer, util
import torch
import re

# GPU 가속 설정
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Loading AI Model on {device}...")

# bge-m3 모델 로드
try:
    model = SentenceTransformer('BAAI/bge-m3', device=device)
    print("✅ SentenceTransformer (BAAI/bge-m3) 모델 로드 성공")
except Exception as e:
    print(f"❌ SentenceTransformer 모델 로드 실패: {e}")
    model = None


# ==========================================
# 🔥 신규 추가: 텍스트 전처리
# ==========================================

def preprocess_text(text: str) -> str:
    """
    임베딩 생성 전 텍스트 정제
    - 불필요한 공백 제거
    - 특수문자 정리
    - 소문자 변환 (영문)
    """
    if not text:
        return ""
    
    # 1. 여러 공백을 하나로
    text = ' '.join(text.split())
    
    # 2. 특수문자 제거 (한글, 영문, 숫자, 기본 구두점만 유지)
    text = re.sub(r'[^\w\s가-힣.,!?()+-]', ' ', text)
    
    # 3. 중복 공백 다시 정리
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def extract_career_keywords(text: str) -> list[str]:
    """
    커리어 관련 핵심 키워드 추출
    """
    if not text:
        return []
    
    text_lower = text.lower()
    
    # 직무/기술 키워드
    tech_keywords = [
        'python', 'java', 'javascript', 'react', 'vue', 'node', 'spring',
        'backend', 'frontend', 'fullstack', 'ai', 'ml', 'data', 'devops',
        'aws', 'gcp', 'docker', 'kubernetes', 'sql', 'nosql',
        '백엔드', '프론트엔드', '풀스택', '개발', '서버', '데이터베이스',
        '인공지능', '머신러닝', '딥러닝', '데이터', '분석'
    ]
    
    # 산업/직군 키워드
    industry_keywords = [
        'startup', 'fintech', 'edtech', 'healthcare', 'e-commerce',
        '스타트업', '핀테크', '에듀테크', '헬스케어', '이커머스',
        '기획', '디자인', 'ui', 'ux', '마케팅', '영업', '전략',
        'pm', 'po', 'designer', 'marketer'
    ]
    
    # 경력/목표 키워드
    career_keywords = [
        'junior', 'senior', 'lead', 'cto', 'ceo',
        '신입', '주니어', '시니어', '리드', '이직', '취업', '커리어',
        '년차', 'year', 'experience', '경력', '경험'
    ]
    
    all_keywords = tech_keywords + industry_keywords + career_keywords
    found_keywords = [kw for kw in all_keywords if kw in text_lower]
    
    return found_keywords


def enhance_text_with_keywords(text: str) -> str:
    """
    원본 텍스트에 추출된 키워드를 추가하여 임베딩 품질 향상
    """
    if not text:
        return text
    
    keywords = extract_career_keywords(text)
    
    if keywords:
        # 키워드를 텍스트 끝에 추가 (중복 제거)
        keyword_str = ' '.join(set(keywords))
        return f"{text} [핵심역량: {keyword_str}]"
    
    return text


# ==========================================
# 🔥 개선된 임베딩 생성 함수
# ==========================================

def generate_embedding(text: str, use_enhancement: bool = True) -> list[float]:
    """
    텍스트를 1024차원 임베딩 벡터로 변환 (전처리 + 키워드 강화 옵션)
    
    Args:
        text: 원본 텍스트
        use_enhancement: 전처리 및 키워드 강화 사용 여부
    
    Returns:
        1024차원 임베딩 벡터
    """
    if model is None:
        raise Exception("ML 모델이 로드되지 않았습니다.")
    
    if not text:
        return [0.0] * 1024
    
    # 전처리 적용
    if use_enhancement:
        processed_text = preprocess_text(text)
        enhanced_text = enhance_text_with_keywords(processed_text)
    else:
        enhanced_text = text
    
    # 임베딩 생성 (정규화 포함)
    embedding = model.encode(enhanced_text, normalize_embeddings=True)
    
    return embedding.tolist()


# ==========================================
# 🔥 개선된 유사도 계산 (가중치 옵션)
# ==========================================

def calculate_match_score(
    embedding1: list[float], 
    embedding2: list[float],
    text1: str = "",
    text2: str = "",
    keyword_weight: float = 0.0  # 키워드 일치 가중치 (0~0.3 권장)
) -> float:
    """
    두 임베딩 벡터 간의 유사도 계산 (키워드 보너스 옵션)
    
    Args:
        embedding1, embedding2: 임베딩 벡터
        text1, text2: 원본 텍스트 (키워드 추출용, 선택)
        keyword_weight: 키워드 일치 시 추가 점수 (0~0.3)
    
    Returns:
        0~100 사이의 유사도 점수
    """
    if not embedding1 or not embedding2:
        return 0.0

    # 1. 코사인 유사도 계산
    cosine_score = util.cos_sim(embedding1, embedding2).item()
    
    if cosine_score < 0:
        cosine_score = 0.0
    
    base_score = cosine_score * 100
    
    # 2. 키워드 일치 보너스 (선택)
    keyword_bonus = 0.0
    if keyword_weight > 0 and text1 and text2:
        keywords1 = set(extract_career_keywords(text1))
        keywords2 = set(extract_career_keywords(text2))
        
        if keywords1 and keywords2:
            # Jaccard 유사도
            intersection = len(keywords1 & keywords2)
            union = len(keywords1 | keywords2)
            
            if union > 0:
                jaccard = intersection / union
                keyword_bonus = jaccard * 100 * keyword_weight
    
    final_score = min(base_score + keyword_bonus, 100)
    
    return round(final_score, 2)


# ==========================================
# 🔥 신규: 배치 임베딩 생성 (성능 최적화)
# ==========================================

def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    여러 텍스트를 한 번에 임베딩 생성 (속도 향상)
    
    Args:
        texts: 텍스트 리스트
    
    Returns:
        임베딩 벡터 리스트
    """
    if model is None:
        raise Exception("ML 모델이 로드되지 않았습니다.")
    
    if not texts:
        return []
    
    # 전처리
    processed_texts = [preprocess_text(t) for t in texts]
    enhanced_texts = [enhance_text_with_keywords(t) for t in processed_texts]
    
    # 배치 임베딩 (GPU 사용 시 훨씬 빠름)
    embeddings = model.encode(
        enhanced_texts, 
        normalize_embeddings=True,
        batch_size=32,  # GPU 메모리에 맞게 조절
        show_progress_bar=True
    )
    
    return [emb.tolist() for emb in embeddings]