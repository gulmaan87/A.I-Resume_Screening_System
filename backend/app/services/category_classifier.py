"""
Category Classification Model for Resume Screening

This module provides a trained classifier that can automatically categorize
resumes into job categories (Data Science, Java Developer, etc.)
"""

import pickle
from pathlib import Path
from typing import List, Optional

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder
except ImportError as e:
    raise ImportError(
        f"Required packages not installed. Run: pip install sentence-transformers scikit-learn numpy\n"
        f"Original error: {e}"
    )

from ..config import Settings, get_settings


class CategoryClassifier:
    """Classify resumes into job categories."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.models_dir = Path(__file__).parent.parent.parent / "trained_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.embedder = SentenceTransformer(self.settings.embedding_model)
        self.label_encoder = LabelEncoder()
        self.classifier = None
        self.categories = None

    def train(
        self,
        resumes: List[str],
        categories: List[str],
        test_size: float = 0.2,
        model_type: str = "logistic",
        random_state: int = 42,
    ) -> dict:
        """
        Train a category classification model.
        
        Args:
            resumes: List of resume texts
            categories: List of corresponding categories
            test_size: Proportion of data for testing
            model_type: 'logistic' or 'random_forest'
            random_state: Random seed for reproducibility
        
        Returns:
            Dictionary with training metrics
        """
        print(f"Training category classifier on {len(resumes)} samples...")
        
        # Encode categories
        self.categories = self.label_encoder.fit_transform(categories)
        category_names = self.label_encoder.classes_
        
        print(f"Found {len(category_names)} categories: {category_names[:10]}...")
        
        # Generate embeddings for resumes
        print("Generating embeddings...")
        embeddings = self.embedder.encode(resumes, show_progress_bar=True, batch_size=32)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            embeddings,
            self.categories,
            test_size=test_size,
            random_state=random_state,
            stratify=self.categories,
        )
        
        # Train classifier
        print(f"Training {model_type} classifier...")
        if model_type == "logistic":
            self.classifier = LogisticRegression(
                max_iter=1000,
                random_state=random_state,
                multi_class="multinomial",
                solver="lbfgs",
            )
        elif model_type == "random_forest":
            self.classifier = RandomForestClassifier(
                n_estimators=100,
                random_state=random_state,
                n_jobs=-1,
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
        
        self.classifier.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.classifier.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Training complete!")
        print(f"   Test Accuracy: {accuracy:.2%}")
        print(f"   Categories: {len(category_names)}")
        
        # Classification report
        report = classification_report(
            y_test,
            y_pred,
            target_names=category_names,
            output_dict=True,
            zero_division=0,
        )
        
        return {
            "accuracy": accuracy,
            "categories": category_names.tolist(),
            "num_categories": len(category_names),
            "num_samples": len(resumes),
            "classification_report": report,
        }

    def predict(self, resume_text: str) -> dict:
        """
        Predict category for a resume.
        
        Args:
            resume_text: Resume text to classify
        
        Returns:
            Dictionary with predicted category and confidence scores
        """
        if self.classifier is None or self.label_encoder is None:
            raise ValueError("Model not trained. Call train() first or load a saved model.")
        
        # Generate embedding
        embedding = self.embedder.encode([resume_text])
        
        # Predict
        predicted_label = self.classifier.predict(embedding)[0]
        predicted_category = self.label_encoder.inverse_transform([predicted_label])[0]
        
        # Get probabilities
        probabilities = self.classifier.predict_proba(embedding)[0]
        category_probs = {
            category: float(prob)
            for category, prob in zip(self.label_encoder.classes_, probabilities)
        }
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_predictions = [
            {
                "category": self.label_encoder.classes_[idx],
                "confidence": float(probabilities[idx]),
            }
            for idx in top_indices
        ]
        
        return {
            "predicted_category": predicted_category,
            "confidence": float(probabilities[predicted_label]),
            "top_predictions": top_predictions,
            "all_probabilities": category_probs,
        }

    def predict_batch(self, resume_texts: List[str]) -> List[str]:
        """
        Predict categories for multiple resumes (batch processing).
        
        Args:
            resume_texts: List of resume texts to classify
        
        Returns:
            List of predicted categories
        """
        if self.classifier is None or self.label_encoder is None:
            raise ValueError("Model not trained. Call train() first or load a saved model.")
        
        if not resume_texts:
            return []
        
        # Generate embeddings
        embeddings = self.embedder.encode(resume_texts, show_progress_bar=False, batch_size=32)
        
        # Predict
        predicted_labels = self.classifier.predict(embeddings)
        predicted_categories = self.label_encoder.inverse_transform(predicted_labels)
        
        return predicted_categories.tolist()

    def save(self, model_name: str = "category_classifier"):
        """Save the trained model."""
        model_path = self.models_dir / model_name
        model_path.mkdir(parents=True, exist_ok=True)
        
        # Save classifier
        with open(model_path / "classifier.pkl", "wb") as f:
            pickle.dump(self.classifier, f)
        
        # Save label encoder
        with open(model_path / "label_encoder.pkl", "wb") as f:
            pickle.dump(self.label_encoder, f)
        
        print(f"✅ Model saved to {model_path}")

    def load(self, model_name: str = "category_classifier"):
        """Load a saved model."""
        model_path = self.models_dir / model_name
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        # Load classifier
        with open(model_path / "classifier.pkl", "rb") as f:
            self.classifier = pickle.load(f)
        
        # Load label encoder
        with open(model_path / "label_encoder.pkl", "rb") as f:
            self.label_encoder = pickle.load(f)
        
        print(f"✅ Model loaded from {model_path}")


def get_category_classifier(settings: Settings | None = None) -> CategoryClassifier:
    """Get a CategoryClassifier instance."""
    return CategoryClassifier(settings)

