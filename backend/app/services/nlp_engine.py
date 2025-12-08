from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import spacy
from sentence_transformers import SentenceTransformer, util

from ..config import Settings, get_settings


class NLPEngine:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._nlp = spacy.load(self.settings.spacy_model)
        self._embedder = SentenceTransformer(self.settings.embedding_model)

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        doc = self._nlp(text)
        skills = set()
        organizations = set()
        degrees = set()
        for ent in doc.ents:
            label = ent.label_.lower()
            if label in {"skill", "language"}:
                skills.add(ent.text)
            elif label in {"org", "company"}:
                organizations.add(ent.text)
            elif label in {"degree", "education", "qualification"}:
                degrees.add(ent.text)
        return {
            "skills": sorted(skills),
            "organizations": sorted(organizations),
            "degrees": sorted(degrees),
        }

    def similarity_score(
        self,
        resume_text: str,
        job_description: Optional[str],
    ) -> float:
        if not job_description:
            return 50.0
        resume_embedding = self._embedder.encode(resume_text, convert_to_tensor=True)
        jd_embedding = self._embedder.encode(job_description, convert_to_tensor=True)
        score = util.cos_sim(resume_embedding, jd_embedding).item()
        normalized = max(0.0, min(1.0, (score + 1) / 2))
        return round(normalized * 100, 2)
    
    def predict_category(self, resume_text: str) -> Optional[Dict[str, Any]]:
        """
        Predict the job category for a resume using trained classifier.
        
        Returns:
            Dictionary with predicted category and confidence, or None if model not available
        """
        try:
            from .category_classifier import get_category_classifier
            classifier = get_category_classifier(self.settings)
            classifier.load()
            return classifier.predict(resume_text)
        except (FileNotFoundError, ImportError):
            # Model not trained yet
            return None


@lru_cache()
def get_nlp_engine() -> NLPEngine:
    return NLPEngine()

