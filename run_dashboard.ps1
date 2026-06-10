# ============================================================================
# NEXAVARA LABS - Dashboard Launcher
# PowerShell script to start the web dashboard
# ============================================================================

Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  ðŸš€ NEXAVARA LABS - PQC Crisis Response Dashboard" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "âœ“ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "âœ— Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow

$requiredPackages = @("flask", "flask-socketio", "flask-cors", "psutil")
$missingPackages = @()

foreach ($package in $requiredPackages) {
    $installed = pip show $package 2>&1
    if ($LASTEXITCODE -ne 0) {
        $missingPackages += $package
    }
}

if ($missingPackages.Count -gt 0) {
    Write-Host ""
    Write-Host "Missing packages detected. Installing..." -ForegroundColor Yellow
    Write-Host ""
    pip install $missingPackages
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "âœ— Failed to install dependencies." -ForegroundColor Red
        Write-Host "  Please run: pip install -r requirements.txt" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "âœ“ All dependencies installed" -ForegroundColor Green

# Start the dashboard
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Starting Dashboard Server..." -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Dashboard will be available at:" -ForegroundColor Green
Write-Host "  â†’ http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  âœ“ Real-time incident monitoring" -ForegroundColor White
Write-Host "  âœ“ Agent status tracking" -ForegroundColor White
Write-Host "  âœ“ Performance metrics visualization" -ForegroundColor White
Write-Host "  âœ“ Live audit trail" -ForegroundColor White
Write-Host "  âœ“ WebSocket real-time updates" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Run the dashboard
python web_dashboard.py

# Made with Bob


