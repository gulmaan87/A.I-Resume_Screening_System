from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from ..database import get_database
from ..dependencies.auth import get_current_active_user
from ..models.candidate_model import CandidateResponse
from ..services.nlp_engine import get_nlp_engine
from ..services.scorer import calculate_scores

router = APIRouter(prefix="/screening", tags=["Screening"])


class ScreeningRequest(BaseModel):
    resume_text: str = Field(..., description="Clean resume text")
    job_description: Optional[str] = Field(
        None, description="Job description text for similarity comparison"
    )
    skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    experience_years: Optional[float] = Field(None, description="Years of experience parsed")


@router.get("/candidates/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: str,
    current_user: dict = Depends(get_current_active_user),  # Authentication required
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    if not ObjectId.is_valid(candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found.")
    # Filter by candidate ID AND user ID to ensure users can only access their own candidates
    document = await db.candidates.find_one({
        "_id": ObjectId(candidate_id),
        "user_id": current_user["id"]
    })
    if not document:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    document["id"] = str(document["_id"])
    document.pop("_id", None)
    return CandidateResponse(**document)


@router.post("/score", status_code=status.HTTP_200_OK)
async def manual_score(payload: ScreeningRequest):
    nlp_engine = get_nlp_engine()
    similarity = nlp_engine.similarity_score(payload.resume_text, payload.job_description)
    results = calculate_scores(
        found_skills=payload.skills,
        missing_skills=payload.missing_skills,
        experience_years=payload.experience_years,
        similarity_score=similarity,
    )

    return {
        "skill_match_score": results.skill_match_score,
        "experience_score": results.experience_score,
        "similarity_score": results.similarity_score,
        "total_ai_score": results.total_ai_score,
        "category": results.category,
        "missing_skills": results.missing_skills,
        "job_similarity_breakdown": results.job_similarity_breakdown,
    }

