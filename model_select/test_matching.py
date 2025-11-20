import time
print("🚀 프로그램 시작... 라이브러리 로딩 중...")

from sentence_transformers import SentenceTransformer, util
import torch

# ------------------------------------------------------------------
# 0. 상황 설정: 멘티의 구체적인 고민 (5줄 이상)
# ------------------------------------------------------------------
# 멘티는 'AWS 배포'와 '대용량 트래픽' 처리가 고민임.
mentee_query = """
안녕하세요, 저는 컴퓨터공학과 4학년 취준생입니다.
현재 Spring Boot로 게시판을 만들고 있는데, 
실제 현업에서 대용량 트래픽을 어떻게 처리하는지,
그리고 AWS 배포는 어떻게 하는지 경험이 부족해서 막막합니다.
단순한 코딩을 넘어 아키텍처 설계를 배우고 싶고,
제 코드를 꼼꼼하게 리뷰해주실 수 있는 멘토님을 찾습니다.
"""

mentors = [
    # [멘토 1: 정답] 단어 표현은 조금 다르지만 맥락이 완벽함
    # (멘티: "AWS 배포" <-> 멘토: "AWS 인프라 구축")
    # (멘티: "대용량 트래픽" <-> 멘토: "고가용성 서버, Black Friday 트래픽")
    """
    [판교 7년차 백엔드 리드]
    Spring Boot와 JPA를 사용하여 고가용성 서버를 구축합니다.
    Black Friday 같은 이벤트 상황의 트래픽 처리 노하우가 있습니다.
    주니어 개발자를 위한 코드 리뷰와 AWS 인프라 구축 경험을 전수해 드립니다.
    """,

    # [멘토 2: 오답] 키워드(AWS, Spring)는 겹치지만 직무가 다름(기획자)
    """
    [5년차 IT 서비스 기획자(PM)]
    개발자 출신은 아니지만 Spring, AWS 용어에 익숙합니다.
    백엔드 개발자와 소통하며 API 명세서를 작성하고 일정을 관리합니다.
    서비스의 기획부터 배포까지 전체적인 흐름(Flow)을 알려드립니다.
    """,

    # [멘토 3: 오답] 개발자지만 분야가 다름
    """
    [프론트엔드 개발 팀장]
    React와 Vue.js를 사용하여 사용자가 보는 화면(UI)을 개발합니다.
    백엔드 API와 통신하는 법은 알지만 서버 아키텍처는 모릅니다.
    """,
    
    # [멘토 4: 오답] 완전 무관
    """
    [홍대 카페 오너 바리스타]
    맛있는 커피를 내리는 법과 카페 창업 노하우를 알려드립니다.
    """
]

print("=" * 80)
print(f"🧑‍💻 멘티의 고민 (Query):\n{mentee_query.strip()}")
print("=" * 80)
print("\n⚔️ [매칭 방식 대결] 키워드 매칭 vs 임베딩 매칭\n")

# ------------------------------------------------------------------
# 1. 키워드 매칭 (Keyword Matching) - 처참한 현실
# ------------------------------------------------------------------
print("❌ [Round 1] 키워드 매칭 (단어 일치 여부)")
print("   방식: 멘티가 쓴 핵심 단어 3개가 멘토 소개글에 '똑같이' 있는가?")
print("   (검색 키워드: '대용량 트래픽', 'AWS 배포', '아키텍처 설계')")
print("-" * 80)

keywords = ["대용량 트래픽", "AWS 배포", "아키텍처 설계"]

for mentor in mentors:
    title = mentor.strip().split('\n')[0]
    # 키워드 포함 개수 세기
    matched_count = 0
    found_keywords = []
    for kw in keywords:
        if kw in mentor:
            matched_count += 1
            found_keywords.append(kw)
            
    if matched_count > 0:
        status = f"⚠️ 부분 매칭 ({matched_count}개: {found_keywords})"
    else:
        status = "🚫 매칭 실패 (0개)"
        
    print(f"{title:<20} -> {status}")

print("\n" + "=" * 80 + "\n")

# ------------------------------------------------------------------
# 2. 임베딩 매칭 (Embedding Matching) - 압도적 성능
# ------------------------------------------------------------------
print("✅ [Round 2] 임베딩 매칭 (의미 기반)")
print("   방식: 다국어 모델(Multilingual-L12)을 사용해 '문맥 유사도' 계산")
print("-" * 80)

# 모델 로드
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# 임베딩 및 점수 계산
query_embedding = model.encode(mentee_query, convert_to_tensor=True)
doc_embeddings = model.encode(mentors, convert_to_tensor=True)
cosine_scores = util.cos_sim(query_embedding, doc_embeddings)[0]

results = []
for i in range(len(mentors)):
    score = cosine_scores[i].item() * 100
    title = mentors[i].strip().split('\n')[0]
    results.append((title, score))

results.sort(key=lambda x: x[1], reverse=True)

for title, score in results:
    if score >= 65:
        grade = "🥇 (정확한 추천)"
    elif score >= 50:
        grade = "🥈 (관련 있음)"
    else:
        grade = "❌ (관련 없음)"
    print(f"{title:<20} -> 점수: {score:.1f}점 {grade}")

print("-" * 80)