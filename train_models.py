#!/usr/bin/env python3
"""
Quick training script wrapper for convenience.

This script makes it easy to train models from the CSV dataset.
Just run: python train_models.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    # Find CSV file
    csv_file = Path(__file__).parent / "job_applicant_dataset.csv"
    
    if not csv_file.exists():
        print(f"❌ Error: CSV file not found at {csv_file}")
        print("   Please ensure job_applicant_dataset.csv is in the project root.")
        sys.exit(1)
    
    # Import and run training
    from app.scripts.train_from_csv import main as train_main
    
    # Set up arguments
    sys.argv = [
        "train_from_csv.py",
        str(csv_file.absolute()),
        "--epochs", "5",
        "--batch-size", "16",
        "--learning-rate", "2e-5",
        "--model-type", "random_forest",
    ]
    
    print("="*60)
    print("🚀 Starting Model Training")
    print("="*60)
    print(f"📁 Dataset: {csv_file}")
    print(f"⚙️  Settings:")
    print(f"   - Epochs: 5")
    print(f"   - Batch Size: 16")
    print(f"   - Learning Rate: 2e-5")
    print(f"   - Model Type: random_forest")
    print("="*60)
    print()
    
    train_main()





