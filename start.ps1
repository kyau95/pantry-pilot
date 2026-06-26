# Windows PowerShell Launch Script for Pantry Pilot (FastAPI Backend + Svelte Frontend)
# Works natively on Windows, with automatic/manual fallback to WSL.

param(
    [switch]$UseWsl
)

$currentDir = $PSScriptRoot
if (-not $currentDir) {
    $currentDir = Get-Location
}

# Auto-detect if we are running in a WSL UNC path
$shouldUseWsl = $UseWsl
if (-not $shouldUseWsl) {
    if ($currentDir.ToString().StartsWith("\\wsl")) {
        $shouldUseWsl = $true
        Write-Host "ℹ️ WSL workspace detected. Auto-switching to WSL execution mode." -ForegroundColor Yellow
    }
}

if ($shouldUseWsl) {
    # WSL Ubuntu Execution
    $wslProjectDir = "/home/keyau/pantry-pilot"
    
    Write-Host "🚀 Launching Pantry Pilot Backend (FastAPI) inside WSL..." -ForegroundColor Cyan
    $backendJob = Start-Job -ScriptBlock {
        param($dir)
        wsl bash -c "cd $dir && source backend/venv/bin/activate && python backend/main.py"
    } -ArgumentList $wslProjectDir

    Start-Sleep -Seconds 2

    Write-Host "⚡ Launching Pantry Pilot Frontend (Svelte) inside WSL..." -ForegroundColor Green
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        wsl bash -c "cd $dir && npm run dev"
    } -ArgumentList $wslProjectDir
} else {
    # Native Windows Execution
    Write-Host "🚀 Launching Pantry Pilot Backend (FastAPI) natively on Windows..." -ForegroundColor Cyan
    
    $venvPath = Join-Path $currentDir "backend\venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    if (-not (Test-Path $activateScript)) {
        Write-Host "⚠️ Windows virtual environment not found at $venvPath." -ForegroundColor Yellow
        Write-Host "Please create it using: python -m venv backend\venv" -ForegroundColor Yellow
        Write-Host "Then install dependencies: .\backend\venv\Scripts\pip.exe install -r backend\requirements.txt" -ForegroundColor Yellow
        Write-Host "Attempting to run Python directly from system PATH..." -ForegroundColor Yellow
    }

    $backendJob = Start-Job -ScriptBlock {
        param($dir, $script)
        Set-Location $dir
        if (Test-Path $script) {
            # Source/Activate the native Windows virtual environment
            . $script
        }
        python backend/main.py
    } -ArgumentList $currentDir, $activateScript

    Start-Sleep -Seconds 2

    Write-Host "⚡ Launching Pantry Pilot Frontend (Svelte) natively on Windows..." -ForegroundColor Green
    $frontendJob = Start-Job -ScriptBlock {
        param($dir)
        Set-Location $dir
        # Run npm via cmd to prevent execution failures inside background jobs
        cmd.exe /c "npm run dev"
    } -ArgumentList $currentDir
}

Write-Host "==================================================" -ForegroundColor Gray
Write-Host "🎯 Both servers are running in background jobs." -ForegroundColor White
Write-Host "   - Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   - Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "🛑 Press Ctrl+C in this terminal to shut down both servers safely." -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Gray

# Trap Ctrl+C (SIGINT) to clean up jobs
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`n🛑 Terminating background server processes..." -ForegroundColor Red
    # Stop background jobs
    Stop-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
    Stop-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -Force -ErrorAction SilentlyContinue
    Remove-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
    
    if ($shouldUseWsl) {
        wsl killall python 2>$null
        wsl killall node 2>$null
    } else {
        # Stop native processes spawned by jobs
        Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
        Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue
    }
    Write-Host "👋 Shutdown complete." -ForegroundColor Green
}
