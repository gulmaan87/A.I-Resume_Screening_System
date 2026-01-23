import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from botocore.exceptions import BotoCoreError, ClientError

from ..config import Settings
from ..database import get_database
from ..dependencies.auth import get_current_active_user
from ..models.candidate_model import CandidateResponse
from ..rate_limit import upload_rate_limit
from ..services.nlp_engine import get_nlp_engine
from ..services.parser import ResumeParserError, get_parser
from ..services.scorer import calculate_scores
from ..services.storage import get_storage_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.post("", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    request: Request,
    resume: UploadFile = File(..., description="PDF or DOCX resume file"),
    job_description: Optional[str] = Form(
        None, description="Optional job description text for similarity scoring"
    ),
    candidate_name: Optional[str] = Form(None, description="Optional candidate full name"),
    background: Optional[str] = Form(None, description="Optional additional background notes"),
    current_user: dict = Depends(get_current_active_user),  # Authentication required
    _rate_limit: None = Depends(upload_rate_limit),  # Proper rate limiting: 10/minute per IP
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    # Get settings from application state (set in lifespan) instead of request body
    settings: Settings = request.app.state.settings
    contents = await resume.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(contents) > settings.resume_max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"Resume file exceeds maximum size of {settings.resume_max_size_mb}MB.",
        )

    if resume.content_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
    }:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    storage_client = get_storage_client(settings)
    try:
        storage_result = storage_client.upload_bytes(
            data=contents,
            filename=resume.filename or "resume",
            content_type=resume.content_type,
        )
    except (BotoCoreError, ClientError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to store resume in S3: {str(exc)}. Verify storage credentials/configuration.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store resume: {str(exc)}",
        ) from exc

    parser = get_parser()
    try:
        parsed = parser.parse(contents, resume.filename or "resume")
    except ResumeParserError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(exc)}"
        ) from exc

    nlp_engine = get_nlp_engine()
    try:
        nlp_entities = nlp_engine.extract_entities(parsed["clean_text"])
        similarity_score = nlp_engine.similarity_score(parsed["clean_text"], job_description)
        
        # Predict category if model is available
        predicted_category = nlp_engine.predict_category(parsed["clean_text"])
    except Exception as exc:
        # If NLP processing fails, use defaults but don't fail the entire request
        logger.error(f"NLP processing failed: {type(exc).__name__}: {exc}", exc_info=True)
        # Use empty entities and default similarity score
        nlp_entities = {"skills": [], "organizations": [], "degrees": []}
        similarity_score = 50.0
        predicted_category = None

    scores = calculate_scores(
        found_skills=parsed["skills"],
        missing_skills=parsed["missing_skills"],
        experience_years=parsed["experience_years"],
        similarity_score=similarity_score,
    )

    document = {
        "full_name": candidate_name or parsed.get("email") or "Unknown Candidate",
        "email": parsed.get("email"),
        "phone": parsed.get("phone"),
        "skills": parsed["skills"],
        "missing_skills": scores.missing_skills,
        "experience_years": parsed["experience_years"],
        "education": parsed["education"],
        "certifications": parsed["certifications"],
        "last_role": parsed["last_role"],
        "summary": parsed.get("summary") or background,
        "job_description": job_description,
        "category": scores.category,
        "score": {
            "skill_match_score": scores.skill_match_score,
            "experience_score": scores.experience_score,
            "similarity_score": scores.similarity_score,
            "total_ai_score": scores.total_ai_score,
        },
        "job_similarity_breakdown": scores.job_similarity_breakdown,
        "resume_text": parsed["clean_text"],
        "metadata": {
            "original_filename": resume.filename or "uploaded_resume",
            "content_type": resume.content_type or storage_result["content_type"],
            "file_size": len(contents),
            "s3_key": storage_result.get("key"),
            "s3_url": storage_result.get("url"),
            "storage_type": "local" if "local_path" in storage_result else "s3",
        },
        "parsed_entities": nlp_entities,
        "predicted_category": predicted_category.get("predicted_category") if predicted_category else None,
        "category_confidence": predicted_category.get("confidence") if predicted_category else None,
        "user_id": current_user["id"],  # Link candidate to the authenticated user
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    try:
        result = await db.candidates.insert_one(document)
        document["id"] = str(result.inserted_id)
    except Exception as exc:
        logger.error(f"Failed to save candidate to database: {type(exc).__name__}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save candidate data: {str(exc)}"
        ) from exc

    try:
        return CandidateResponse(**document)
    except Exception as exc:
        logger.error(f"Failed to create response model: {type(exc).__name__}: {exc}", exc_info=True)
        logger.error(f"Document keys: {list(document.keys())}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create response: {str(exc)}"
        ) from exc

