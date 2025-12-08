You are an expert senior Python developer.

Build a complete production-ready project called:
"AI-Powered Cloud-Based Resume Screening System for HR".

========================================
🧱 TECHNOLOGY REQUIREMENTS
========================================
Backend:
- Python 3.10+
- FastAPI framework
- Uvicorn server
- MongoDB Atlas or PostgreSQL (any one)
- AWS S3 SDK for file storage
- NLP libraries:
    - spaCy
    - HuggingFace Transformers
    - sentence-transformers
- Resume parsing libs:
    - pdfminer.six
    - python-docx

Frontend (auto-generate basic UI):
- React + Tailwind
- Resume upload page
- Dashboard page to show scoring + categories

========================================
🎯 CORE FEATURES TO BUILD
========================================

1. **Resume Upload API**
   - Accept PDF or DOCX
   - Store file in AWS S3
   - Save metadata in DB

2. **Resume Parsing Engine**
   - Extract text using pdfminer.six / docx2txt
   - Clean text, normalize formatting
   - Extract:
       - Skills
       - Work experience
       - Education
       - Certifications
       - Contact info

3. **AI Screening Engine**
   - Use spaCy for NER (skills, degrees, companies)
   - Use SentenceTransformer for job-resume similarity score
   - Use ML logic to generate:
       - skill_match_score (0–100)
       - experience_score (0–100)
       - total_ai_score (0–100)

4. **Candidate Categorization**
   - Strong Fit (score > 80)
   - Medium Fit (score 60–80)
   - Weak Fit (< 60)

5. **Dashboard API**
   - Get all candidates sorted by score
   - Filter by category
   - Return analytics summary:
       - average score
       - common missing skills
       - experience distribution

6. **Frontend**
   - Simple React app:
       - Resume upload
       - Table of candidates
       - Score display
       - Category tags
       - Analytics components

========================================
📁 PROJECT STRUCTURE
========================================
Generate exactly this structure:

/backend
    /app
        main.py
        /routes
            upload.py
            screening.py
            dashboard.py
        /services
            parser.py
            nlp_engine.py
            scorer.py
            storage.py
        /models
            candidate_model.py
        config.py

/frontend
    /src
        /components
        /pages
            Upload.jsx
            Dashboard.jsx
    package.json
package.json
README.md

========================================
🧠 IMPLEMENTATION DETAILS
========================================

Resume Parsing:
- Use pdfminer.six for PDF
- Use python-docx for DOCX
- Add cleaning functions
- Extract skills via a predefined skills.json list

NLP Engine:
- Load spaCy model: en_core_web_sm
- Extract entities for skills, orgs, degrees
- Use SentenceTransformer('all-MiniLM-L6-v2') for similarity scoring

Scoring Logic:
- skill match = (# matched skills / total relevant skills) * 100
- experience extraction using regex for "X years" phrases
- final score = (similarity*0.6 + skill_match*0.3 + experience*0.1)

Storage:
- Upload resumes to S3 bucket
- Store metadata + extracted data in MongoDB or Postgres

Dashboard:
- Return analytics:
  - avg score
  - skill gap list
  - category counts
  - best candidates

========================================
🧪 ADD DEMO DATA
========================================
- Add a script to generate sample resumes and fill the database with 20 mock candidates.

========================================
🚀 DEPLOYMENT SETUP
========================================
- Add Dockerfile for backend + frontend
- Add docker-compose.yml
- Add environment variables template:
    - DB_URI
    - AWS_ACCESS_KEY
    - AWS_SECRET_KEY
    - S3_BUCKET_NAME

========================================
📌 OUTPUT EXPECTATION
========================================
Generate:
- All backend files with full working code
- All frontend files with working UI
- Proper comments and clean code
- Instructions in README.md
- Docker support
- API documentation with FastAPI Swagger UI

========================================
Begin creating the entire project now.
========================================
