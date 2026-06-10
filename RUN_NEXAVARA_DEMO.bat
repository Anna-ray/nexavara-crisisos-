@echo off
echo ============================================================
echo NEXAVARA CrisisOS - Interactive Demonstration
echo The World's First Autonomous Crisis Intelligence OS
echo ============================================================
echo.
echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+
    pause
    exit /b 1
)
echo.
echo Installing dependencies...
pip install pydantic requests python-dotenv --quiet
echo.
echo Starting NEXAVARA CrisisOS Demo...
echo.
python nexavara_demo.py
echo.
echo ============================================================
echo Demo Complete
echo ============================================================
pause

@REM Made with Bob
