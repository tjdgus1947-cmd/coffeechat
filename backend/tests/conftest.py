"""
pytest 공통 설정

무거운 외부 의존성(torch, sentence-transformers 모델 다운로드, Supabase, Gemini)은
테스트에서 가짜 모듈로 대체해, 모델 없이도 API·점수 로직을 빠르게 검증한다.
"""
import sys
import types
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))


def _stub(name, **attrs):
    mod = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    sys.modules[name] = mod
    return mod


class _FakeCrossEncoder:
    """(쿼리, 문서) 쌍마다 공통 bigram 수를 로짓처럼 반환하는 가짜 리랭커"""

    def __init__(self, *args, **kwargs):
        pass

    def predict(self, pairs, **kwargs):
        out = []
        for q, d in pairs:
            qb = {q[i:i + 2] for i in range(len(q) - 1)}
            db = {d[i:i + 2] for i in range(len(d) - 1)}
            out.append(float(len(qb & db)) - 2.0)
        return out


def _cos_sim(a, b):
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1
    nb = math.sqrt(sum(y * y for y in b)) or 1
    return types.SimpleNamespace(item=lambda: dot / (na * nb))


if "torch" not in sys.modules:
    _stub("torch", cuda=types.SimpleNamespace(is_available=lambda: False))
if "sentence_transformers" not in sys.modules:
    _stub(
        "sentence_transformers",
        SentenceTransformer=lambda *a, **k: None,
        CrossEncoder=_FakeCrossEncoder,
        util=types.SimpleNamespace(cos_sim=_cos_sim),
    )
if "supabase" not in sys.modules:
    _stub("supabase", create_client=lambda *a, **k: None, Client=object, ClientOptions=lambda **k: None)
if "gotrue" not in sys.modules:
    _stub("gotrue")
    _stub("gotrue.errors", AuthApiError=type("AuthApiError", (Exception,), {"message": ""}))
    _stub("gotrue.types", User=object)
if "google.generativeai" not in sys.modules:
    google = sys.modules.get("google") or _stub("google")
    genai = _stub("google.generativeai", configure=lambda **k: None, GenerativeModel=lambda *a, **k: None)
    google.generativeai = genai


@pytest.fixture
def make_client():
    """FakeSupabase 를 모든 모듈의 supabase 로 주입하고, 로그인 사용자를 지정한 TestClient 를 만든다."""
    from fastapi.testclient import TestClient

    import main
    from app.api import auth, availability, bookings, chat, location, matching, mentors, profile
    from app.services import feedback_service

    def _make(fake, user_id):
        for mod in (bookings, matching, availability, chat, location, mentors, profile, feedback_service):
            mod.supabase = fake
        main.app.dependency_overrides[auth.get_current_user_id] = lambda: user_id
        return TestClient(main.app)

    yield _make

    import main as _main
    _main.app.dependency_overrides.clear()
