"""
Model Training and Fine-tuning Module for Resume Screening System

This module provides functionality to:
1. Fine-tune sentence transformer models for better job-resume matching
2. Train custom spaCy NER models for better skill extraction
3. Collect feedback data for continuous improvement
4. Evaluate and compare model performance
"""

import json
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
from sentence_transformers import InputExample, SentenceTransformer, losses, evaluation
from sentence_transformers.datasets import NoDuplicatesDataLoader
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding


class ModelTrainer:
    """Handles training and fine-tuning of models for better accuracy."""

    def __init__(self, settings=None):
        from ..config import get_settings
        self.settings = settings or get_settings()
        self.training_data_dir = Path(__file__).parent.parent.parent / "training_data"
        self.training_data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir = Path(__file__).parent.parent.parent / "trained_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    def prepare_similarity_training_data(
        self,
        resume_texts: List[str],
        job_descriptions: List[str],
        similarity_scores: List[float],
    ) -> List[InputExample]:
        """
        Prepare training data for sentence transformer fine-tuning.
        
        Args:
            resume_texts: List of resume text samples
            job_descriptions: List of corresponding job descriptions
            similarity_scores: List of similarity scores (0-1) indicating match quality
        
        Returns:
            List of InputExample objects for training
        """
        examples = []
        for resume, jd, score in zip(resume_texts, job_descriptions, similarity_scores):
            # Create positive examples (high similarity)
            if score >= 0.7:
                examples.append(InputExample(texts=[resume, jd], label=float(score)))
        return examples

    def fine_tune_similarity_model(
        self,
        training_examples: List[InputExample],
        output_model_name: str = "fine-tuned-resume-matcher",
        epochs: int = 3,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
    ) -> SentenceTransformer:
        """
        Fine-tune the sentence transformer model for better resume-job matching.
        
        Args:
            training_examples: List of InputExample objects
            output_model_name: Name for the fine-tuned model
            epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate for optimization
        
        Returns:
            Fine-tuned SentenceTransformer model
        """
        # Load base model
        base_model = SentenceTransformer(self.settings.embedding_model)
        
        # Create data loader
        train_dataloader = NoDuplicatesDataLoader(training_examples, batch_size=batch_size)
        
        # Define loss function (cosine similarity loss)
        train_loss = losses.CosineSimilarityLoss(base_model)
        
        # Fine-tune the model
        base_model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=epochs,
            warmup_steps=100,
            output_path=str(self.models_dir / output_model_name),
            optimizer_params={"lr": learning_rate},
            show_progress_bar=True,
        )
        
        return base_model

    def prepare_ner_training_data(
        self,
        texts: List[str],
        annotations: List[Dict[str, List[Tuple[int, int, str]]]],
    ) -> List[Example]:
        """
        Prepare training data for spaCy NER model.
        
        Args:
            texts: List of text samples
            annotations: List of annotation dicts with 'entities' key containing
                        list of (start, end, label) tuples
        
        Returns:
            List of spaCy Example objects
        """
        nlp = spacy.load(self.settings.spacy_model)
        examples = []
        
        for text, annot in zip(texts, annotations):
            doc = nlp.make_doc(text)
            entities = annot.get("entities", [])
            example = Example.from_dict(doc, {"entities": entities})
            examples.append(example)
        
        return examples

    def train_custom_ner_model(
        self,
        training_examples: List[Example],
        output_model_name: str = "custom-resume-ner",
        epochs: int = 10,
        dropout: float = 0.2,
    ) -> spacy.Language:
        """
        Train a custom spaCy NER model for better skill/entity extraction.
        
        Args:
            training_examples: List of spaCy Example objects
            output_model_name: Name for the trained model
            epochs: Number of training epochs
            dropout: Dropout rate during training
        
        Returns:
            Trained spaCy model
        """
        # Load base model
        nlp = spacy.load(self.settings.spacy_model)
        
        # Add NER labels if not present
        if "ner" not in nlp.pipe_names:
            ner = nlp.add_pipe("ner", last=True)
        else:
            ner = nlp.get_pipe("ner")
        
        # Add labels from training data
        for example in training_examples:
            for ent in example.reference.ents:
                ner.add_label(ent.label_)
        
        # Disable other pipeline components during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != "ner"]
        with nlp.disable_pipes(*other_pipes):
            # Initialize optimizer
            optimizer = nlp.resume_training()
            
            # Training loop
            for epoch in range(epochs):
                losses = {}
                batches = minibatch(training_examples, size=compounding(4.0, 32.0, 1.001))
                
                for batch in batches:
                    nlp.update(batch, drop=dropout, losses=losses, sgd=optimizer)
                
                print(f"Epoch {epoch + 1}/{epochs}, Loss: {losses.get('ner', 0):.4f}")
        
        # Save the model
        output_path = self.models_dir / output_model_name
        nlp.to_disk(str(output_path))
        
        return nlp

    def collect_feedback(
        self,
        candidate_id: str,
        predicted_score: float,
        predicted_category: str,
        actual_score: Optional[float] = None,
        actual_category: Optional[str] = None,
        hr_feedback: Optional[str] = None,
    ):
        """
        Collect feedback data for continuous model improvement.
        
        Args:
            candidate_id: ID of the candidate
            predicted_score: Model's predicted score
            predicted_category: Model's predicted category
            actual_score: Actual score from HR (if available)
            actual_category: Actual category from HR (if available)
            hr_feedback: Additional feedback from HR
        """
        feedback_file = self.training_data_dir / "feedback.jsonl"
        
        feedback_data = {
            "candidate_id": candidate_id,
            "predicted_score": predicted_score,
            "predicted_category": predicted_category,
            "actual_score": actual_score,
            "actual_category": actual_category,
            "hr_feedback": hr_feedback,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(feedback_data) + "\n")

    def evaluate_model_performance(
        self,
        test_examples: List[InputExample],
        model: Optional[SentenceTransformer] = None,
    ) -> Dict[str, float]:
        """
        Evaluate model performance on test data.
        
        Args:
            test_examples: List of test InputExample objects
            model: Model to evaluate (uses default if None)
        
        Returns:
            Dictionary with evaluation metrics
        """
        if model is None:
            model = SentenceTransformer(self.settings.embedding_model)
        
        # Create evaluator
        evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(
            test_examples, name="resume-job-similarity"
        )
        
        # Evaluate
        score = evaluator(model)
        
        return {
            "similarity_score": score,
            "model_name": model.get_sentence_embedding_dimension(),
        }

    def update_skills_database(self, new_skills: List[str], skill_categories: Optional[Dict[str, List[str]]] = None):
        """
        Update the skills database with new skills and categories.
        
        Args:
            new_skills: List of new skills to add
            skill_categories: Optional dict mapping categories to skill lists
        """
        skills_file = Path(__file__).parent / "skills.json"
        
        # Load existing skills
        with open(skills_file, "r", encoding="utf-8") as f:
            existing_skills = set(json.load(f))
        
        # Add new skills
        existing_skills.update(new_skills)
        
        # Save updated skills
        with open(skills_file, "w", encoding="utf-8") as f:
            json.dump(sorted(existing_skills), f, indent=2)
        
        # Save categorized skills if provided
        if skill_categories:
            categories_file = Path(__file__).parent / "skills_categories.json"
            with open(categories_file, "w", encoding="utf-8") as f:
                json.dump(skill_categories, f, indent=2)

    def adjust_scoring_weights(
        self,
        similarity_weight: float = 0.6,
        skill_match_weight: float = 0.3,
        experience_weight: float = 0.1,
    ):
        """
        Adjust the scoring weights for better accuracy.
        
        Args:
            similarity_weight: Weight for similarity score (default 0.6)
            skill_match_weight: Weight for skill match score (default 0.3)
            experience_weight: Weight for experience score (default 0.1)
        """
        weights_file = Path(__file__).parent / "scoring_weights.json"
        
        weights = {
            "similarity_weight": similarity_weight,
            "skill_match_weight": skill_match_weight,
            "experience_weight": experience_weight,
        }
        
        # Validate weights sum to 1.0
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        
        with open(weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2)


def get_model_trainer(settings=None):
    """Get a ModelTrainer instance."""
    return ModelTrainer(settings)

