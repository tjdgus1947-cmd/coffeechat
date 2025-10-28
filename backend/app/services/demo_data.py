"""
Demo data for prototype testing
"""
import random
from typing import List, Dict

# Demo Mentee (User)
DEMO_MENTEE = {
    "id": "mentee-1",
    "name": "김멘티",
    "email": "mentee@example.com",
    "field": "경영학",
    "current_situation": "대학교 3학년 경영학과 재학 중입니다.",
    "desired_field": "회계 분야로 진출하고 싶고, CPA 자격증을 준비하고 있습니다.",
    "interests": ["CPA", "회계", "재무", "세무"],
    "location": {"lat": 37.5665, "lng": 126.9780, "address": "서울특별시 중구"},
}

# Demo Mentors
DEMO_MENTORS = [
    {
        "id": "mentor-1",
        "name": "이회계",
        "email": "lee@example.com",
        "field": "CPA",
        "company": "삼일회계법인",
        "position": "시니어 회계사",
        "years_of_experience": 7,
        "career_summary": "삼일회계법인에서 7년간 근무하며 대기업 회계감사 및 세무 자문을 담당했습니다. CPA 자격증을 보유하고 있으며, 법인세와 부가세에 특화되어 있습니다.",
        "specialties": "회계감사, 법인세, 부가세, 재무제표 분석",
        "tags": ["회계", "CPA", "세무", "감사"],
        "location": {"lat": 37.5700, "lng": 126.9850, "address": "서울특별시 종로구"},
        "is_verified": True,
        "chat_history": 3,
        "distance": 2.5,
        "match_score": 95,
    },
    {
        "id": "mentor-2",
        "name": "박재무",
        "email": "park@example.com",
        "field": "재무관리",
        "company": "삼성증권",
        "position": "선임 애널리스트",
        "years_of_experience": 5,
        "career_summary": "삼성증권에서 5년간 기업 재무 분석 및 투자 자문을 담당했습니다. 재무제표 분석과 기업 가치 평가에 전문성을 가지고 있습니다.",
        "specialties": "재무분석, 투자자문, 기업가치평가, 자산관리",
        "tags": ["재무", "투자", "자산관리", "증권"],
        "location": {"lat": 37.5600, "lng": 126.9700, "address": "서울특별시 중구"},
        "is_verified": True,
        "chat_history": 1,
        "distance": 1.8,
        "match_score": 88,
    },
    {
        "id": "mentor-3",
        "name": "최경영",
        "email": "choi@example.com",
        "field": "경영전략",
        "company": "현대자동차",
        "position": "전략기획 팀장",
        "years_of_experience": 10,
        "career_summary": "현대자동차 전략기획팀에서 10년간 근무하며 신사업 기획 및 M&A를 담당했습니다. MBA 학위를 보유하고 있습니다.",
        "specialties": "경영전략, 사업기획, M&A, 조직관리",
        "tags": ["경영", "전략", "MBA", "기획"],
        "location": {"lat": 37.5750, "lng": 127.0000, "address": "서울특별시 강남구"},
        "is_verified": True,
        "chat_history": 0,
        "distance": 3.2,
        "match_score": 75,
    },
    {
        "id": "mentor-4",
        "name": "정세무",
        "email": "jung@example.com",
        "field": "세무사",
        "company": "김앤장 법률사무소",
        "position": "세무사",
        "years_of_experience": 8,
        "career_summary": "김앤장에서 8년간 세무 자문 및 조세 소송을 담당했습니다. 세무사 자격증을 보유하고 있으며 법인세에 특화되어 있습니다.",
        "specialties": "법인세, 부가세, 조세소송, 세무조사",
        "tags": ["세무", "법인세", "부가세", "조세"],
        "location": {"lat": 37.5650, "lng": 126.9750, "address": "서울특별시 중구"},
        "is_verified": True,
        "chat_history": 2,
        "distance": 1.5,
        "match_score": 92,
    },
    {
        "id": "mentor-5",
        "name": "강마케팅",
        "email": "kang@example.com",
        "field": "마케팅",
        "company": "LG전자",
        "position": "마케팅 이사",
        "years_of_experience": 12,
        "career_summary": "LG전자에서 12년간 브랜드 마케팅 및 디지털 마케팅을 담당했습니다. 글로벌 캠페인 다수 진행 경험이 있습니다.",
        "specialties": "브랜드 마케팅, 디지털 마케팅, SNS 마케팅, 캠페인 기획",
        "tags": ["마케팅", "브랜딩", "디지털", "SNS"],
        "location": {"lat": 37.5550, "lng": 126.9900, "address": "서울특별시 영등포구"},
        "is_verified": True,
        "chat_history": 0,
        "distance": 4.5,
        "match_score": 62,
    },
    {
        "id": "mentor-6",
        "name": "윤금융",
        "email": "yoon@example.com",
        "field": "금융공학",
        "company": "KB국민은행",
        "position": "리스크 관리 팀장",
        "years_of_experience": 9,
        "career_summary": "KB국민은행에서 9년간 금융상품 개발 및 리스크 관리를 담당했습니다. CFA 자격증을 보유하고 있습니다.",
        "specialties": "금융공학, 리스크관리, 파생상품, 포트폴리오",
        "tags": ["금융", "CFA", "리스크", "파생상품"],
        "location": {"lat": 37.5680, "lng": 126.9830, "address": "서울특별시 종로구"},
        "is_verified": True,
        "chat_history": 1,
        "distance": 2.0,
        "match_score": 78,
    },
    {
        "id": "mentor-7",
        "name": "한법무",
        "email": "han@example.com",
        "field": "법무",
        "company": "삼성전자",
        "position": "법무 팀장",
        "years_of_experience": 11,
        "career_summary": "삼성전자 법무팀에서 11년간 계약 검토 및 송무를 담당했습니다. 변호사 자격증을 보유하고 있습니다.",
        "specialties": "계약법, 상사법, 지적재산권, 송무",
        "tags": ["법무", "변호사", "계약", "송무"],
        "location": {"lat": 37.5720, "lng": 127.0050, "address": "서울특별시 강남구"},
        "is_verified": True,
        "chat_history": 0,
        "distance": 4.0,
        "match_score": 58,
    },
    {
        "id": "mentor-8",
        "name": "서인사",
        "email": "seo@example.com",
        "field": "인사관리",
        "company": "네이버",
        "position": "HR 총괄",
        "years_of_experience": 13,
        "career_summary": "네이버에서 13년간 인사 정책 수립 및 조직문화 개선을 담당했습니다. 채용, 평가, 보상 전반에 걸친 경험이 있습니다.",
        "specialties": "인사전략, 채용, 조직문화, 보상체계",
        "tags": ["인사", "HR", "채용", "조직문화"],
        "location": {"lat": 37.5590, "lng": 126.9470, "address": "서울특별시 마포구"},
        "is_verified": True,
        "chat_history": 0,
        "distance": 3.8,
        "match_score": 55,
    },
]

