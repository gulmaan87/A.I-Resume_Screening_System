"""
Train a category classification model using the CSV dataset.

Usage:
    python -m app.scripts.train_category_classifier <path_to_csv> [options]
"""

import argparse
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Installing pandas...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    import pandas as pd

from ..services.category_classifier import CategoryClassifier


def load_dataset(csv_path: str):
    """Load and preprocess the dataset."""
    print(f"Loading dataset from {csv_path}...")
    
    df = pd.read_csv(csv_path)
    
    # Check required columns
    if 'Category' not in df.columns and 'category' not in df.columns:
        raise ValueError("Dataset must have a 'Category' column")
    if 'Resume' not in df.columns and 'resume' not in df.columns:
        raise ValueError("Dataset must have a 'Resume' column")
    
    category_col = 'Category' if 'Category' in df.columns else 'category'
    resume_col = 'Resume' if 'Resume' in df.columns else 'resume'
    
    # Clean data
    df = df.dropna(subset=[category_col, resume_col])
    df = df[df[resume_col].astype(str).str.len() > 50]  # Remove very short resumes
    
    # Convert to lists
    resumes = df[resume_col].astype(str).tolist()
    categories = df[category_col].astype(str).tolist()
    
    print(f"✅ Loaded {len(resumes)} samples")
    print(f"   Categories: {df[category_col].nunique()} unique")
    print(f"   Category distribution:")
    print(df[category_col].value_counts().head(10))
    
    return resumes, categories


def main():
    parser = argparse.ArgumentParser(
        description="Train category classification model from CSV dataset"
    )
    parser.add_argument(
        "csv_path",
        type=str,
        help="Path to CSV file with Category and Resume columns"
    )
    parser.add_argument(
        "--model-type",
        type=str,
        choices=["logistic", "random_forest"],
        default="logistic",
        help="Type of classifier to train"
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Proportion of data for testing (default: 0.2)"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="category_classifier",
        help="Name for the saved model (default: category_classifier)"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=None,
        help="Maximum number of samples to use (for testing)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.csv_path).exists():
        print(f"❌ Error: File not found: {args.csv_path}")
        sys.exit(1)
    
    # Load dataset
    try:
        resumes, categories = load_dataset(args.csv_path)
    except Exception as e:
        print(f"❌ Error loading dataset: {e}")
        sys.exit(1)
    
    # Limit samples if specified
    if args.max_samples and len(resumes) > args.max_samples:
        print(f"⚠️  Limiting to {args.max_samples} samples for testing...")
        resumes = resumes[:args.max_samples]
        categories = categories[:args.max_samples]
    
    # Train model
    classifier = CategoryClassifier()
    
    try:
        metrics = classifier.train(
            resumes=resumes,
            categories=categories,
            test_size=args.test_size,
            model_type=args.model_type,
        )
        
        # Save model
        classifier.save(args.model_name)
        
        print("\n" + "="*60)
        print("📊 Training Summary:")
        print(f"   Accuracy: {metrics['accuracy']:.2%}")
        print(f"   Categories: {metrics['num_categories']}")
        print(f"   Samples: {metrics['num_samples']}")
        print("="*60)
        
        print(f"\n✅ Model training complete! Saved as '{args.model_name}'")
        print(f"\nTo use the model:")
        print(f"  from app.services.category_classifier import CategoryClassifier")
        print(f"  classifier = CategoryClassifier()")
        print(f"  classifier.load('{args.model_name}')")
        print(f"  result = classifier.predict(resume_text)")
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

