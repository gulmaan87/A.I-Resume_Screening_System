from __future__ import annotations

import json
import re
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from docx import Document
from pdfminer.high_level import extract_text as extract_pdf_text

SKILLS_FILE = Path(__file__).with_name("skills.json")


class ResumeParserError(Exception):
    """Raised when resume parsing fails."""


class ResumeParser:
    def __init__(self):
        if not SKILLS_FILE.exists():
            raise FileNotFoundError(f"skills.json not found at {SKILLS_FILE}")
        with SKILLS_FILE.open("r", encoding="utf-8") as fp:
            self.skills_catalog = {skill.lower() for skill in json.load(fp)}

    def parse(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        text = self._extract_text(file_bytes, filename)
        cleaned_text = self._clean_text(text)
        sentences = self._split_sentences(cleaned_text)

        skills_found, missing_skills = self._extract_skills(cleaned_text)
        experience_years = self._extract_experience_years(cleaned_text)
        education = self._extract_education(sentences)
        certifications = self._extract_certifications(cleaned_text)
        contact_info = self._extract_contact_info(cleaned_text)
        last_role = self._extract_last_role(sentences)

        parsed = {
            "raw_text": text,
            "clean_text": cleaned_text,
            "skills": sorted(skills_found),
            "missing_skills": sorted(missing_skills),
            "experience_years": experience_years,
            "education": education,
            "certifications": certifications,
            "email": contact_info.get("email"),
            "phone": contact_info.get("phone"),
            "summary": self._extract_summary(sentences),
            "last_role": last_role,
        }
        return parsed

    def _extract_text(self, file_bytes: bytes, filename: str) -> str:
        suffix = Path(filename).suffix.lower()
        if suffix == ".pdf":
            return extract_pdf_text(BytesIO(file_bytes))
        if suffix in {".docx", ".doc"}:
            document = Document(BytesIO(file_bytes))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        raise ResumeParserError(f"Unsupported file type: {suffix}")

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\uf0b7", " ")
        return text.strip()

    def _split_sentences(self, text: str) -> List[str]:
        raw_sentences = re.split(r"(?<=[.!?])\s+", text)
        return [sentence.strip() for sentence in raw_sentences if sentence.strip()]

    def _extract_skills(self, text: str) -> tuple[set[str], list[str]]:
        text_lower = text.lower()
        skills_found = {skill for skill in self.skills_catalog if skill in text_lower}
        missing_skills = sorted(self.skills_catalog - skills_found)[:25]
        return skills_found, missing_skills

    def _extract_experience_years(self, text: str) -> Optional[float]:
        matches = re.findall(r"(\d+(?:\.\d+)?)\s+(?:\+?\s*)?(?:years?|yrs?)", text, flags=re.IGNORECASE)
        if not matches:
            return None
        numbers = [float(match) for match in matches]
        return max(numbers)

    def _extract_education(self, sentences: List[str]) -> List[str]:
        keywords = ("bachelor", "master", "phd", "university", "college", "certificate", "diploma", "degree")
        education = [sentence for sentence in sentences if any(keyword in sentence.lower() for keyword in keywords)]
        return education[:5]

    def _extract_certifications(self, text: str) -> List[str]:
        cert_keywords = (
            "certified",
            "certification",
            "certificate",
            "professional",
            "license",
        )
        matches = []
        for line in text.split("."):
            if any(keyword in line.lower() for keyword in cert_keywords):
                cleaned = line.strip()
                if cleaned:
                    matches.append(cleaned)
        return matches[:10]

    def _extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone_match = re.search(
            r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}",
            text,
        )
        return {
            "email": email_match.group(0) if email_match else None,
            "phone": phone_match.group(0) if phone_match else None,
        }

    def _extract_summary(self, sentences: List[str]) -> Optional[str]:
        if not sentences:
            return None
        summary_sentences = sentences[:3]
        return " ".join(summary_sentences)

    def _extract_last_role(self, sentences: List[str]) -> Optional[str]:
        role_keywords = ("engineer", "developer", "manager", "consultant", "analyst", "specialist", "architect")
        for sentence in sentences:
            lower = sentence.lower()
            if any(keyword in lower for keyword in role_keywords):
                return sentence
        return None


@lru_cache()
def get_parser() -> ResumeParser:
    """Get a singleton ResumeParser instance."""
    return ResumeParser()

