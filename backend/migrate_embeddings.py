# migrate_embeddings.py
import psycopg2
from app.services.ml_service import generate_embedding

# 👇 사진에서 추출한 정확한 접속 정보입니다.
# migrate_embeddings.py

DB_CONFIG = {
    # 1. Host: 아까 로그에 떴던 'Pooler 주소'를 씁니다. (Direct 주소 쓰면 절대 안 됨!)
    # (IPv4를 지원하는 우회 도로입니다)
    "host": "aws-1-ap-southeast-1.pooler.supabase.com", 

    "dbname": "postgres",

    # 2. User: [중요] Pooler를 쓸 땐 아이디 뒤에 프로젝트ID가 꼭 붙어야 합니다.
    "user": "postgres.qnomybedioqfzdqdkucs",

    # 3. Port: [핵심] 6543 대신 '5432'를 씁니다.
    # (Pooler도 5432번으로 접속을 받아줍니다. 이건 방화벽에 안 걸립니다.)
    "port": "5432", 

    # 4. Password: 재설정한 비밀번호 입력
    "password": "Da2ga3dk1!!",
    
    "sslmode": "require"
}

def migrate_data():
    conn = None
    try:
        # DB 연결
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print(f"✅ 수파베이스({DB_CONFIG['host']}) 연결 성공!")
        print("데이터 마이그레이션을 시작합니다...")

        # ==========================================
        # 1. 멘토 프로필 업데이트
        # ==========================================
        print("\n[1/2] 멘토 프로필 업데이트 중...")
        cur.execute("SELECT id, career_info FROM mentor_profiles")
        mentors = cur.fetchall()

        for m_id, career_info in mentors:
            if career_info:
                # 텍스트 -> 1024차원 벡터 변환 (bge-m3)
                new_vector = generate_embedding(career_info)
                # 업데이트
                cur.execute(
                    "UPDATE mentor_profiles SET embedding = %s WHERE id = %s",
                    (str(new_vector), m_id)
                )
        print(f"👉 멘토 {len(mentors)}명 처리 완료.")

        # ==========================================
        # 2. 멘티 프로필 업데이트
        # ==========================================
        print("\n[2/2] 멘티 프로필 업데이트 중...")
        cur.execute("SELECT id, current_situation, career_goal FROM mentee_profiles")
        mentees = cur.fetchall()

        for m_id, situation, goal in mentees:
            full_text = f"{situation or ''} {goal or ''}".strip()
            
            if full_text:
                new_vector = generate_embedding(full_text)
                cur.execute(
                    "UPDATE mentee_profiles SET embedding = %s WHERE id = %s",
                    (str(new_vector), m_id)
                )
        print(f"👉 멘티 {len(mentees)}명 처리 완료.")

        conn.commit()
        print("\n🎉 모든 마이그레이션이 성공적으로 완료되었습니다!")

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ 에러 발생: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_data()