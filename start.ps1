# Network Monitor - Startup Script
# Activates the virtual environment and starts the API server.
# Open the dashboard separately: dashboard/index.html

Write-Host "Starting Network Monitor..." -ForegroundColor Cyan

# Activate virtual environment
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting API server at http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Open dashboard/index.html in your browser to view the dashboard." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

uvicorn api.main:app --reload