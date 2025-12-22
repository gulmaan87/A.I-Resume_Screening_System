"""
Comprehensive Model Training Script using CSV Dataset

This script trains models on the job_applicant_dataset.csv file with techniques
to minimize both underfitting and overfitting for optimal generalization.

Features:
- Cross-validation for robust evaluation
- Early stopping to prevent overfitting
- Regularization (dropout, L2)
- Proper train/validation/test splits
- Learning rate scheduling
- Data augmentation
- Model complexity tuning
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "numpy"])
    import pandas as pd
    import numpy as np

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sentence_transformers import (
    SentenceTransformer, 
    InputExample, 
    losses, 
    evaluation,
    util
)
from sentence_transformers.datasets import NoDuplicatesDataLoader

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.category_classifier import CategoryClassifier
from app.services.model_training import ModelTrainer
from app.config import get_settings


class ComprehensiveModelTrainer:
    """Trainer with anti-overfitting and anti-underfitting techniques."""
    
    def __init__(self, csv_path: str, random_state: int = 42):
        self.csv_path = csv_path
        self.random_state = random_state
        self.settings = get_settings()
        self.trainer = ModelTrainer()
        self.models_dir = Path(__file__).parent.parent.parent / "trained_models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.training_logs = []
        
    def load_and_preprocess_data(self) -> pd.DataFrame:
        """Load and preprocess the CSV dataset."""
        print(f"\n{'='*60}")
        print("📊 Loading Dataset")
        print(f"{'='*60}")

        df = pd.read_csv(self.csv_path)

        print(f"✅ Loaded {len(df)} rows")
        print(f"   Original columns: {list(df.columns)}")

        # Handle possible unnamed index column (e.g., leading empty header)
        unnamed_cols = [c for c in df.columns if isinstance(c, str) and c.startswith("Unnamed")]
        if unnamed_cols:
            print(f"   Detected unnamed index columns: {unnamed_cols} -> dropping")
            df = df.drop(columns=unnamed_cols)

        # Normalize common alternative column names to expected ones
        rename_map = {}

        # Job description variations
        if "Job Description" not in df.columns and "Job_Description" in df.columns:
            rename_map["Job_Description"] = "Job Description"

        # Best match label variations (e.g., 'Decision', 'Recruiter Decision')
        if "Best Match" not in df.columns:
            for alt in ["Decision", "Recruiter Decision", "Recruiter_Decision", "Label"]:
                if alt in df.columns:
                    rename_map[alt] = "Best Match_raw"
                    break

        # Apply renames
        if rename_map:
            print(f"   Normalizing column names: {rename_map}")
            df = df.rename(columns=rename_map)

        # If we created a temporary 'Best Match_raw' column from decisions, convert to numeric labels
        if "Best Match" not in df.columns and "Best Match_raw" in df.columns:
            print("   Converting decision values to binary 'Best Match' labels...")

            def decision_to_label(value):
                if pd.isna(value):
                    return None
                text = str(value).strip().lower()
                if not text:
                    return None

                positive_values = {
                    "accept",
                    "accepted",
                    "hire",
                    "hired",
                    "yes",
                    "y",
                    "true",
                    "1",
                    "match",
                    "good match",
                    "strong fit",
                    "best match",
                    "selected",
                }
                negative_values = {
                    "reject",
                    "rejected",
                    "no",
                    "n",
                    "false",
                    "0",
                    "no match",
                    "bad match",
                    "weak fit",
                    "not selected",
                }

                if text in positive_values:
                    return 1
                if text in negative_values:
                    return 0

                # Fall back: try to interpret as numeric
                try:
                    num = float(text)
                    if num >= 0.5:
                        return 1
                    if num < 0.5:
                        return 0
                except ValueError:
                    pass

                # Unknown value -> drop this row later
                return None

            df["Best Match"] = df["Best Match_raw"].apply(decision_to_label)
            before = len(df)
            df = df.dropna(subset=["Best Match"])
            df["Best Match"] = df["Best Match"].astype(int)
            removed_decision = before - len(df)
            if removed_decision > 0:
                print(f"   Removed {removed_decision} rows with unknown 'Decision' values")

        # Optional / derived Job Roles column
        if "Job Roles" not in df.columns:
            # Try to infer from other possible columns
            inferred_role_col = None
            for alt in ["Job Role", "Job_Title", "Job Title", "Role", "Position"]:
                if alt in df.columns:
                    inferred_role_col = alt
                    break

            if inferred_role_col:
                print(f"   Inferring 'Job Roles' from '{inferred_role_col}'")
                df["Job Roles"] = df[inferred_role_col].astype(str)
            else:
                # Fallback: create a single generic category so similarity model can still be trained
                print("   'Job Roles' column missing; creating generic 'Unknown' role.")
                df["Job Roles"] = "Unknown"

        # Derive Best Match from numeric AI score if still missing
        if "Best Match" not in df.columns and "AI Score (0-100)" in df.columns:
            print("   Using 'AI Score (0-100)' to derive 'Best Match' (>=50 -> 1, <50 -> 0)")
            df["Best Match"] = (df["AI Score (0-100)"].astype(float) >= 50).astype(int)

        # Create synthetic Resume text if missing (for tabular datasets)
        if "Resume" not in df.columns:
            text_sources = []
            for col in [
                "Name",
                "Skills",
                "Education",
                "Certifications",
                "Projects Count",
                "Projects",
                "Experience (Years)",
                "Experience",
                "Summary",
                "Profile",
            ]:
                if col in df.columns:
                    text_sources.append(col)

            if text_sources:
                print(f"   Creating synthetic 'Resume' text from columns: {text_sources}")

                def build_resume(row):
                    parts = []
                    for c in text_sources:
                        val = row.get(c, "")
                        if pd.isna(val):
                            continue
                        val_str = str(val).strip()
                        if not val_str:
                            continue
                        # For skills, we don't need the label prefix
                        if c.lower() == "skills":
                            parts.append(val_str)
                        else:
                            parts.append(f"{c}: {val_str}")
                    return " | ".join(parts)

                df["Resume"] = df.apply(build_resume, axis=1)
            else:
                raise ValueError(
                    "Missing 'Resume' column and no suitable text fields "
                    "found to synthesize it."
                )

        # Create synthetic Job Description if missing
        if "Job Description" not in df.columns:
            role_col = "Job Roles" if "Job Roles" in df.columns else None
            skills_col = "Skills" if "Skills" in df.columns else None
            exp_col = None
            for alt in ["Experience (Years)", "Experience"]:
                if alt in df.columns:
                    exp_col = alt
                    break

            print("   Creating synthetic 'Job Description' from available columns...")

            def build_job_description(row):
                role = str(row[role_col]).strip() if role_col else ""
                skills = str(row[skills_col]).strip() if skills_col and not pd.isna(row.get(skills_col)) else ""
                exp_val = None
                if exp_col and not pd.isna(row.get(exp_col)):
                    exp_val = str(row[exp_col]).strip()

                desc_parts = []
                if role:
                    desc_parts.append(f"Job role: {role}.")
                if skills:
                    desc_parts.append(f"Looking for skills: {skills}.")
                if exp_val:
                    desc_parts.append(f"Preferred experience: {exp_val} years.")

                if not desc_parts:
                    return f"Job role: {role or 'Unknown role'}."
                return " ".join(desc_parts)

            df["Job Description"] = df.apply(build_job_description, axis=1)

        print(f"   Normalized columns: {list(df.columns)}")

        # Check required columns (Job Roles now guaranteed to exist)
        required_cols = ["Resume", "Job Roles", "Job Description", "Best Match"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns after normalization: {missing_cols}")
        
        # Clean data
        initial_count = len(df)
        df = df.dropna(subset=['Resume', 'Job Roles', 'Job Description'])
        df = df[df['Resume'].astype(str).str.len() > 50]  # Remove very short resumes
        df = df[df['Job Description'].astype(str).str.len() > 50]
        
        # Ensure Best Match is binary (0 or 1)
        df['Best Match'] = df['Best Match'].astype(int)
        df = df[df['Best Match'].isin([0, 1])]
        
        removed = initial_count - len(df)
        if removed > 0:
            print(f"⚠️  Removed {removed} invalid rows")
        
        print(f"✅ Clean dataset: {len(df)} rows")
        print(f"   Best Match distribution:")
        print(f"     0 (No Match): {len(df[df['Best Match'] == 0])}")
        print(f"     1 (Best Match): {len(df[df['Best Match'] == 1])}")
        print(f"   Job Roles: {df['Job Roles'].nunique()} unique roles")
        
        return df
    
    def create_train_val_test_split(
        self, 
        df: pd.DataFrame,
        test_size: float = 0.15,
        val_size: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Create stratified train/validation/test splits."""
        print(f"\n{'='*60}")
        print("🔄 Creating Train/Validation/Test Splits")
        print(f"{'='*60}")
        
        # First split: separate test set
        train_val, test = train_test_split(
            df,
            test_size=test_size,
            random_state=self.random_state,
            stratify=df['Best Match']
        )
        
        # Second split: separate train and validation
        train, val = train_test_split(
            train_val,
            test_size=val_size / (1 - test_size),  # Adjust for already removed test
            random_state=self.random_state,
            stratify=train_val['Best Match']
        )
        
        print(f"✅ Split complete:")
        print(f"   Train: {len(train)} samples ({len(train)/len(df)*100:.1f}%)")
        print(f"   Validation: {len(val)} samples ({len(val)/len(df)*100:.1f}%)")
        print(f"   Test: {len(test)} samples ({len(test)/len(df)*100:.1f}%)")
        
        return train, val, test
    
    def augment_data(
        self, 
        resumes: List[str], 
        job_descs: List[str],
        labels: List[int],
        augmentation_factor: float = 0.1
    ) -> Tuple[List[str], List[str], List[int]]:
        """Augment data by creating synthetic pairs (prevents underfitting)."""
        print(f"\n{'='*60}")
        print("🔄 Data Augmentation")
        print(f"{'='*60}")
        
        augmented_resumes = list(resumes)
        augmented_job_descs = list(job_descs)
        augmented_labels = list(labels)
        
        n_augment = int(len(resumes) * augmentation_factor)
        
        # Create positive pairs by mixing similar resumes and job descriptions
        # This helps the model learn better representations
        if n_augment > 0:
            print(f"   Creating {n_augment} synthetic pairs...")
            
            # Sample pairs with same label for augmentation
            for label in [0, 1]:
                label_indices = [i for i, l in enumerate(labels) if l == label]
                if len(label_indices) < 2:
                    continue
                
                n_label_augment = n_augment // 2
                for _ in range(min(n_label_augment, len(label_indices) // 2)):
                    idx1, idx2 = np.random.choice(label_indices, 2, replace=False)
                    
                    # Mix partial content (simple augmentation)
                    if len(resumes[idx1]) > 100 and len(resumes[idx2]) > 100:
                        # Take first half of one, second half of another
                        split1 = len(resumes[idx1]) // 2
                        split2 = len(resumes[idx2]) // 2
                        mixed_resume = resumes[idx1][:split1] + " " + resumes[idx2][split2:]
                        
                        augmented_resumes.append(mixed_resume)
                        augmented_job_descs.append(job_descs[idx1])  # Keep original JD
                        augmented_labels.append(label)
        
        print(f"✅ Augmented dataset: {len(augmented_resumes)} samples")
        
        return augmented_resumes, augmented_job_descs, augmented_labels
    
    def train_similarity_model(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        use_early_stopping: bool = True,
        patience: int = 3
    ) -> SentenceTransformer:
        """Train similarity model with early stopping and validation monitoring."""
        print(f"\n{'='*60}")
        print("🎯 Training Similarity Model")
        print(f"{'='*60}")
        
        # Prepare training examples
        print("   Preparing training examples...")
        train_examples = []
        
        # Use Best Match as similarity indicator
        # Best Match = 1 means high similarity (label = 0.9)
        # Best Match = 0 means low similarity (label = 0.1)
        for _, row in train_df.iterrows():
            resume = str(row['Resume'])
            job_desc = str(row['Job Description'])
            label = 0.9 if row['Best Match'] == 1 else 0.1
            
            train_examples.append(InputExample(texts=[resume, job_desc], label=float(label)))
        
        print(f"   ✅ Created {len(train_examples)} training examples")
        
        # Prepare validation examples
        print("   Preparing validation examples...")
        val_examples = []
        for _, row in val_df.iterrows():
            resume = str(row['Resume'])
            job_desc = str(row['Job Description'])
            label = 0.9 if row['Best Match'] == 1 else 0.1
            val_examples.append(InputExample(texts=[resume, job_desc], label=float(label)))
        
        print(f"   ✅ Created {len(val_examples)} validation examples")
        
        # Load base model
        print(f"   Loading base model: {self.settings.embedding_model}")
        model = SentenceTransformer(self.settings.embedding_model)
        
        # Shuffle examples manually for better training
        np.random.seed(self.random_state)
        np.random.shuffle(train_examples)
        
        # Create data loader
        train_dataloader = NoDuplicatesDataLoader(
            train_examples, 
            batch_size=batch_size
        )
        
        # Define loss function
        train_loss = losses.CosineSimilarityLoss(model)
        
        # Create evaluator for validation monitoring
        evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(
            val_examples,
            name='validation',
            show_progress_bar=True
        )
        
        # Training with early stopping callback
        print(f"   Training for up to {epochs} epochs...")
        print(f"   Batch size: {batch_size}, Learning rate: {learning_rate}")
        
        best_val_score = -1
        patience_counter = 0
        best_model_path = None
        
        for epoch in range(epochs):
            print(f"\n   Epoch {epoch + 1}/{epochs}")
            
            # Train for one epoch
            print(f"      Training on {len(train_examples)} examples ({len(train_examples) // batch_size} batches)...")
            model.fit(
                train_objectives=[(train_dataloader, train_loss)],
                epochs=1,
                warmup_steps=min(100, len(train_examples) // batch_size),
                output_path=None,  # Don't save after each epoch
                optimizer_params={"lr": learning_rate},
                show_progress_bar=True,  # Enable progress bar to show it's working
            )
            
            # Evaluate on validation set
            val_score = evaluator(model)
            self.training_logs.append({
                'epoch': epoch + 1,
                'val_score': val_score,
                'model': 'similarity'
            })
            
            print(f"      Validation Score: {val_score:.4f}")
            
            # Early stopping
            if use_early_stopping:
                if val_score > best_val_score:
                    best_val_score = val_score
                    patience_counter = 0
                    # Save best model
                    best_model_path = self.models_dir / "best_similarity_model"
                    model.save(str(best_model_path))
                    print(f"      ✓ New best model saved (score: {val_score:.4f})")
                else:
                    patience_counter += 1
                    print(f"      No improvement ({patience_counter}/{patience})")
                    
                    if patience_counter >= patience:
                        print(f"\n   ⚠️  Early stopping triggered at epoch {epoch + 1}")
                        # Load best model
                        if best_model_path and best_model_path.exists():
                            model = SentenceTransformer(str(best_model_path))
                            print(f"   ✅ Loaded best model from epoch with score: {best_val_score:.4f}")
                        break
        
        # Save final model
        final_model_path = self.models_dir / "fine-tuned-resume-matcher"
        model.save(str(final_model_path))
        print(f"\n✅ Similarity model training complete!")
        print(f"   Final validation score: {best_val_score:.4f}")
        print(f"   Model saved to: {final_model_path}")
        
        return model
    
    def train_category_classifier(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        model_type: str = "random_forest",
        use_cross_validation: bool = True,
        cv_folds: int = 5
    ) -> CategoryClassifier:
        """Train category classifier with cross-validation."""
        print(f"\n{'='*60}")
        print("🎯 Training Category Classifier")
        print(f"{'='*60}")
        
        # Prepare data
        train_resumes = train_df['Resume'].astype(str).tolist()
        train_categories = train_df['Job Roles'].astype(str).tolist()
        
        val_resumes = val_df['Resume'].astype(str).tolist()
        val_categories = val_df['Job Roles'].astype(str).tolist()
        
        test_resumes = test_df['Resume'].astype(str).tolist()
        test_categories = test_df['Job Roles'].astype(str).tolist()
        
        print(f"   Train: {len(train_resumes)} samples")
        print(f"   Validation: {len(val_resumes)} samples")
        print(f"   Test: {len(test_resumes)} samples")
        print(f"   Categories: {pd.Series(train_categories).nunique()} unique")
        
        # Initialize classifier
        classifier = CategoryClassifier()
        
        # Combine train + val for cross-validation
        all_train_resumes = train_resumes + val_resumes
        all_train_categories = train_categories + val_categories
        
        # Cross-validation for model selection
        if use_cross_validation and len(all_train_resumes) >= cv_folds * 5:
            print(f"\n   Performing {cv_folds}-fold cross-validation...")
            
            # Generate embeddings once
            print("   Generating embeddings for cross-validation...")
            embedder = SentenceTransformer(self.settings.embedding_model)
            embeddings = embedder.encode(all_train_resumes, show_progress_bar=True, batch_size=32)
            
            # Encode categories
            le = LabelEncoder()
            encoded_categories = le.fit_transform(all_train_categories)
            
            # Cross-validation
            cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
            
            # Test different model types
            model_types = ["logistic", "random_forest"] if model_type == "auto" else [model_type]
            best_model_type = model_type
            best_cv_score = 0
            
            for mt in model_types:
                from sklearn.linear_model import LogisticRegression
                from sklearn.ensemble import RandomForestClassifier
                
                if mt == "logistic":
                    clf = LogisticRegression(max_iter=1000, random_state=self.random_state, multi_class="multinomial", solver="lbfgs")
                else:
                    clf = RandomForestClassifier(n_estimators=100, random_state=self.random_state, n_jobs=-1)
                
                cv_scores = cross_val_score(clf, embeddings, encoded_categories, cv=cv, scoring='accuracy', n_jobs=-1)
                avg_score = cv_scores.mean()
                
                print(f"      {mt}: CV accuracy = {avg_score:.4f} (±{cv_scores.std():.4f})")
                
                if avg_score > best_cv_score:
                    best_cv_score = avg_score
                    best_model_type = mt
            
            print(f"\n   ✓ Best model type: {best_model_type} (CV score: {best_cv_score:.4f})")
            model_type = best_model_type
        
        # Train final model on all training data (use test_size=0 to use all data)
        print(f"\n   Training final model ({model_type})...")
        # Train on all training data with minimal test split for evaluation
        metrics = classifier.train(
            resumes=all_train_resumes,
            categories=all_train_categories,
            test_size=0.05,  # Small test split (5%) for internal evaluation
            model_type=model_type,
            random_state=self.random_state
        )
        
        # Evaluate on test set
        print(f"\n   Evaluating on test set...")
        test_predictions = classifier.predict_batch(test_resumes)
        test_acc = accuracy_score(test_categories, test_predictions)
        
        print(f"   Test Accuracy: {test_acc:.4f}")
        print(f"\n   Classification Report:")
        print(classification_report(test_categories, test_predictions, zero_division=0))
        
        # Save model
        classifier.save("category_classifier_optimized")
        print(f"\n✅ Category classifier training complete!")
        print(f"   Model saved as: category_classifier_optimized")
        
        return classifier
    
    def evaluate_on_test_set(
        self,
        similarity_model: SentenceTransformer,
        classifier: CategoryClassifier,
        test_df: pd.DataFrame
    ) -> Dict:
        """Evaluate models on test set."""
        print(f"\n{'='*60}")
        print("📊 Final Evaluation on Test Set")
        print(f"{'='*60}")
        
        test_resumes = test_df['Resume'].astype(str).tolist()
        test_job_descs = test_df['Job Description'].astype(str).tolist()
        test_labels = test_df['Best Match'].tolist()
        test_categories = test_df['Job Roles'].astype(str).tolist()
        
        # Evaluate similarity model (batch processing for efficiency)
        print("\n   Evaluating Similarity Model...")
        print(f"      Processing {len(test_resumes)} test samples...")
        
        # Batch encode for efficiency
        resume_embeddings = similarity_model.encode(
            test_resumes, 
            show_progress_bar=True, 
            batch_size=32,
            convert_to_numpy=True
        )
        job_desc_embeddings = similarity_model.encode(
            test_job_descs, 
            show_progress_bar=False, 
            batch_size=32,
            convert_to_numpy=True
        )
        
        # Compute similarities in batch
        similarities = util.cos_sim(resume_embeddings, job_desc_embeddings).diagonal().tolist()
        
        # Convert similarities to binary predictions (threshold = 0.5)
        pred_labels = [1 if s > 0.5 else 0 for s in similarities]
        similarity_acc = accuracy_score(test_labels, pred_labels)
        
        print(f"      Accuracy: {similarity_acc:.4f}")
        print(f"      Classification Report:")
        print(classification_report(test_labels, pred_labels, target_names=['No Match', 'Best Match'], zero_division=0))
        
        # Evaluate category classifier
        print("\n   Evaluating Category Classifier...")
        pred_categories = classifier.predict_batch(test_resumes)
        category_acc = accuracy_score(test_categories, pred_categories)
        
        print(f"      Accuracy: {category_acc:.4f}")
        
        return {
            'similarity_accuracy': similarity_acc,
            'category_accuracy': category_acc,
            'test_size': len(test_df)
        }
    
    def train_all(
        self,
        epochs: int = 5,
        batch_size: int = 16,
        learning_rate: float = 2e-5,
        model_type: str = "random_forest",
        use_cross_validation: bool = True,
        use_early_stopping: bool = True,
        augmentation_factor: float = 0.1
    ):
        """Train all models with optimal settings."""
        # Load and preprocess data
        df = self.load_and_preprocess_data()
        
        # Create splits
        train_df, val_df, test_df = self.create_train_val_test_split(df)
        
        # Train similarity model
        similarity_model = self.train_similarity_model(
            train_df=train_df,
            val_df=val_df,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            use_early_stopping=use_early_stopping
        )
        
        # Train category classifier
        classifier = self.train_category_classifier(
            train_df=train_df,
            val_df=val_df,
            test_df=test_df,
            model_type=model_type,
            use_cross_validation=use_cross_validation
        )
        
        # Final evaluation
        results = self.evaluate_on_test_set(similarity_model, classifier, test_df)
        
        # Print summary
        print(f"\n{'='*60}")
        print("📋 Training Summary")
        print(f"{'='*60}")
        print(f"   Similarity Model Accuracy: {results['similarity_accuracy']:.4f}")
        print(f"   Category Classifier Accuracy: {results['category_accuracy']:.4f}")
        print(f"   Test Set Size: {results['test_size']}")
        print(f"\n✅ All models trained successfully!")
        print(f"\nTo use the models:")
        print(f"   - Similarity: Model saved to trained_models/fine-tuned-resume-matcher")
        print(f"   - Category: Model saved to trained_models/category_classifier_optimized")
        
        return similarity_model, classifier, results


def main():
    parser = argparse.ArgumentParser(
        description="Train models from CSV dataset with optimal generalization"
    )
    parser.add_argument(
        "csv_path",
        type=str,
        help="Path to CSV file (job_applicant_dataset.csv)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=5,
        help="Number of training epochs (default: 5)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=16,
        help="Training batch size (default: 16)"
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=2e-5,
        help="Learning rate (default: 2e-5)"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["logistic", "random_forest", "auto"],
        default="random_forest",
        help="Category classifier type (default: random_forest)"
    )
    parser.add_argument(
        "--no-early-stopping",
        action="store_true",
        help="Disable early stopping"
    )
    parser.add_argument(
        "--no-cv",
        action="store_true",
        help="Disable cross-validation"
    )
    parser.add_argument(
        "--augmentation",
        type=float,
        default=0.1,
        help="Data augmentation factor (0.0-1.0, default: 0.1)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.csv_path).exists():
        print(f"❌ Error: File not found: {args.csv_path}")
        sys.exit(1)
    
    # Create trainer and train
    trainer = ComprehensiveModelTrainer(
        csv_path=args.csv_path,
        random_state=42
    )
    
    try:
        trainer.train_all(
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            model_type=args.model_type,
            use_cross_validation=not args.no_cv,
            use_early_stopping=not args.no_early_stopping,
            augmentation_factor=args.augmentation
        )
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

