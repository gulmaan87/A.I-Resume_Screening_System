"""
API endpoint for collecting HR feedback to improve model accuracy.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from ..database import get_database
from ..dependencies.auth import get_current_active_user
from ..services.model_training import get_model_trainer

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    candidate_id: str = Field(..., description="ID of the candidate")
    predicted_score: float = Field(..., ge=0, le=100, description="Model's predicted score")
    predicted_category: str = Field(..., description="Model's predicted category")
    actual_score: Optional[float] = Field(None, ge=0, le=100, description="Actual score from HR")
    actual_category: Optional[str] = Field(None, description="Actual category from HR")
    hr_feedback: Optional[str] = Field(None, description="Additional feedback from HR")


@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_active_user),  # Authentication required
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Submit feedback to improve model accuracy.
    This feedback will be used for future model training.
    """
    # Verify candidate exists and belongs to the current user
    from bson import ObjectId
    
    if not ObjectId.is_valid(feedback.candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found.")
    
    # Filter by candidate ID AND user ID to ensure users can only provide feedback on their own candidates
    candidate = await db.candidates.find_one({
        "_id": ObjectId(feedback.candidate_id),
        "user_id": current_user["id"]
    })
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    
    # Collect feedback
    trainer = get_model_trainer()
    trainer.collect_feedback(
        candidate_id=feedback.candidate_id,
        predicted_score=feedback.predicted_score,
        predicted_category=feedback.predicted_category,
        actual_score=feedback.actual_score,
        actual_category=feedback.actual_category,
        hr_feedback=feedback.hr_feedback,
    )
    
    return {
        "message": "Feedback collected successfully",
        "candidate_id": feedback.candidate_id,
    }




