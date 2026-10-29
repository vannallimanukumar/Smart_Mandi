@echo off
setlocal
start "Smart Mandi Backend" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%~dp0backend'; if (!(Test-Path '.venv\Scripts\python.exe')) { Write-Host 'Backend venv missing. Run setup commands from README.md first.' -ForegroundColor Red; exit }; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload"
start "Smart Mandi Frontend" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%~dp0frontend'; if (!(Test-Path 'node_modules')) { Write-Host 'Frontend dependencies missing. Run npm install in frontend first.' -ForegroundColor Red; exit }; npm run dev"
endlocal
