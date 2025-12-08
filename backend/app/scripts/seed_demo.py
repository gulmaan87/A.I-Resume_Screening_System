import asyncio
import random
from datetime import datetime, timedelta, timezone

from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient

from ..config import get_settings
from ..services.scorer import calculate_scores


async def seed_demo_data(record_count: int = 20) -> None:
    settings = get_settings()
    client = AsyncIOMotorClient(settings.database_url)
    db = client[settings.mongo_db_name]
    collection = db.candidates

    faker = Faker()
    Faker.seed(42)
    random.seed(42)

    job_descriptions = [
        "Lead backend engineer responsible for scaling microservices and API-driven integrations.",
        "Frontend specialist building accessible design systems with React and Tailwind.",
        "Machine learning engineer optimizing NLP pipelines for resume intelligence.",
        "Cloud architect focused on AWS infrastructure, DevOps automation, and security best practices.",
    ]

    skill_pool = [
        "python",
        "fastapi",
        "django",
        "react",
        "node.js",
        "aws",
        "docker",
        "kubernetes",
        "terraform",
        "sql",
        "mongodb",
        "postgresql",
        "machine learning",
        "data analysis",
        "nlp",
        "pandas",
        "numpy",
        "ci/cd",
        "git",
        "leadership",
    ]

    await collection.delete_many({"metadata.s3_key": {"$regex": "^demo/"}})

    documents = []
    for idx in range(record_count):
        full_name = faker.name()
        email = faker.email()
        phone = faker.phone_number()
        experience_years = round(random.uniform(1, 18), 1)
        chosen_skills = random.sample(skill_pool, k=random.randint(5, 10))
        job_description = random.choice(job_descriptions)

        similarity_score = random.uniform(55, 95)
        scoring = calculate_scores(
            found_skills=chosen_skills,
            missing_skills=sorted(set(skill_pool) - set(chosen_skills))[:20],
            experience_years=experience_years,
            similarity_score=similarity_score,
        )

        created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 45))

        documents.append(
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "job_description": job_description,
                "skills": chosen_skills,
                "missing_skills": scoring.missing_skills,
                "experience_years": experience_years,
                "education": [
                    f"{random.choice(['BSc', 'MSc', 'BEng'])} in {random.choice(['Computer Science', 'Information Systems', 'Software Engineering'])}",
                    f"{random.choice(['Certified', 'Professional'])} {random.choice(['Scrum Master', 'AWS Architect', 'Data Scientist'])}",
                ],
                "certifications": [
                    f"{random.choice(['AWS', 'Azure', 'GCP'])} {random.choice(['Solutions Architect', 'Developer', 'Data Engineer'])}"
                ],
                "last_role": random.choice(
                    ["Senior Engineer", "Tech Lead", "Staff Engineer", "Machine Learning Specialist"]
                ),
                "summary": faker.paragraph(nb_sentences=3),
                "category": scoring.category,
                "score": {
                    "skill_match_score": scoring.skill_match_score,
                    "experience_score": scoring.experience_score,
                    "similarity_score": scoring.similarity_score,
                    "total_ai_score": scoring.total_ai_score,
                },
                "job_similarity_breakdown": scoring.job_similarity_breakdown,
                "resume_text": faker.text(max_nb_chars=1200),
                "metadata": {
                    "original_filename": f"{full_name.replace(' ', '_').lower()}_demo.pdf",
                    "content_type": "application/pdf",
                    "file_size": random.randint(150_000, 400_000),
                    "s3_key": f"demo/resume_{idx}.pdf",
                    "s3_url": None,
                },
                "parsed_entities": {
                    "skills": chosen_skills,
                    "organizations": [faker.company() for _ in range(2)],
                    "degrees": ["Bachelors", "Masters"],
                },
                "created_at": created_at,
                "updated_at": created_at,
            }
        )

    if documents:
        await collection.insert_many(documents)
    client.close()


if __name__ == "__main__":
    asyncio.run(seed_demo_data())

