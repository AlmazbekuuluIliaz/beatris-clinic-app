$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$VenvCandidates = @(
    (Join-Path $ProjectRoot "venv\Scripts\python.exe"),
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe")
)

$Python = $VenvCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1

if (-not $Python) {
    Write-Error @"
Virtual environment Python was not found.
Create and install dependencies with:
  python -m venv venv
  .\venv\Scripts\python.exe -m pip install -r requirements.txt
"@
}

$VenvRoot = Split-Path -Parent (Split-Path -Parent $Python)
$Alembic = Join-Path $VenvRoot "Scripts\alembic.exe"

if (-not (Test-Path -LiteralPath ".env")) {
    Write-Warning ".env was not found. The app will use defaults from app/core/config.py."
}

Write-Host "Using Python: $Python"

if (-not (Test-Path -LiteralPath $Alembic)) {
    Write-Error "Alembic was not found in the virtual environment. Install dependencies: $Python -m pip install -r requirements.txt"
}

Write-Host "Applying database migrations..."
& $Alembic upgrade head

Write-Host ""
Write-Host "Starting Beatris backend..."
Write-Host "Admin:   http://127.0.0.1:8000/admin"
Write-Host "Swagger: http://127.0.0.1:8000/docs"
Write-Host ""

& $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
