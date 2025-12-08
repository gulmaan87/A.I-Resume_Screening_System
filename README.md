# AI-Powered Cloud-Based Resume Screening System for HR

An end-to-end platform that ingests resumes, performs AI-driven analysis, stores structured insights, and surfaces candidate intelligence through a modern dashboard UI. The backend is powered by FastAPI, MongoDB, and AWS S3; the frontend is a React + Tailwind single-page app.

## Features

- **Resume Upload API**: Accepts PDF/DOCX files, stores them in S3, persists metadata, and orchestrates the parsing + scoring pipeline.
- **NLP Parsing Engine**: Extracts text, skills, experience, education, certifications, and contact details using `pdfminer.six`, `python-docx`, and `spaCy`.
- **AI Screening Engine**: Combines spaCy NER, SentenceTransformer semantic similarity, and heuristic scoring to compute skill, experience, and overall AI scores.
- **Candidate Categorization**: Automatically flags resumes as Strong Fit, Medium Fit, or Weak Fit.
- **Dashboard Analytics**: Provides aggregated analytics (average score, category counts, skill gaps, experience distribution) and a sortable candidate table.
- **Frontend Experience**: React UI for uploading resumes, viewing breakdowns, and monitoring pipeline health.
- **Demo Data Seeder**: Generates 20 realistic mock candidates to jumpstart evaluation environments.
- **Containerization**: Dockerfiles for backend and frontend plus docker-compose for the full stack.

## Project Structure

```
/backend
  /app
    main.py
    config.py
    /routes
    /services
    /models
    /scripts
/frontend
  package.json
  /src
    /pages
    /components
package.json
docker-compose.yml
env.example
```

## Prerequisites

- Python 3.10+
- Node.js 18+ (for frontend dev server)
- MongoDB 6.x (local or MongoDB Atlas)
- AWS S3 bucket (or compatible object storage such as MinIO/LocalStack)

## Environment Variables

The backend now auto-loads the first file it finds in this order: `.env`, `.env.local`, then `env.example`. For local hacking the bundled defaults (localhost Mongo, fake AWS keys, local bucket name) are enough to boot the stack. **Before deploying**, create a real `.env` with production credentials to override the placeholders.

Key settings:

- `DB_URI`, `DB_NAME` – Mongo connection string and database.
- `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGION`, `S3_BUCKET_NAME` – Credentials for object storage.
- `SPACY_MODEL`, `EMBEDDING_MODEL_NAME` – NLP models (defaults provided).
- `VITE_API_BASE_URL` – Frontend API base URL (used in production builds).

> **Note:** Download the spaCy model once locally: `python -m spacy download en_core_web_sm`.

Frontend builds read `VITE_API_BASE_URL` at compile time. Create a frontend `.env` (e.g. `frontend/.env.production`) with the API origin you expect in production; Vite dev server already proxies to `http://localhost:8000`.

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The FastAPI docs are available at `http://localhost:8000/docs`.

### Seeding Demo Data

Ensure MongoDB is running, then execute:

```bash
cd backend
python -m app.scripts.seed_demo
```

This inserts 20 mock candidates with varied scores and metadata.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

By default the Vite dev server proxies `/api` to `http://localhost:8000`.

## Docker Workflow

Build and run the complete stack:

```bash
docker-compose up --build
```

Services:

- `backend` → `http://localhost:8000`
- `frontend` → `http://localhost:5173`
- `mongo` → exposed on `27017` for local access

## API Overview

- `POST /api/resumes` – Upload and analyze a resume (multipart form-data).
- `GET /api/screening/candidates/{id}` – Retrieve a specific candidate.
- `POST /api/screening/score` – Manually score raw resume text + job description.
- `GET /api/dashboard` – Retrieve candidate list and analytics summary.

Refer to the automatically generated Swagger UI (`/docs`) or ReDoc (`/redoc`) for detailed schemas.

## Testing & Quality

- **Backend**: relies on FastAPI validation and typing. Add Pytest suites under `backend/tests` as needed.
- **Frontend**: ESLint and Prettier configs included (`npm run lint`, `npm run format`).

## Next Steps & Enhancements

- Integrate authentication/authorization for HR teams.
- Persist job descriptions per requisition and compare candidates within a role.
- Implement webhooks/notifications for new strong-fit candidates.
- Add automated unit/integration tests for critical paths.

---

Built by an AI senior Python developer to accelerate HR talent acquisition workflows.

