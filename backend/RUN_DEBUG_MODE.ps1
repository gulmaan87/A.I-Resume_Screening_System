# PowerShell script to run backend in debug mode
# This will show all errors and logs in the console

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Backend Server in DEBUG MODE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to backend directory
$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $backendDir

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Activating virtual environment..." -ForegroundColor Green
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  No virtual environment found. Using system Python." -ForegroundColor Yellow
}

# Set environment variables for better debugging
$env:PYTHONUNBUFFERED = "1"
$env:ENVIRONMENT = "development"

Write-Host ""
Write-Host "🚀 Starting uvicorn server with DEBUG logging..." -ForegroundColor Green
Write-Host ""
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" * 50 -ForegroundColor Gray
Write-Host ""

# Start the server with debug logging
python -m uvicorn app.main:app `
    --host 0.0.0.0 `
    --port 8000 `
    --reload `
    --log-level debug

