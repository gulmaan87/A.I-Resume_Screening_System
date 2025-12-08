from collections import Counter, defaultdict
from statistics import mean
from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database import get_database
from ..dependencies.auth import get_current_active_user
from ..models.candidate_model import Dashboard, DashboardAnalytics, CandidateListItem

router = APIRouter(tags=["Dashboard"])


def _serialize_candidate(document: Dict[str, Any]) -> Dict[str, Any]:
    """Safely serialize candidate document with error handling."""
    from datetime import datetime, timezone
    
    score_data = document.get("score", {})
    if not isinstance(score_data, dict):
        score_data = {}
    
    # Handle created_at - ensure it's a datetime or use current time
    created_at = document.get("created_at")
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    elif isinstance(created_at, str):
        # Try to parse if it's a string
        try:
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            created_at = datetime.now(timezone.utc)
    
    return {
        "id": str(document.get("_id", "")),
        "full_name": document.get("full_name", "Unknown"),
        "email": document.get("email"),
        "phone": document.get("phone"),
        "category": document.get("category", "Uncategorized"),
        "total_ai_score": float(score_data.get("total_ai_score", 0.0)),
        "skill_match_score": float(score_data.get("skill_match_score", 0.0)),
        "experience_years": document.get("experience_years"),
        "last_role": document.get("last_role"),
        "created_at": created_at,
    }


@router.get("", response_model=Dashboard)
async def get_dashboard(
    current_user: dict = Depends(get_current_active_user),  # Authentication required
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    cursor = db.candidates.find().sort("score.total_ai_score", -1)
    candidates = [doc async for doc in cursor]

    serialized = [CandidateListItem(**_serialize_candidate(doc)) for doc in candidates]

    if not candidates:
        analytics = DashboardAnalytics(
            average_score=0.0,
            category_counts={},
            common_missing_skills=[],
            experience_distribution={},
            top_candidates=[]
        )
        return Dashboard(candidates=[], analytics=analytics)

    total_scores = [
        doc["score"]["total_ai_score"] 
        for doc in candidates 
        if doc.get("score") and isinstance(doc.get("score"), dict) and "total_ai_score" in doc["score"]
    ]
    average_score = mean(total_scores) if total_scores else 0

    category_counts = Counter(doc.get("category", "Uncategorized") for doc in candidates)

    missing_skills = Counter()
    for doc in candidates:
        missing_skills.update(doc.get("missing_skills", []))
    common_missing_skills = [skill for skill, _ in missing_skills.most_common(10)]

    experience_distribution = defaultdict(int)
    for doc in candidates:
        years = doc.get("experience_years")
        if years is None:
            bucket = "Unknown"
        elif years < 3:
            bucket = "0-3 years"
        elif years < 7:
            bucket = "3-7 years"
        elif years < 12:
            bucket = "7-12 years"
        else:
            bucket = "12+ years"
        experience_distribution[bucket] += 1

    analytics = DashboardAnalytics(
        average_score=round(average_score, 2),
        category_counts=dict(category_counts),
        common_missing_skills=common_missing_skills,
        experience_distribution=dict(experience_distribution),
        top_candidates=serialized[:5],
    )

    return Dashboard(candidates=serialized, analytics=analytics)

