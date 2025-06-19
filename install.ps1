# PowerShell install script for Windows

Write-Host "[0/6] Checking for Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed. Please install Python 3.8+ and try again." -ForegroundColor Red
    exit 1
}
$pyver = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ([version]$pyver -lt [version]'3.8') {
    Write-Host "Python version must be 3.8 or higher. Found: $pyver" -ForegroundColor Red
    exit 1
}
Write-Host "Python found: $pyver" -ForegroundColor Green

$pip = Get-Command pip -ErrorAction SilentlyContinue
if (-not $pip) {
    Write-Host "pip is not installed. Please install pip for Python." -ForegroundColor Red
    exit 1
}
Write-Host "pip found." -ForegroundColor Green
Start-Sleep -Seconds 1

Write-Host "[1/6] Detecting OS..." -ForegroundColor Yellow
if ($env:OS -notlike '*Windows*') {
    Write-Host "Unsupported OS. Please use install.sh for Mac/Linux." -ForegroundColor Red
    exit 1
}
Start-Sleep -Seconds 2

Write-Host "[2/6] Checking for Ollama..." -ForegroundColor Yellow
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "Ollama not found. Downloading and installing..." -ForegroundColor Yellow
    $ollamaInstaller = "https://ollama.com/download/OllamaSetup.exe"
    $tempPath = "$env:TEMP\OllamaSetup.exe"
    Invoke-WebRequest -Uri $ollamaInstaller -OutFile $tempPath
    Start-Process -FilePath $tempPath -Wait
    Remove-Item $tempPath
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        Write-Host "Failed to install Ollama." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Ollama is already installed." -ForegroundColor Green
}
Start-Sleep -Seconds 2

Write-Host "[3/6] Pulling aya-expanse:8b model..." -ForegroundColor Yellow
$models = ollama list
if ($models -match "aya-expanse") {
    Write-Host "Model aya-expanse:8b already present." -ForegroundColor Green
} else {
    ollama pull aya-expanse:8b
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to pull aya-expanse:8b." -ForegroundColor Red
        exit 1
    }
}
Start-Sleep -Seconds 2

Write-Host "[4/6] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}
Start-Sleep -Seconds 2

Write-Host "[5/6] Installing Python requirements..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install requirements." -ForegroundColor Red
    deactivate
    exit 1
}
deactivate
Start-Sleep -Seconds 2

Write-Host "[6/6] Setup complete!" -ForegroundColor Green
Write-Host "`nYou can now run the system with:" -ForegroundColor Green
Write-Host "cd scripts && ./run_processing.sh`n" -ForegroundColor Yellow 