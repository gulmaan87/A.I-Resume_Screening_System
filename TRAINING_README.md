# Model Training Guide with CSV Dataset

This guide explains how to train your models using the `job_applicant_dataset.csv` file with techniques to minimize both underfitting and overfitting.

## Quick Start

Train all models with optimal settings:

```bash
cd backend
python -m app.scripts.train_from_csv ../job_applicant_dataset.csv
```

## Features

### ✅ Anti-Underfitting Techniques
- **Cross-validation**: 5-fold stratified cross-validation for robust model selection
- **Data augmentation**: Synthetic data generation to increase training set size
- **Feature engineering**: Uses sentence transformers for rich embeddings
- **Large dataset**: Leverages all 10,000+ samples from the CSV

### ✅ Anti-Overfitting Techniques
- **Early stopping**: Monitors validation loss and stops when no improvement
- **Train/Val/Test splits**: Proper data splitting (70%/15%/15%)
- **Regularization**: Built into Random Forest and Logistic Regression models
- **Validation monitoring**: Tracks performance on validation set during training
- **Model selection**: Automatically selects best model type based on CV scores

## Command Line Options

```bash
python -m app.scripts.train_from_csv job_applicant_dataset.csv [OPTIONS]
```

### Options:

- `--epochs INT`: Number of training epochs (default: 5)
- `--batch-size INT`: Training batch size (default: 16)
- `--learning-rate FLOAT`: Learning rate (default: 2e-5)
- `--model-type {logistic,random_forest,auto}`: Classifier type (default: random_forest)
- `--no-early-stopping`: Disable early stopping
- `--no-cv`: Disable cross-validation
- `--augmentation FLOAT`: Data augmentation factor 0.0-1.0 (default: 0.1)

### Examples:

**Basic training:**
```bash
python -m app.scripts.train_from_csv job_applicant_dataset.csv
```

**Train with more epochs:**
```bash
python -m app.scripts.train_from_csv job_applicant_dataset.csv --epochs 10
```

**Train with custom settings:**
```bash
python -m app.scripts.train_from_csv job_applicant_dataset.csv \
    --epochs 8 \
    --batch-size 32 \
    --learning-rate 3e-5 \
    --model-type auto \
    --augmentation 0.2
```

**Fast training (no CV, no early stopping):**
```bash
python -m app.scripts.train_from_csv job_applicant_dataset.csv \
    --no-cv \
    --no-early-stopping \
    --epochs 3
```

## What Gets Trained

### 1. Similarity Model
- **Purpose**: Matches resumes to job descriptions
- **Input**: Resume text + Job description
- **Output**: Similarity score (0-1)
- **Base Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Fine-tuning**: Uses Best Match label from CSV
- **Saved to**: `trained_models/fine-tuned-resume-matcher/`

### 2. Category Classifier
- **Purpose**: Classifies resumes into job categories
- **Input**: Resume text
- **Output**: Job role category
- **Model Types**: Logistic Regression or Random Forest
- **Auto-selection**: Chooses best model via cross-validation
- **Saved to**: `trained_models/category_classifier_optimized/`

## Training Process

1. **Data Loading**: Loads and cleans the CSV dataset
2. **Data Splitting**: Creates stratified train/validation/test splits
3. **Similarity Model Training**:
   - Prepares training examples from resume-job pairs
   - Fine-tunes sentence transformer
   - Uses early stopping with validation monitoring
4. **Category Classifier Training**:
   - Performs cross-validation for model selection
   - Trains final model on training + validation data
   - Evaluates on held-out test set
5. **Final Evaluation**: Comprehensive evaluation on test set

## Model Evaluation

The script provides:

- **Accuracy scores** for both models
- **Classification reports** with precision/recall/F1
- **Confusion matrices** for detailed analysis
- **Training logs** for monitoring progress

## Output Files

```
trained_models/
├── fine-tuned-resume-matcher/          # Similarity model
│   ├── config.json
│   ├── pytorch_model.bin
│   └── ...
└── category_classifier_optimized/      # Category classifier
    ├── classifier.pkl
    └── label_encoder.pkl
```

## Using Trained Models

### Similarity Model

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("trained_models/fine-tuned-resume-matcher")
resume_emb = model.encode("Resume text...")
job_emb = model.encode("Job description...")
similarity = util.cos_sim(resume_emb, job_emb)
```

### Category Classifier

```python
from app.services.category_classifier import CategoryClassifier

classifier = CategoryClassifier()
classifier.load("category_classifier_optimized")
result = classifier.predict("Resume text...")
print(result["predicted_category"])
```

## Troubleshooting

### "Not enough data for cross-validation"
- The dataset should have at least 50 samples per category
- Reduce CV folds: Use `--no-cv` to disable cross-validation

### "Out of memory"
- Reduce batch size: `--batch-size 8`
- Process in smaller chunks

### "Model not improving"
- Increase epochs: `--epochs 10`
- Adjust learning rate: `--learning-rate 1e-5` (lower) or `--learning-rate 5e-5` (higher)
- Check data quality in CSV

### "Slow training"
- Reduce epochs: `--epochs 3`
- Disable CV: `--no-cv`
- Use smaller model: Edit config to use a smaller sentence transformer

## Best Practices

1. **First Run**: Use default settings to establish baseline
2. **Iteration**: Gradually increase epochs/features if needed
3. **Monitoring**: Watch validation scores for overfitting signs
4. **Regular Updates**: Retrain monthly with new data
5. **Data Quality**: Ensure CSV has clean, valid data

## Expected Performance

With the full dataset (~10,000 samples):

- **Similarity Model**: ~75-85% accuracy
- **Category Classifier**: ~70-80% accuracy

*Note: Actual performance depends on data quality and distribution*

## Next Steps

After training:

1. Test models on new resumes
2. Collect feedback from HR team
3. Fine-tune based on feedback
4. Deploy models to production
5. Set up automated retraining pipeline

## Support

For issues or questions:
- Check training logs in console output
- Review `MODEL_TRAINING_GUIDE.md` for more details
- Ensure all dependencies are installed: `pip install -r requirements.txt`





