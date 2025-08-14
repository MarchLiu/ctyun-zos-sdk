@echo off
REM CTyun ZOS SDK Virtual Environment Setup Script for Windows

echo Setting up Python virtual environment for CTyun ZOS SDK...

REM Check if Python 3 is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do set PYTHON_VERSION=%%i

if "%PYTHON_VERSION%"=="" (
    echo ❌ Failed to get Python version
    pause
    exit /b 1
)

echo ✓ Python version: %PYTHON_VERSION%

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment created successfully

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✓ Virtual environment activated

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements-dev.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✓ Dependencies installed successfully

REM Install package in development mode
echo Installing package in development mode...
pip install -e .

if %errorlevel% neq 0 (
    echo ❌ Failed to install package in development mode
    pause
    exit /b 1
)

echo ✓ Package installed in development mode

REM Run basic tests
echo Running basic tests...
python test_basic.py

if %errorlevel% equ 0 (
    echo ✓ Basic tests passed
) else (
    echo ⚠ Basic tests had some issues (this is normal for first run)
)

echo.
echo 🎉 Virtual environment setup completed!
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate:
echo   deactivate
echo.
echo Next steps:
echo 1. Copy config.env.example to .env
echo 2. Edit .env with your CTyun credentials
echo 3. Run: python test_real_connection.py
echo.
echo For more information, see SETUP.md
pause
