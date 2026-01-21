@echo off
REM Chef Assistant GUI Launcher

echo ==========================================
echo Chef Assistant - GUI Mode
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check required packages
echo Checking dependencies...
python -c "import tkinter, cv2, PIL" 2>nul
if errorlevel 1 (
    echo [WARNING] Missing required packages
    echo Installing dependencies...
    pip install opencv-python pillow
)

echo.
echo Starting Chef Assistant GUI...
echo.

REM Run the GUI
python chef_assistant_gui.py

if errorlevel 1 (
    echo.
    echo [ERROR] Chef Assistant exited with an error
    pause
)
