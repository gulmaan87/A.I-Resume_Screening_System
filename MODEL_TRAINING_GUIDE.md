# Model Training Guide for Resume Screening System

This guide explains how to train and improve your models for better accuracy in resume screening.

## Overview

Your system uses three main components that can be improved:

1. **Sentence Transformer Model** (`all-MiniLM-L6-v2`) - For semantic similarity matching
2. **spaCy NER Model** (`en_core_web_sm`) - For entity extraction (skills, organizations)
3. **Scoring Algorithm** - Combines similarity (60%), skill match (30%), experience (10%)

## Quick Start: Improve Accuracy Without Training

### 1. Update Skills Database

Add more skills to improve skill matching:

```python
from app.services.model_training import get_model_trainer

trainer = get_model_trainer()
new_skills = [
    "kubernetes", "helm", "ansible", "jenkins", 
    "github actions", "redis", "elasticsearch"
]
trainer.update_skills_database(new_skills)
```

Or edit `backend/app/services/skills.json` directly.

### 2. Adjust Scoring Weights

If you find similarity is more/less important:

```python
trainer = get_model_trainer()
trainer.adjust_scoring_weights(
    similarity_weight=0.7,  # Increase if job description matching is more important
    skill_match_weight=0.2,  # Decrease accordingly
    experience_weight=0.1
)
```

### 3. Use Better Pre-trained Models

Update `env.example` or `.env`:

```bash
# Better embedding model (larger, more accurate)
EMBEDDING_MODEL_NAME=sentence-transformers/all-mpnet-base-v2

# Better spaCy model (larger, more accurate)
SPACY_MODEL=en_core_web_md  # or en_core_web_lg
```

**Note:** You'll need to download the model first:
```bash
python -m spacy download en_core_web_md
```

## Fine-tuning the Similarity Model

### Step 1: Collect Training Data

The system automatically collects data from your database. You need at least 10-20 resumes with job descriptions.

**Option A: Use existing data**
```bash
cd backend
python -m app.scripts.train_models --similarity --epochs 5
```

**Option B: Prepare custom training data**

Create `training_data/similarity_training.json`:
```json
[
  {
    "resume_text": "Experienced Python developer with 5 years...",
    "job_description": "Looking for senior Python developer...",
    "similarity_score": 0.85
  }
]
```

### Step 2: Train the Model

```python
from app.services.model_training import ModelTrainer
from sentence_transformers import InputExample

trainer = ModelTrainer()

# Prepare examples
examples = [
    InputExample(texts=[resume, jd], label=score)
    for resume, jd, score in your_training_data
]

# Fine-tune
model = trainer.fine_tune_similarity_model(
    examples,
    output_model_name="my-resume-matcher",
    epochs=5,
    batch_size=16
)
```

### Step 3: Use the Fine-tuned Model

Update your config to use the new model:
```python
# In config.py or .env
EMBEDDING_MODEL_NAME=./trained_models/my-resume-matcher
```

## Training Custom NER Model for Better Skill Extraction

### Step 1: Prepare Training Data

Create `training_data/ner_training.json`:
```json
[
  {
    "text": "Experienced in Python, React, and AWS",
    "entities": [
      [15, 21, "SKILL"],
      [23, 28, "SKILL"],
      [33, 36, "SKILL"]
    ]
  }
]
```

### Step 2: Train the Model

```python
from app.services.model_training import ModelTrainer
from spacy.training import Example

trainer = ModelTrainer()

# Load and prepare examples
examples = trainer.prepare_ner_training_data(texts, annotations)

# Train
model = trainer.train_custom_ner_model(
    examples,
    output_model_name="custom-resume-ner",
    epochs=20
)
```

### Step 3: Use the Custom Model

```python
# In config.py or .env
SPACY_MODEL=./trained_models/custom-resume-ner
```

## Collecting Feedback for Continuous Improvement

### Via API

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "123...",
    "predicted_score": 75.5,
    "predicted_category": "Medium Fit",
    "actual_score": 85.0,
    "actual_category": "Strong Fit",
    "hr_feedback": "Great candidate, should have scored higher"
  }'
```

### Via Python

```python
from app.services.model_training import get_model_trainer

trainer = get_model_trainer()
trainer.collect_feedback(
    candidate_id="123...",
    predicted_score=75.5,
    predicted_category="Medium Fit",
    actual_score=85.0,
    actual_category="Strong Fit",
    hr_feedback="Great candidate"
)
```

Feedback is saved to `training_data/feedback.jsonl` for future training.

## Evaluation and Testing

### Evaluate Model Performance

```python
from app.services.model_training import ModelTrainer
from sentence_transformers import InputExample

trainer = ModelTrainer()

# Prepare test examples
test_examples = [
    InputExample(texts=[resume, jd], label=expected_score)
    for resume, jd, expected_score in test_data
]

# Evaluate
metrics = trainer.evaluate_model_performance(test_examples)
print(f"Similarity Score: {metrics['similarity_score']}")
```

## Best Practices

### 1. Start with Better Pre-trained Models
- Use `all-mpnet-base-v2` instead of `all-MiniLM-L6-v2` for better accuracy
- Use `en_core_web_lg` instead of `en_core_web_sm` for better NER

### 2. Collect Quality Training Data
- At least 50-100 examples for fine-tuning
- Include diverse job descriptions and resumes
- Get HR feedback on predictions

### 3. Regular Retraining
- Retrain monthly with new feedback data
- Monitor model performance over time
- Adjust weights based on business needs

### 4. Domain-Specific Training
- Fine-tune on your industry-specific resumes
- Add domain-specific skills to the database
- Train NER on your company's job descriptions

## Advanced: Custom Scoring Algorithm

You can also create a custom scoring algorithm:

```python
# In scorer.py, modify calculate_scores function
def calculate_scores(...):
    # Your custom logic here
    # Maybe use ML model for scoring
    # Or add more factors (education, certifications, etc.)
    pass
```

## Troubleshooting

### "Not enough training data"
- Upload more resumes with job descriptions
- Use the seed script to generate demo data
- Collect feedback from HR team

### "Model not improving"
- Check training data quality
- Increase training epochs
- Try different learning rates
- Use larger pre-trained models

### "Skills not being detected"
- Update skills.json with missing skills
- Train custom NER model
- Use better spaCy model (md or lg)

## Next Steps

1. **Immediate**: Update skills database and adjust weights
2. **Short-term**: Collect feedback and fine-tune similarity model
3. **Long-term**: Train custom NER model and build domain-specific models

For questions or issues, check the training logs in `training_data/` directory.

