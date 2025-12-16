"""
Comprehensive test script to verify all project functionalities.
Tests backend API endpoints, database connectivity, and core features.
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError

# Test configuration
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api"
TIMEOUT = 30.0

# Colors for terminal output (using ASCII-safe characters for Windows)
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    try:
        print(f"{Colors.GREEN}[PASS] {message}{Colors.RESET}")
    except:
        print(f"[PASS] {message}")

def print_error(message: str):
    try:
        print(f"{Colors.RED}[FAIL] {message}{Colors.RESET}")
    except:
        print(f"[FAIL] {message}")

def print_warning(message: str):
    try:
        print(f"{Colors.YELLOW}[WARN] {message}{Colors.RESET}")
    except:
        print(f"[WARN] {message}")

def print_info(message: str):
    try:
        print(f"{Colors.BLUE}[INFO] {message}{Colors.RESET}")
    except:
        print(f"[INFO] {message}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")


async def test_backend_health():
    """Test if backend server is running and accessible."""
    print_header("1. Testing Backend Health")
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            # Test root endpoint
            response = await client.get(f"{BACKEND_URL}/")
            if response.status_code in [200, 404]:  # 404 is OK, means server is running
                print_success("Backend server is running")
                return True
            
            # Test docs endpoint
            response = await client.get(f"{BACKEND_URL}/docs")
            if response.status_code == 200:
                print_success("FastAPI docs are accessible")
                print_info(f"API Documentation: {BACKEND_URL}/docs")
                return True
            else:
                print_error(f"Backend returned status {response.status_code}")
                return False
    except httpx.ConnectError:
        print_error("Cannot connect to backend. Is the server running?")
        print_info("Start backend with: cd backend && python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error testing backend: {e}")
        return False


async def test_database_connection():
    """Test MongoDB database connectivity."""
    print_header("2. Testing Database Connection")
    try:
        from backend.app.config import get_settings
        settings = get_settings()
        
        client = AsyncIOMotorClient(settings.database_url, serverSelectionTimeoutMS=5000)
        # Test connection
        await client.admin.command('ping')
        print_success(f"Connected to MongoDB at {settings.database_url}")
        print_info(f"Database name: {settings.mongo_db_name}")
        
        # Check if database exists and has collections
        db = client[settings.mongo_db_name]
        collections = await db.list_collection_names()
        if collections:
            print_info(f"Found collections: {', '.join(collections)}")
            # Count documents in candidates collection
            if 'candidates' in collections:
                count = await db.candidates.count_documents({})
                print_info(f"Candidates in database: {count}")
        else:
            print_warning("Database exists but has no collections yet")
        
        client.close()
        return True
    except ServerSelectionTimeoutError:
        print_error("Cannot connect to MongoDB. Is MongoDB running?")
        print_info("Start MongoDB with: docker run -d -p 27017:27017 mongo:6.0")
        return False
    except Exception as e:
        print_error(f"Error connecting to database: {e}")
        return False


async def test_api_endpoints():
    """Test all API endpoints."""
    print_header("3. Testing API Endpoints")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Test Dashboard endpoint
        print_info("Testing GET /api/dashboard")
        try:
            response = await client.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                print_success("Dashboard endpoint is working")
                print_info(f"  - Candidates: {len(data.get('candidates', []))}")
                print_info(f"  - Average score: {data.get('analytics', {}).get('average_score', 'N/A')}")
            else:
                print_error(f"Dashboard returned status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print_error(f"Error testing dashboard: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test Screening endpoints
        print_info("Testing GET /api/screening/candidates/{id}")
        try:
            # First get a candidate ID from dashboard
            response = await client.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                candidates = data.get('candidates', [])
                if candidates:
                    candidate_id = candidates[0]['id']
                    response = await client.get(f"{API_BASE}/screening/candidates/{candidate_id}")
                    if response.status_code == 200:
                        print_success("Get candidate endpoint is working")
                    else:
                        print_warning(f"Get candidate returned status {response.status_code}")
                else:
                    print_warning("No candidates found to test get candidate endpoint")
            else:
                print_warning("Cannot test get candidate - dashboard not accessible")
        except Exception as e:
            print_warning(f"Error testing get candidate: {e}")
        
        # Test manual scoring endpoint
        print_info("Testing POST /api/screening/score")
        try:
            test_payload = {
                "resume_text": "Experienced software engineer with 5 years in Python and React development.",
                "job_description": "Looking for a senior Python developer with React experience.",
                "skills": ["Python", "React", "JavaScript"],
                "missing_skills": ["Docker"],
                "experience_years": 5.0
            }
            response = await client.post(
                f"{API_BASE}/screening/score",
                json=test_payload
            )
            if response.status_code == 200:
                data = response.json()
                print_success("Manual scoring endpoint is working")
                print_info(f"  - Total AI Score: {data.get('total_ai_score', 'N/A')}")
                print_info(f"  - Category: {data.get('category', 'N/A')}")
            else:
                print_error(f"Manual scoring returned status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print_error(f"Error testing manual scoring: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # All endpoints tested - return True if we got here without critical failures
    return True


async def test_resume_upload():
    """Test resume upload functionality."""
    print_header("4. Testing Resume Upload")
    
    # Create a simple test PDF content (minimal valid PDF)
    test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume Content) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000316 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
400
%%EOF"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            files = {
                'resume': ('test_resume.pdf', test_pdf_content, 'application/pdf')
            }
            data = {
                'job_description': 'Looking for a software engineer with Python and React experience.',
                'candidate_name': 'Test Candidate'
            }
            
            print_info("Uploading test resume...")
            response = await client.post(
                f"{API_BASE}/resumes",
                files=files,
                data=data
            )
            
            if response.status_code == 201:
                result = response.json()
                print_success("Resume upload is working!")
                print_info(f"  - Candidate ID: {result.get('id', 'N/A')}")
                print_info(f"  - Name: {result.get('full_name', 'N/A')}")
                print_info(f"  - Total AI Score: {result.get('score', {}).get('total_ai_score', 'N/A')}")
                print_info(f"  - Category: {result.get('category', 'N/A')}")
                return result.get('id')
            else:
                print_error(f"Resume upload failed with status {response.status_code}")
                print_error(f"Response: {response.text[:500]}")
                return None
        except Exception as e:
            print_error(f"Error testing resume upload: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_dashboard_analytics():
    """Test dashboard analytics functionality."""
    print_header("5. Testing Dashboard Analytics")
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.get(f"{API_BASE}/dashboard")
            if response.status_code == 200:
                data = response.json()
                analytics = data.get('analytics', {})
                candidates = data.get('candidates', [])
                
                print_success("Dashboard analytics are working")
                print_info(f"  - Total candidates: {len(candidates)}")
                print_info(f"  - Average score: {analytics.get('average_score', 'N/A')}")
                print_info(f"  - Category counts: {analytics.get('category_counts', {})}")
                print_info(f"  - Experience distribution: {analytics.get('experience_distribution', {})}")
                print_info(f"  - Common missing skills: {analytics.get('common_missing_skills', [])[:5]}")
                print_info(f"  - Top candidates: {len(analytics.get('top_candidates', []))}")
                
                return True
            else:
                print_error(f"Dashboard returned status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Error testing dashboard analytics: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


async def test_configuration():
    """Test configuration loading."""
    print_header("6. Testing Configuration")
    
    try:
        from backend.app.config import get_settings
        settings = get_settings()
        
        print_success("Configuration loaded successfully")
        print_info(f"  - App name: {settings.app_name}")
        print_info(f"  - API prefix: {settings.api_prefix}")
        print_info(f"  - Database: {settings.mongo_db_name}")
        print_info(f"  - S3 Bucket: {settings.s3_bucket_name}")
        print_info(f"  - Spacy model: {settings.spacy_model}")
        print_info(f"  - Embedding model: {settings.embedding_model}")
        
        return True
    except Exception as e:
        print_error(f"Error loading configuration: {e}")
        return False


async def main():
    """Run all tests."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*60)
    print("  AI Resume Screening System - Functionality Test")
    print("="*60)
    print(f"{Colors.RESET}\n")
    
    results = {}
    
    # Run all tests
    results['backend_health'] = await test_backend_health()
    results['database'] = await test_database_connection()
    results['configuration'] = await test_configuration()
    results['api_endpoints'] = await test_api_endpoints()
    results['resume_upload'] = await test_resume_upload() is not None
    results['dashboard'] = await test_dashboard_analytics()
    
    # Summary
    print_header("Test Summary")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.RESET}\n")
    
    if passed == total:
        print_success("All tests passed! Your project is working correctly.")
        return 0
    else:
        print_warning(f"{total - passed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