# Tag weights based on mentee interests and chat history
TAG_WEIGHTS = {
    "CPA": 4,
    "회계": 4,
    "세무": 3,
    "재무": 2,
    "감사": 2,
    "투자": 1,
    "경영": 1,
    "전략": 1,
    "마케팅": 0,
    "브랜딩": 0,
}

def get_demo_mentee() -> Dict:
    """Get demo mentee data"""
    return DEMO_MENTEE

def get_demo_mentors(limit: int = None) -> List[Dict]:
    """Get demo mentors data"""
    mentors = DEMO_MENTORS.copy()
    if limit:
        return mentors[:limit]
    return mentors

def get_demo_mentor(mentor_id: str) -> Dict:
    """Get specific demo mentor"""
    for mentor in DEMO_MENTORS:
        if mentor["id"] == mentor_id:
            return mentor
    return None

def get_recommended_mentors(limit: int = 10) -> List[Dict]:
    """Get recommended mentors sorted by match score"""
    mentors = sorted(DEMO_MENTORS, key=lambda x: x["match_score"], reverse=True)
    return mentors[:limit]

def get_network_data() -> Dict:
    """
    Generate network graph data
    Returns nodes and edges for visualization
    """
    nodes = []
    edges = []
    
    # Central mentee node
    nodes.append({
        "id": "mentee-center",
        "type": "mentee",
        "label": DEMO_MENTEE["name"],
        "data": DEMO_MENTEE,
    })
    
    # Tag nodes
    unique_tags = set()
    for mentor in DEMO_MENTORS:
        unique_tags.update(mentor["tags"])
    
    for tag in unique_tags:
        nodes.append({
            "id": f"tag-{tag}",
            "type": "tag",
            "label": tag,
            "weight": TAG_WEIGHTS.get(tag, 0),
        })
        
        # Edge from mentee to tag (if in interests)
        if tag in DEMO_MENTEE["interests"]:
            edges.append({
                "id": f"edge-mentee-{tag}",
                "source": "mentee-center",
                "target": f"tag-{tag}",
                "type": "interest",
                "animated": True,
            })
    
    # Mentor nodes
    for mentor in DEMO_MENTORS:
        nodes.append({
            "id": mentor["id"],
            "type": "mentor",
            "label": mentor["name"],
            "data": mentor,
        })
        
        # Edge from mentee to mentor
        edges.append({
            "id": f"edge-{mentor['id']}",
            "source": "mentee-center",
            "target": mentor["id"],
            "type": "connection",
            "animated": mentor["chat_history"] > 0,
            "weight": mentor["chat_history"],
        })
        
        # Edges from mentor to tags
        for tag in mentor["tags"]:
            edges.append({
                "id": f"edge-{mentor['id']}-{tag}",
                "source": mentor["id"],
                "target": f"tag-{tag}",
                "type": "expertise",
            })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "mentee": DEMO_MENTEE,
        "tag_weights": TAG_WEIGHTS,
    }

def search_mentors(query: str = "", tags: List[str] = None, max_distance: float = None) -> List[Dict]:
    """
    Search mentors with filters
    """
    mentors = DEMO_MENTORS.copy()
    
    # Filter by tags
    if tags:
        mentors = [m for m in mentors if any(tag in m["tags"] for tag in tags)]
    
    # Filter by distance
    if max_distance:
        mentors = [m for m in mentors if m["distance"] <= max_distance]
    
    # Filter by query (search in name, company, field)
    if query:
        query_lower = query.lower()
        mentors = [
            m for m in mentors
            if query_lower in m["name"].lower()
            or query_lower in m["company"].lower()
            or query_lower in m["field"].lower()
            or query_lower in m["specialties"].lower()
        ]
    
    return mentors