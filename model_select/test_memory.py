import os
import psutil
from sentence_transformers import SentenceTransformer

def get_memory_usage_mb():
    """ 현재 프로세스가 사용 중인 실제 메모리(RSS)를 MB 단위로 반환 """
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / (1024 * 1024)

# --- 1. 아무것도 로드하지 않았을 때 (기본) ---
mem_before = get_memory_usage_mb()
print(f"스크립트 기본 실행 메모리: {mem_before:.2f} MB")

# --- 2. 모델 로드 (★ 한 번에 하나씩만 주석 해제해서 테스트 ★) ---
model_name = ""

# 테스트 1: all-MiniLM-L6-v2 (약 80MB)
model_name = 'all-MiniLM-L6-v2'

# 테스트 2: 한국어 SBERT (약 440MB)
# model_name = 'snunlp/KR-SBERT-V40K-klueNLI-augSTS'

# 테스트 3: 다국어 MiniLM-L12 (약 471MB)
# model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'


if model_name:
    print(f"\n'{model_name}' 모델 로드 중...")
    try:
        model = SentenceTransformer(model_name)
        print("모델 로드 성공.")
        
        mem_after = get_memory_usage_mb()
        
        print("\n--- '" + model_name + "' 테스트 결과 ---")
        print(f"모델 로드 후 총 메모리: {mem_after:.2f} MB")
        print(f"모델 로드 전 기본 메모리: {mem_before:.2f} MB")
        print("-" * 30)
        print(f"모델이 추가로 사용한 순수 RAM: {mem_after - mem_before:.2f} MB")
    
    except Exception as e:
        print(f"모델 로드 실패: {e}")
else:
    print("\n테스트할 모델의 주석을 해제해주세요.")