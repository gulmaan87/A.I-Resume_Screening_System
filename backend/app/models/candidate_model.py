from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class ResumeMetadata(BaseModel):
    original_filename: str
    content_type: str
    file_size: int
    s3_key: str
    s3_url: Optional[str]


class ScoreBreakdown(BaseModel):
    skill_match_score: float = Field(..., ge=0, le=100)
    experience_score: float = Field(..., ge=0, le=100)
    similarity_score: float = Field(..., ge=0, le=100)
    total_ai_score: float = Field(..., ge=0, le=100)


class CandidateBase(BaseModel):
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    job_description: Optional[str]
    skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[float]
    education: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    last_role: Optional[str]
    summary: Optional[str]
    category: str
    score: ScoreBreakdown
    job_similarity_breakdown: List[dict] = Field(default_factory=list)


class CandidateCreate(CandidateBase):
    resume_text: str
    metadata: ResumeMetadata
    parsed_entities: dict = Field(default_factory=dict)


class CandidateInDB(CandidateCreate):
    id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CandidateListItem(BaseModel):
    id: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    category: str
    total_ai_score: float
    skill_match_score: float
    experience_years: Optional[float]
    last_role: Optional[str]
    created_at: datetime


class DashboardAnalytics(BaseModel):
    average_score: float
    category_counts: dict
    common_missing_skills: List[str]
    experience_distribution: dict
    top_candidates: List[CandidateListItem] = Field(default_factory=list)


class Dashboard(BaseModel):
    candidates: List[CandidateListItem] = Field(default_factory=list)
    analytics: DashboardAnalytics


class CandidateResponse(CandidateInDB):
    pass

