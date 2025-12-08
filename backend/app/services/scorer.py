from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ScoringResult:
    skill_match_score: float
    experience_score: float
    similarity_score: float
    total_ai_score: float
    category: str
    missing_skills: List[str]
    job_similarity_breakdown: List[Dict[str, float]]


def _clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, round(value, 2)))


def _calculate_skill_match(found_skills: Iterable[str], missing_skills: Iterable[str]) -> float:
    found = set(found_skills)
    missing = set(missing_skills)
    total = len(found) + len(missing)
    if total == 0:
        return 50.0
    return (len(found) / total) * 100


def _calculate_experience_score(experience_years: Optional[float]) -> float:
    if experience_years is None:
        return 40.0
    capped_years = min(experience_years, 20)
    return (capped_years / 20) * 100


def _categorize(score: float) -> str:
    if score > 80:
        return "Strong Fit"
    if score >= 60:
        return "Medium Fit"
    return "Weak Fit"


def calculate_scores(
    *,
    found_skills: Iterable[str],
    missing_skills: Iterable[str],
    experience_years: Optional[float],
    similarity_score: float,
) -> ScoringResult:
    skill_match_score = _clamp(_calculate_skill_match(found_skills, missing_skills))
    experience_score = _clamp(_calculate_experience_score(experience_years))
    similarity_score = _clamp(similarity_score)

    total_ai_score = _clamp(
        (similarity_score * 0.6) + (skill_match_score * 0.3) + (experience_score * 0.1)
    )

    breakdown = [
        {"metric": "similarity", "weight": 0.6, "score": similarity_score},
        {"metric": "skill_match", "weight": 0.3, "score": skill_match_score},
        {"metric": "experience", "weight": 0.1, "score": experience_score},
    ]

    return ScoringResult(
        skill_match_score=skill_match_score,
        experience_score=experience_score,
        similarity_score=similarity_score,
        total_ai_score=total_ai_score,
        category=_categorize(total_ai_score),
        missing_skills=sorted(set(missing_skills)),
        job_similarity_breakdown=breakdown,
    )

