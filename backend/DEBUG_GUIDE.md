# Backend Debug Mode Guide

This guide will help you run the backend in debug mode to see detailed error messages when resume upload fails.

## Method 1: Using the PowerShell Script (Easiest)

1. Open PowerShell in the `backend` directory
2. Run:
   ```powershell
   .\RUN_DEBUG_MODE.ps1
   ```
3. The server will start and show all logs/errors in the console
4. Keep this window open to see errors when you upload a resume

## Method 2: Manual Command Line

1. Open PowerShell or Command Prompt
2. Navigate to the backend directory:
   ```powershell
   cd A.I-Resume_Screening_System\backend
   ```
3. Activate virtual environment (if exists):
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
   Or on Windows CMD:
   ```cmd
   venv\Scripts\activate.bat
   ```
4. Set environment variables:
   ```powershell
   $env:PYTHONUNBUFFERED = "1"
   $env:ENVIRONMENT = "development"
   ```
5. Start the server with debug logging:
   ```powershell
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
   ```

## What You'll See

When running in debug mode, you'll see:
- ✅ Server startup messages
- ✅ All HTTP requests with details
- ✅ Full Python stack traces for any errors
- ✅ Database connection status
- ✅ Model loading messages

## Testing the Upload

### Option 1: Use the Test Script

1. Make sure backend is running in debug mode (see above)
2. In a NEW terminal window, navigate to backend directory
3. Run the test script:
   ```powershell
   python test_upload_debug.py
   ```
4. The script will:
   - Try to login
   - Upload a test resume
   - Show detailed error messages if anything fails

### Option 2: Use Swagger UI

1. Open browser: http://localhost:8000/docs
2. Find the `POST /api/resumes` endpoint
3. Click "Try it out"
4. Upload a resume file
5. Click "Execute"
6. Check both:
   - The response in Swagger UI
   - The error messages in your backend console (where debug mode is running)

### Option 3: Use Frontend

1. Make sure backend is running in debug mode
2. Start your frontend (if not already running)
3. Try uploading a resume through the UI
4. Watch the backend console for error messages

## What to Look For

When you see an error, look for:

1. **The Error Type**: 
   - `FileNotFoundError` = Missing file/model
   - `ImportError` = Missing Python package
   - `AttributeError` = Code bug (wrong attribute name)
   - `ValueError` = Invalid data/configuration
   - `ConnectionError` = Database/S3 connection issue

2. **The Stack Trace**: Shows exactly which line of code failed

3. **The Error Message**: Usually explains what went wrong

## Common Issues and Fixes

### Issue: "Module not found"
**Fix**: Install missing package: `pip install <package-name>`

### Issue: "spaCy model not found"
**Fix**: Download model: `python -m spacy download en_core_web_sm`

### Issue: "Database connection failed"
**Fix**: Check MongoDB is running and DB_URI in .env is correct

### Issue: "S3 connection failed"
**Fix**: Check AWS credentials in .env or use local storage

### Issue: "Category classifier not available"
**Fix**: This is OK - the system will work without it, just won't predict categories

## Getting Help

When reporting errors, include:
1. The full error message from the console
2. The stack trace (the lines showing file paths and line numbers)
3. What you were trying to do (upload resume, etc.)
4. The file you were uploading (if applicable)

## Next Steps

After identifying the error:
1. Note the error type and message
2. Check the stack trace to see which file/line failed
3. Report back with the error details
4. I can then provide a permanent fix!






















