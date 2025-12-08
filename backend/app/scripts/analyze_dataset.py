"""
Analyze a CSV dataset to determine if it can be used for model training.
"""

import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
    import pandas as pd


def analyze_dataset(csv_path: str):
    """Analyze the dataset and provide recommendations."""
    print(f"Analyzing dataset: {csv_path}\n")
    print("=" * 60)
    
    # Read the dataset
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    # Basic information
    print(f"📊 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"📋 Columns: {', '.join(df.columns.tolist())}\n")
    
    # Check for required columns
    has_category = 'Category' in df.columns or 'category' in df.columns
    has_resume = 'Resume' in df.columns or 'resume' in df.columns
    has_job_description = 'Job Description' in df.columns or 'job_description' in df.columns or 'JD' in df.columns
    
    print("🔍 Column Analysis:")
    print(f"  ✓ Has Category column: {has_category}")
    print(f"  ✓ Has Resume column: {has_resume}")
    print(f"  ✓ Has Job Description column: {has_job_description}\n")
    
    if has_category:
        category_col = 'Category' if 'Category' in df.columns else 'category'
        print(f"📂 Categories Found: {df[category_col].nunique()} unique categories")
        print("\nTop 10 Categories:")
        print(df[category_col].value_counts().head(10))
        print()
    
    if has_resume:
        resume_col = 'Resume' if 'Resume' in df.columns else 'resume'
        resume_lengths = df[resume_col].astype(str).str.len()
        print(f"📝 Resume Statistics:")
        print(f"  - Average length: {resume_lengths.mean():.0f} characters")
        print(f"  - Min length: {resume_lengths.min():.0f} characters")
        print(f"  - Max length: {resume_lengths.max():.0f} characters")
        print(f"  - Empty resumes: {df[resume_col].isna().sum()}\n")
    
    # Training suitability assessment
    print("=" * 60)
    print("🎯 Training Suitability Assessment:\n")
    
    suitability_score = 0
    recommendations = []
    
    # Check 1: Dataset size
    if df.shape[0] >= 100:
        print("✅ Dataset size: Good (≥100 samples)")
        suitability_score += 2
    elif df.shape[0] >= 50:
        print("⚠️  Dataset size: Acceptable (50-99 samples)")
        suitability_score += 1
        recommendations.append("More samples would improve training quality")
    else:
        print("❌ Dataset size: Too small (<50 samples)")
        recommendations.append("Need at least 50 samples for meaningful training")
    
    # Check 2: Has resume data
    if has_resume:
        print("✅ Has resume data: Yes")
        suitability_score += 2
    else:
        print("❌ Has resume data: No")
        recommendations.append("Dataset needs a 'Resume' column")
    
    # Check 3: Has job descriptions or categories
    if has_job_description:
        print("✅ Has job descriptions: Yes (Perfect for similarity training)")
        suitability_score += 3
    elif has_category:
        print("⚠️  Has categories: Yes (Can be used for classification, not similarity)")
        suitability_score += 1
        recommendations.append("For similarity training, you need job descriptions, not just categories")
    else:
        print("❌ Has job descriptions/categories: No")
        recommendations.append("Need job descriptions for similarity model training")
    
    # Check 4: Data quality
    if has_resume:
        resume_col = 'Resume' if 'Resume' in df.columns else 'resume'
        empty_ratio = df[resume_col].isna().sum() / len(df)
        if empty_ratio < 0.1:
            print("✅ Data quality: Good (<10% missing)")
            suitability_score += 1
        else:
            print(f"⚠️  Data quality: {empty_ratio*100:.1f}% missing data")
            recommendations.append("Clean missing data before training")
    
    print(f"\n📊 Suitability Score: {suitability_score}/8")
    
    # Final recommendation
    print("\n" + "=" * 60)
    print("💡 Recommendations:\n")
    
    if suitability_score >= 6:
        print("✅ YES! This dataset CAN be used for training!")
        print("\nRecommended training approaches:")
        if has_job_description:
            print("  1. ✅ Fine-tune similarity model (resume-job description matching)")
            print("  2. ✅ Train classification model (resume → category)")
        elif has_category:
            print("  1. ✅ Train classification model (resume → category)")
            print("  2. ⚠️  For similarity training, you'll need to add job descriptions")
    elif suitability_score >= 4:
        print("⚠️  PARTIALLY suitable - needs some preparation")
        print("\nWhat you can do:")
        print("  1. Use categories for classification training")
        print("  2. Generate or collect job descriptions for similarity training")
    else:
        print("❌ NOT directly suitable - needs significant preparation")
        print("\nWhat you need:")
        print("  1. Add job descriptions for similarity training")
        print("  2. Ensure sufficient data quality")
    
    if recommendations:
        print("\n📝 Action Items:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
    
    # Show sample data
    print("\n" + "=" * 60)
    print("📄 Sample Data (First Row):\n")
    for col in df.columns:
        value = str(df[col].iloc[0])
        if len(value) > 200:
            value = value[:200] + "..."
        print(f"{col}: {value}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_dataset.py <path_to_csv>")
        print("\nExample:")
        print("  python analyze_dataset.py C:/Users/mohdg/Downloads/UpdatedResumeDataSet.csv/UpdatedResumeDataSet.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    if not Path(csv_path).exists():
        print(f"❌ File not found: {csv_path}")
        sys.exit(1)
    
    analyze_dataset(csv_path)

