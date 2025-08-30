@echo off
echo Running Dlib Algorithm Test...
echo.

if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python dlib_test.py
pause
