@echo off
REM Installation script for Chef Assistant on Windows
REM This script sets up all dependencies for offline operation

echo ==========================================
echo Chef Assistant - Windows Installation
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.8+ is required but not found.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check Python version
python -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.8 or higher is required.
    pause
    exit /b 1
)

REM Step 1: Create project directories
echo Step 1: Creating project directories...
if not exist "models\vision" mkdir models\vision
if not exist "models\stt" mkdir models\stt
if not exist "models\tts" mkdir models\tts
if not exist "models\detectors" mkdir models\detectors
if not exist "models\depth" mkdir models\depth
if not exist "config" mkdir config
if not exist "logs" mkdir logs
if not exist "data\calibration" mkdir data\calibration
if not exist "temp" mkdir temp
echo Directories created successfully
echo.

REM Step 2: Create Python virtual environment
echo Step 2: Creating Python virtual environment...
python -m venv chef_venv
call chef_venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip setuptools wheel
echo Virtual environment created successfully
echo.

REM Step 3: Install Python dependencies
echo Step 3: Installing Python dependencies...
pip install -r requirements.txt
echo Python dependencies installed successfully
echo.

REM Step 4: Install Tesseract OCR
echo Step 4: Tesseract OCR Setup
echo.
echo Checking for Tesseract...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo Tesseract found at C:\Program Files\Tesseract-OCR\
) else (
    echo WARNING: Tesseract OCR not found!
    echo.
    echo Please download and install Tesseract from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo Recommended: tesseract-ocr-w64-setup-v5.3.x.exe
    echo During installation, select "Additional language data" and install:
    echo   - English
    echo   - Hindi (Devanagari)
    echo   - Marathi (if available)
    echo.
    echo After installation, add to PATH:
    echo   C:\Program Files\Tesseract-OCR
    echo.
)
echo.

REM Step 5: Setup llama.cpp for Vision LLM
echo Step 5: llama.cpp Setup for Vision LLM
echo.
if not exist "llama.cpp" (
    echo Downloading llama.cpp...
    echo Please download llama.cpp Windows build from:
    echo https://github.com/ggerganov/llama.cpp/releases
    echo.
    echo Download: llama-master-[commit]-bin-win-[arch].zip
    echo Extract to: llama.cpp\ directory
    echo.
    echo Or build from source using CMake and Visual Studio.
    echo.
) else (
    echo llama.cpp directory found
)
echo.

REM Step 6: Setup whisper.cpp for STT
echo Step 6: whisper.cpp Setup for STT
echo.
if not exist "whisper.cpp" (
    echo Downloading whisper.cpp...
    echo Please download whisper.cpp Windows build from:
    echo https://github.com/ggerganov/whisper.cpp/releases
    echo.
    echo Download: whisper-bin-x64.zip
    echo Extract to: whisper.cpp\ directory
    echo.
) else (
    echo whisper.cpp directory found
)
echo.

REM Step 7: Setup Piper TTS
echo Step 7: Piper TTS Setup
echo.
if not exist "piper" (
    echo Downloading Piper TTS...
    echo Please download Piper for Windows from:
    echo https://github.com/rhasspy/piper/releases
    echo.
    echo Download: piper_windows_amd64.zip
    echo Extract to: piper\ directory
    echo.
) else (
    echo piper directory found
)
echo.

REM Step 8: Create default configuration
echo Step 8: Creating default configuration...
(
echo # Chef Assistant Configuration
echo offline_mode: true
echo log_level: INFO
echo.
echo # Model paths ^(update after downloading models^)
echo vision_model: ./models/vision/moondream2-q4.gguf
echo whisper_model: ./models/stt/ggml-base.en.bin
echo piper_voice: ./models/tts/en_US-amy-low.onnx
echo.
echo # OCR settings
echo ocr_languages: eng+deva
echo.
echo # Camera settings
echo camera_index: 0
echo camera_resolution: [640, 480]
echo camera_fps: 2
echo.
echo # Audio settings
echo sample_rate: 16000
echo vad_threshold: 0.5
) > config\default_config.yaml
echo Configuration file created
echo.

REM Step 9: Test installations
echo Step 9: Testing installations...
python -c "import numpy, cv2, PIL, yaml; print('Python packages: OK')" 2>nul
if errorlevel 1 (
    echo Python packages: Some packages missing - check installation
) else (
    echo Python packages: OK
)

if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo Tesseract OCR: OK
) else (
    echo Tesseract OCR: NOT FOUND
)
echo.

REM Create model download info
echo Step 10: Creating model download guide...
(
echo # Model Download Guide
echo.
echo ## Required Models
echo.
echo ### 1. Vision Model ^(Moondream2 or LLaVA^)
echo Download from Hugging Face:
echo - Moondream2: https://huggingface.co/vikhyatk/moondream2
echo - LLaVA: https://huggingface.co/mys/ggml_llava-v1.5-7b
echo.
echo Save GGUF file to: models/vision/
echo Recommended: moondream2-q4.gguf ^(~2GB^)
echo.
echo ### 2. Whisper Model ^(STT^)
echo Download from:
echo https://huggingface.co/ggerganov/whisper.cpp
echo.
echo Recommended files:
echo - ggml-base.en.bin ^(~140MB, English only^)
echo - ggml-small.en.bin ^(~460MB, better accuracy^)
echo.
echo Save to: models/stt/
echo.
echo ### 3. Piper Voice ^(TTS^)
echo Download from:
echo https://github.com/rhasspy/piper/releases
echo.
echo Recommended voice:
echo - en_US-amy-low.onnx ^(~10MB^)
echo - en_US-lessac-medium.onnx ^(~20MB, better quality^)
echo.
echo Save to: models/tts/
echo.
echo ### 4. Optional: ONNX Models
echo - Spoon detector: Train custom or use YOLOv8-nano
echo - Depth estimation: MiDaS small
echo.
echo ## Quick Download Script
echo Run: python scripts/download_models.py
) > MODELS_DOWNLOAD_GUIDE.md
echo Model download guide created: MODELS_DOWNLOAD_GUIDE.md
echo.

echo ==========================================
echo Installation Complete!
echo ==========================================
echo.
echo IMPORTANT NEXT STEPS:
echo.
echo 1. Download required models:
echo    - See MODELS_DOWNLOAD_GUIDE.md for links
echo    - Or run: python scripts\download_models.py
echo.
echo 2. Install Tesseract OCR if not already installed:
echo    - Download from: https://github.com/UB-Mannheim/tesseract/wiki
echo.
echo 3. Download llama.cpp, whisper.cpp, and Piper binaries
echo    - See links above for Windows builds
echo.
echo 4. Test the installation:
echo    run_chef.bat --interactive
echo.
echo 5. Start cooking:
echo    run_chef.bat --recipe recipes\poha.json
echo.
echo For help: python chef_assistant.py --help
echo.
pause
