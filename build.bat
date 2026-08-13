@echo off
title SolveX Auto Update Build
echo ======================================================
echo           SolveX Auto Update Installer & Builder
echo ======================================================

echo [+] Stopping any running SolveX.exe and update.exe instances...
taskkill /F /IM SolveX.exe 2>nul
taskkill /F /IM update.exe 2>nul
timeout /t 1 /nobreak >nul

echo [+] Starting PyInstaller build process...
.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean solvex.spec

if %ERRORLEVEL% EQU 0 (
    echo ======================================================
    echo [✓] Build Completed Successfully!
    echo [✓] Launching new SolveX version...
    echo ======================================================
    start "" dist\SolveX.exe
) else (
    echo ======================================================
    echo [!] Build Failed with Error Code %ERRORLEVEL%
    echo ======================================================
    pause
)
