@echo off
REM Run script for Chef Assistant on Windows

REM Activate virtual environment
if exist "chef_venv\Scripts\activate.bat" (
    call chef_venv\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found. Run install_offline_windows.bat first.
    pause
    exit /b 1
)

REM Set environment variables for offline mode
set OFFLINE_MODE=1
if not defined VISION_MODEL set VISION_MODEL=.\models\vision\moondream2-q4.gguf
if not defined WHISPER_MODEL set WHISPER_MODEL=.\models\stt\ggml-base.en.bin
if not defined PIPER_VOICE set PIPER_VOICE=.\models\tts\en_US-amy-low.onnx
if not defined OCR_LANGS set OCR_LANGS=eng+deva
if not defined SPOON_DETECTOR_ONNX set SPOON_DETECTOR_ONNX=
if not defined DEPTH_MODEL_ONNX set DEPTH_MODEL_ONNX=
if not defined CALIB_FILE set CALIB_FILE=

REM Ensure logs directory exists
if not exist "logs" mkdir logs

REM Display startup message
echo ==========================================
echo Chef Assistant - Offline Cooking Helper
echo ==========================================
echo.
echo Models:
echo   Vision: %VISION_MODEL%
echo   STT: %WHISPER_MODEL%
echo   TTS: %PIPER_VOICE%
echo   OCR: %OCR_LANGS%
echo.

REM Check if models exist
set missing_models=0
if not exist "%VISION_MODEL%" (
    echo WARNING: Vision model not found: %VISION_MODEL%
    echo    Run: python scripts\download_models.py
    set missing_models=1
)

if not exist "%WHISPER_MODEL%" (
    echo WARNING: Whisper model not found: %WHISPER_MODEL%
    set missing_models=1
)

if not exist "%PIPER_VOICE%" (
    echo WARNING: Piper voice not found: %PIPER_VOICE%
    set missing_models=1
)

if %missing_models%==1 (
    echo.
    echo Some models are missing. The system will run in mock mode.
    echo Download models with: python scripts\download_models.py
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

REM Run the Chef Assistant
python chef_assistant.py %*

REM Pause on exit if running interactively
if "%1"=="" pause
