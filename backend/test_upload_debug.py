"""
Test script to upload a resume and see detailed error messages.
Run this while your backend server is running in debug mode.
"""
import asyncio
import httpx
import sys
from pathlib import Path

async def test_upload():
    """Test resume upload endpoint with detailed error reporting."""
    print("=" * 60)
    print("RESUME UPLOAD DEBUG TEST")
    print("=" * 60)
    print()
    
    # Check if a test resume file exists
    test_files = [
        Path("test_resume.pdf"),
        Path("../test_resume.pdf"),
        Path("test_resume.docx"),
        Path("../test_resume.docx"),
    ]
    
    resume_file = None
    for test_file in test_files:
        if test_file.exists():
            resume_file = test_file
            break
    
    if not resume_file:
        print("❌ No test resume file found!")
        print("Please create a test PDF or DOCX file named 'test_resume.pdf' or 'test_resume.docx'")
        print("Or modify this script to point to your resume file.")
        return
    
    print(f"📄 Using test file: {resume_file}")
    print()
    
    # Read the file
    try:
        with open(resume_file, "rb") as f:
            file_content = f.read()
        print(f"✅ File read successfully ({len(file_content)} bytes)")
    except Exception as e:
        print(f"❌ Failed to read file: {e}")
        return
    
    print()
    print("🚀 Attempting to upload resume...")
    print()
    
    # Get access token first (you need to be logged in)
    # For testing, you can use a test token or skip auth temporarily
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(base_url=base_url, timeout=60.0) as client:
        # First, try to login to get a token
        print("1. Logging in to get access token...")
        try:
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "credentials": {
                        "email": "user@example.com",
                        "password": "strongpassword"
                    }
                }
            )
            
            if login_response.status_code == 200:
                token_data = login_response.json()
                access_token = token_data.get("access_token")
                print(f"✅ Login successful! Token: {access_token[:20]}...")
            else:
                print(f"⚠️  Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                print()
                print("⚠️  Continuing without auth token (will fail if auth is required)")
                access_token = None
        except Exception as e:
            print(f"⚠️  Login error: {e}")
            print("⚠️  Continuing without auth token")
            access_token = None
        
        print()
        print("2. Uploading resume file...")
        print()
        
        # Prepare the upload
        files = {
            "resume": (resume_file.name, file_content, "application/pdf" if resume_file.suffix == ".pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        
        data = {
            "job_description": "Looking for a Python developer with experience in FastAPI, MongoDB, and AWS.",
            "candidate_name": "Test Candidate"
        }
        
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        
        try:
            response = await client.post(
                "/api/resumes",
                files=files,
                data=data,
                headers=headers
            )
            
            print("=" * 60)
            print("RESPONSE DETAILS")
            print("=" * 60)
            print(f"Status Code: {response.status_code}")
            print()
            
            if response.status_code == 201:
                print("✅ SUCCESS! Resume uploaded and analyzed.")
                print()
                result = response.json()
                print("Response Data:")
                print("-" * 60)
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                print("❌ ERROR! Upload failed.")
                print()
                print("Error Response:")
                print("-" * 60)
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(response.text)
                
                print()
                print("=" * 60)
                print("DEBUGGING INFO")
                print("=" * 60)
                print(f"Status: {response.status_code}")
                print(f"Headers: {dict(response.headers)}")
                print(f"Raw Response: {response.text[:500]}")
                
        except httpx.TimeoutException:
            print("❌ Request timed out! The server might be processing slowly.")
        except httpx.ConnectError:
            print("❌ Cannot connect to server!")
            print("   Make sure the backend is running on http://localhost:8000")
        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
            import traceback
            print()
            print("Full traceback:")
            print("-" * 60)
            traceback.print_exc()

if __name__ == "__main__":
    print()
    asyncio.run(test_upload())
    print()




