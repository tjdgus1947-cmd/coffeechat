from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict
import google.generativeai as genai
import os
import sys

router = APIRouter()

# 1. API 키 설정 (공백 제거 필수)
raw_api_key = "AIzaSyCPYuZgF7NJLvnTRvrwZi-WIIw-Mh4v21c" 
GOOGLE_API_KEY = raw_api_key.strip()

# 2. transport='rest' 옵션 추가
genai.configure(api_key=GOOGLE_API_KEY, transport='rest')

# 요청 받을 데이터 구조
class IntroGenerationRequest(BaseModel):
    original_intro: str
    situation: str # 멘토의 경우 '소속/직무' 정보로 활용
    topics: str
    survey_answers: Dict[str, str]
    role: str = "mentee" # 기본값 mentee, 멘토 요청 시 "mentor"

@router.post("/api/ai/generate-intro")
def generate_introduction(request: IntroGenerationRequest):
    """
    Gemini 모델을 사용하여 역할에 맞는 자기소개를 생성합니다.
    """
    try:
        # 사용 가능한 최신 모델 지정
        target_model = 'gemini-2.0-flash'
        print(f"🚀 [AI 생성 시작] Role: {request.role}, Model: {target_model}")
        
        model = genai.GenerativeModel(target_model)

        # 역할에 따른 프롬프트 분기
        if request.role == "mentor":
            system_persona = "당신은 최고의 커리어 멘토링 전문가이자 퍼스널 브랜딩 컨설턴트입니다."
            target_audience = "성장을 꿈꾸는 주니어 멘티들"
            tone_manner = "전문적이고 신뢰감 있으며, 동시에 친절하고 이끌어주는 어조"
            context_info = f"- 소속/경력: {request.situation}\n- 전문 분야: {request.topics}"
        else:
            system_persona = "당신은 취업 및 커리어 멘토링을 위한 자기소개서 작성 전문가입니다."
            target_audience = "현직자 멘토님"
            tone_manner = "열정적이고 배우려는 자세가 돋보이는 정중한 어조"
            context_info = f"- 현재 상황: {request.situation}\n- 관심 분야: {request.topics}"

        # 프롬프트 구성
        prompt = f"""
        {system_persona}
        아래 제공된 정보를 바탕으로, {target_audience}에게 어필할 수 있는 {tone_manner}의 자기소개서를 300~500자 내외로 작성해주세요.
        
        [사용자 정보]
        {context_info}
        - 사용자가 쓴 초안: {request.original_intro}

        [성향 설문 답변]
        1. {request.survey_answers.get('q1')}
        2. {request.survey_answers.get('q2')}
        3. {request.survey_answers.get('q3')}
        4. {request.survey_answers.get('q4')}
        5. {request.survey_answers.get('q5')}

        조건:
        1. "안녕하세요"로 시작하는 자연스러운 줄글로 작성하세요.
        2. 설문 답변을 단순히 나열하지 말고, 하나의 스토리로 자연스럽게 녹여내세요.
        3. {request.role == 'mentor' and "멘티에게 어떤 구체적인 도움을 줄 수 있는지, 멘토링 철학이 무엇인지 강조하세요." or "자신의 고민과 목표를 명확히 하여 멘토링이 필요한 이유를 어필하세요."}
        """

        # AI 생성 요청
        response = model.generate_content(prompt)
        generated_text = response.text
        
        print("✅ AI 응답 생성 완료")
        return {"generated_text": generated_text}

    except Exception as e:
        print(f"🔥 Gemini 생성 오류: {e}")
        raise HTTPException(status_code=500, detail=f"AI 오류: {str(e)}")