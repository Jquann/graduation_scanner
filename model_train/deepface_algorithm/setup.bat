@echo off
echo Setting up Dlib Algorithm Environment...
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error creating virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment and install packages
echo Activating virtual environment and installing packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip

REM Install packages from requirements.txt (includes pre-compiled dlib wheel)
echo Installing dependencies including pre-compiled dlib...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error installing packages
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo Note: Using face_recognition library (dlib backend) - no model download needed.
echo.
echo To run the Face Recognition test:
echo 1. Run: venv\Scripts\activate.bat
echo 2. Run: python dlib_test.py
echo.
pause
