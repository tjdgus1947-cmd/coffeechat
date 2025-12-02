# backend/app/api/mentor_network.py

from fastapi import APIRouter, HTTPException
from app.core.config import supabase
import numpy as np

router = APIRouter()

def get_mentor_profile_by_id(mentor_profile_id: int):
    response = supabase.table('mentor_profiles') \
        .select('*') \
        .eq('id', mentor_profile_id) \
        .single() \
        .execute()
    return response.data

def get_all_mentors_profiles():
    response = supabase.table('mentor_profiles') \
        .select('*') \
        .execute()
    return response.data

def calculate_mentor_similarities(center_profile: dict, all_profiles: list, top_k: int = 10):
    center_emb = center_profile.get('embedding')
    if not center_emb:
        return []
    center_emb = np.array(center_emb)

    results = []
    center_id = center_profile.get('id')

    for profile in all_profiles:
        if profile.get('id') == center_id:
            continue

        emb = profile.get('embedding')
        if not emb:
            continue

        emb = np.array(emb)

        if center_emb.shape != emb.shape:
            continue

        sim = np.dot(center_emb, emb) / (np.linalg.norm(center_emb) * np.linalg.norm(emb))
        results.append({
            "mentor_id": profile.get("id"),
            "similarity": float(sim),
            "career_info": profile.get("career_info")
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


@router.get("/network/mentor/{mentor_id}")
def get_mentor_network(mentor_id: int):
    center_profile = get_mentor_profile_by_id(mentor_id)
    if not center_profile:
        raise HTTPException(status_code=404, detail="Mentor not found")

    all_profiles = get_all_mentors_profiles()
    similar_mentors = calculate_mentor_similarities(center_profile, all_profiles)

    return {
        "center_mentor": center_profile,
        "similar_mentors": similar_mentors
    }
