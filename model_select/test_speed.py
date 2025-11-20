import time
from sentence_transformers import SentenceTransformer
# TensorFlow 관련 임포트 모두 제거

# ------------------------------------------------------------------
# 0. 테스트 준비
# ------------------------------------------------------------------
print("테스트를 준비합니다. (3개 모델 로딩, 시간이 걸릴 수 있습니다...)")

# 테스트에 사용할 샘플 텍스트 10개 묶음 (Batch)
batch_texts = [
    "저는 법학전문대학원을 준비 중이고, 계약서 검토나 기업 법무에 관심이 많습니다.",
    "AI와 데이터 과학 분야에서 멘토를 찾고 있습니다.",
    "프론트엔드 개발자로 취업하고 싶은데, 리액트와 Vue.js 포트폴리오 조언이 필요해요.",
    "스타트업 창업을 준비 중입니다. 투자 유치 경험이 있는 멘토님을 만나고 싶어요.",
    "금융권 취업, 특히 은행 PB 직무에 대해 현직자의 이야기가 궁금합니다.",
    "UX/UI 디자이너로 이직을 고민 중입니다. 제 포트폴리오를 검토해 주실 수 있나요?",
    "백엔드 개발자입니다. Java, Spring, MSA 환경에 대해 깊게 배우고 싶습니다.",
    "마케팅 직무, 그중에서도 퍼포먼스 마케팅에 대해 실무를 배우고 싶어요.",
    "공기업 취업을 준비하는데 NCS와 면접 팁이 궁금합니다.",
    "데이터 엔지니어링, Airflow와 Spark를 다루는 현직 멘토님을 찾습니다."
]

print(f"\n✅ 테스트 문장: {len(batch_texts)}개 묶음 (Batch)")

# --- 모델 1: all-MiniLM-L6-v2 로드 ---
try:
    model_mini_lm = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ 1. all-MiniLM-L6-v2 모델 로드 성공 (약 80MB, 6-Layer)")
except Exception as e:
    print(f"❌ 1. all-MiniLM-L6-v2 로드 실패: {e}")
    model_mini_lm = None

# --- 모델 2: 한국어 SBERT (KoBERT 기반) 로드 ---
try:
    model_korean_sbert = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')
    print("✅ 2. 한국어 SBERT 모델 로드 성공 (약 440MB, Korean-Specific)")
except Exception as e:
    print(f"❌ 2. 한국어 SBERT 로드 실패: {e}")
    model_korean_sbert = None

# --- ⭐️⭐️⭐️ 모델 3: 다국어 SBERT (12-Layer) 로드 ⭐️⭐️⭐️ ---
try:
    model_multilingual = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    print("✅ 3. 다국어 MiniLM-L12 모델 로드 성공 (약 471MB, 12-Layer)")
except Exception as e:
    print(f"❌ 3. 다국어 MiniLM-L12 로드 실패: {e}")
    model_multilingual = None


print("-" * 50)
print(f"각 모델이 {len(batch_texts)}개 문장 묶음을 한 번에 처리하는 속도를 3회씩 측정합니다.")
print("-" * 50)

# ------------------------------------------------------------------
# 1. all-MiniLM-L6-v2 (경량) 배치 속도 측정
# ------------------------------------------------------------------
if model_mini_lm:
    print("🚀 [테스트 1] all-MiniLM-L6-v2 (80MB, 6-Layer)")
    for i in range(3):
        start_time = time.perf_counter()
        embeddings = model_mini_lm.encode(batch_texts)
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000 # ms
        print(f"  (시도 {i+1}) {len(batch_texts)}개 처리 시간: {duration:.2f} ms")

# ------------------------------------------------------------------
# 2. 한국어 SBERT (헤비급) 배치 속도 측정
# ------------------------------------------------------------------
if model_korean_sbert:
    print("\n🚀 [테스트 2] 한국어 SBERT (440MB, Korean-Specific)")
    for i in range(3):
        start_time = time.perf_counter()
        embeddings = model_korean_sbert.encode(batch_texts)
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000 # ms
        print(f"  (시도 {i+1}) {len(batch_texts)}개 처리 시간: {duration:.2f} ms")

# ------------------------------------------------------------------
# 3. 다국어 SBERT (헤비급) 배치 속도 측정
# ------------------------------------------------------------------
if model_multilingual:
    print("\n🚀 [테스트 3] 다국어 MiniLM-L12 (471MB, 12-Layer)")
    for i in range(3):
        start_time = time.perf_counter()
        embeddings = model_multilingual.encode(batch_texts)
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000 # ms
        print(f"  (시도 {i+1}) {len(batch_texts)}개 처리 시간: {duration:.2f} ms")

print("-" * 50)
print("테스트 완료.")