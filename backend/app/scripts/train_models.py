"""
Script to train and fine-tune models for better resume screening accuracy.

Usage:
    python -m app.scripts.train_models --similarity --ner --update-skills
"""

import argparse
import asyncio
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorClient

from ..config import get_settings
from ..services.model_training import ModelTrainer


async def collect_training_data_from_database():
    """Collect training data from existing candidates in the database."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.database_url)
    db = client[settings.mongo_db_name]
    
    candidates = []
    async for candidate in db.candidates.find({"job_description": {"$ne": None}}):
        candidates.append({
            "resume_text": candidate.get("resume_text", ""),
            "job_description": candidate.get("job_description", ""),
            "score": candidate.get("score", {}).get("similarity_score", 0) / 100.0,
        })
    
    client.close()
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Train models for resume screening")
    parser.add_argument("--similarity", action="store_true", help="Fine-tune similarity model")
    parser.add_argument("--ner", action="store_true", help="Train custom NER model")
    parser.add_argument("--update-skills", action="store_true", help="Update skills database")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=16, help="Training batch size")
    
    args = parser.parse_args()
    
    trainer = ModelTrainer()
    
    if args.similarity:
        print("Collecting training data from database...")
        training_data = asyncio.run(collect_training_data_from_database())
        
        if len(training_data) < 10:
            print("⚠️  Warning: Need at least 10 samples for training. Found:", len(training_data))
            print("   Upload more resumes with job descriptions to improve training data.")
            return
        
        print(f"Preparing {len(training_data)} training examples...")
        from sentence_transformers import InputExample
        
        examples = []
        for data in training_data:
            examples.append(
                InputExample(
                    texts=[data["resume_text"], data["job_description"]],
                    label=float(data["score"])
                )
            )
        
        print("Fine-tuning similarity model...")
        trainer.fine_tune_similarity_model(
            examples,
            epochs=args.epochs,
            batch_size=args.batch_size,
        )
        print("✅ Similarity model fine-tuning complete!")
    
    if args.ner:
        print("⚠️  NER training requires manually annotated data.")
        print("   Create training data in training_data/ner_training.json")
        print("   Format: [{\"text\": \"...\", \"entities\": [[start, end, \"SKILL\"], ...]}, ...]")
    
    if args.update_skills:
        print("Updating skills database...")
        # Add common missing skills
        new_skills = [
            "kubernetes", "helm", "ansible", "jenkins", "github actions",
            "redis", "elasticsearch", "kafka", "rabbitmq", "nginx",
            "vue.js", "angular", "svelte", "next.js", "nuxt.js",
            "rust", "swift", "kotlin", "scala", "r",
            "blockchain", "solidity", "web3", "defi", "nft",
        ]
        trainer.update_skills_database(new_skills)
        print(f"✅ Added {len(new_skills)} new skills to database!")


if __name__ == "__main__":
    main()




