@echo off
REM ===== Build SolveX.exe (chay tren Windows) =====
setlocal

echo [1/4] Kiem tra Python...
python --version || (echo Chua cai Python. Tai tai python.org va nho tick "Add to PATH". & pause & exit /b 1)

echo [2/4] Tao moi truong ao...
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat

echo [3/4] Cai thu vien...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo [4/4] Dong goi...
pyinstaller --noconfirm --clean solvex.spec

echo.
echo XONG. File nam o: dist\SolveX.exe
pause
