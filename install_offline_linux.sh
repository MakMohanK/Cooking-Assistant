#!/usr/bin/env bash
# Installation script for Chef Assistant on Linux/Raspberry Pi OS
# This script sets up all dependencies for offline operation

set -e  # Exit on error

echo "=========================================="
echo "Chef Assistant - Linux Installation"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root. Run as regular user with sudo privileges."
    exit 1
fi

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)
echo "Detected: $OS $ARCH"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "Error: Python 3.8+ required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "Python version: $PYTHON_VERSION ✓"
echo ""

# Step 1: Install system dependencies
echo "Step 1: Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    curl \
    python3-pip \
    python3-venv \
    python3-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-hin \
    tesseract-ocr-mar \
    libtesseract-dev \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    alsa-utils \
    libopencv-dev

echo "System dependencies installed ✓"
echo ""

# Step 2: Create project directories
echo "Step 2: Creating project directories..."
mkdir -p models/vision
mkdir -p models/stt
mkdir -p models/tts
mkdir -p models/detectors
mkdir -p models/depth
mkdir -p config
mkdir -p logs
mkdir -p data/calibration
mkdir -p temp

echo "Directories created ✓"
echo ""

# Step 3: Create Python virtual environment
echo "Step 3: Creating Python virtual environment..."
python3 -m venv chef_venv
source chef_venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

echo "Virtual environment created ✓"
echo ""

# Step 4: Install Python dependencies
echo "Step 4: Installing Python dependencies..."
pip install -r requirements.txt

echo "Python dependencies installed ✓"
echo ""

# Step 4.5: Verify PyAudio installation (for voice mode)
echo "Step 4.5: Verifying PyAudio for voice mode..."
python3 -c "import pyaudio; print('PyAudio installed successfully ✓')" 2>/dev/null || {
    echo "⚠️  PyAudio installation failed. Voice mode will not work."
    echo "   This is usually due to missing portaudio19-dev"
    echo "   Try: sudo apt-get install portaudio19-dev python3-dev"
    echo "   Then: pip install pyaudio"
}
echo ""

# Step 5: Build llama.cpp for Vision LLM
echo "Step 5: Building llama.cpp for Vision LLM..."
if [ ! -d "llama.cpp" ]; then
    echo "Cloning llama.cpp repository..."
    git clone https://github.com/ggerganov/llama.cpp.git
    cd llama.cpp
    
    # Build with LLaVA support
    echo "Building llama.cpp (this may take several minutes)..."
    make clean
    make -j$(nproc) llava-cli
    
    cd ..
    echo "llama.cpp built ✓"
else
    echo "llama.cpp already exists, skipping build"
fi
echo ""

# Step 6: Build whisper.cpp for STT
echo "Step 6: Building whisper.cpp for STT..."
if [ ! -d "whisper.cpp" ]; then
    echo "Cloning whisper.cpp repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git
    cd whisper.cpp
    
    echo "Building whisper.cpp..."
    make clean
    make -j$(nproc)
    
    cd ..
    echo "whisper.cpp built ✓"
else
    echo "whisper.cpp already exists, skipping build"
fi
echo ""

# Step 7: Install Piper TTS
echo "Step 7: Installing Piper TTS..."
if [ ! -d "piper" ]; then
    mkdir -p piper
    cd piper
    
    # Download Piper binary based on architecture
    if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
        # Raspberry Pi ARM64
        echo "Downloading Piper for ARM64..."
        wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz
        tar -xzf piper_arm64.tar.gz
        rm piper_arm64.tar.gz
    elif [ "$ARCH" = "x86_64" ]; then
        # x86_64 Linux
        echo "Downloading Piper for x86_64..."
        wget -q https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz
        tar -xzf piper_amd64.tar.gz
        rm piper_amd64.tar.gz
    else
        echo "Warning: Unsupported architecture for Piper: $ARCH"
        echo "You may need to build Piper from source"
    fi
    
    cd ..
    echo "Piper installed ✓"
else
    echo "Piper already exists, skipping installation"
fi
echo ""

# Step 8: Create default configuration
echo "Step 8: Creating default configuration..."
cat > config/default_config.yaml << EOF
# Chef Assistant Configuration
offline_mode: true
log_level: INFO

# Model paths (update after downloading models)
vision_model: ./models/vision/moondream2-q4.gguf
whisper_model: ./models/stt/ggml-base.en.bin
piper_voice: ./models/tts/en_US-amy-low.onnx

# OCR settings
ocr_languages: eng+deva

# Camera settings
camera_index: 0
camera_resolution: [640, 480]
camera_fps: 2

# Audio settings (for voice mode)
sample_rate: 16000
vad_threshold: 0.02

# Optional models (uncomment if downloaded)
# spoon_detector: ./models/detectors/spoon_tiny.onnx
# depth_model: ./models/depth/midas_small.onnx

# Calibration (run calibration script to populate)
# calibration_file: ./config/calibration.yaml
EOF

echo "Default configuration created ✓"
echo ""

# Step 9: Make scripts executable
echo "Step 9: Making scripts executable..."
chmod +x run_chef.sh
chmod +x scripts/*.py 2>/dev/null || true

echo "Scripts made executable ✓"
echo ""

# Step 10: Test installations
echo "Step 10: Testing installations..."

# Test Python imports
python3 << EOF
try:
    import numpy
    import cv2
    import PIL
    import yaml
    print("Python packages: ✓")
except ImportError as e:
    print(f"Python package test failed: {e}")
    exit(1)
EOF

# Test PyAudio
python3 << EOF
try:
    import pyaudio
    print("PyAudio (voice mode): ✓")
except ImportError:
    print("PyAudio (voice mode): ✗ (voice mode will not work)")
EOF

# Test Tesseract
if command -v tesseract &> /dev/null; then
    echo "Tesseract OCR: ✓"
else
    echo "Tesseract OCR: ✗ (not found)"
fi

# Test llama.cpp
if [ -f "llama.cpp/llava-cli" ]; then
    echo "llama.cpp: ✓"
else
    echo "llama.cpp: ✗ (not built)"
fi

# Test whisper.cpp
if [ -f "whisper.cpp/main" ]; then
    echo "whisper.cpp: ✓"
else
    echo "whisper.cpp: ✗ (not built)"
fi

# Test Piper
if [ -f "piper/piper" ]; then
    echo "Piper TTS: ✓"
else
    echo "Piper TTS: ✗ (not installed)"
fi

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Download required models:"
echo "   python3 scripts/download_models.py"
echo ""
echo "2. (Optional) Run calibration:"
echo "   python3 scripts/calibrate.py"
echo ""
echo "3. Start the Chef Assistant:"
echo ""
echo "   INTERACTIVE MODE (keyboard input):"
echo "   ./run_chef.sh --interactive"
echo ""
echo "   VOICE MODE (hands-free with microphone):"
echo "   ./run_chef.sh --voice --recipe recipes/poha.json"
echo ""
echo "   For voice mode help, see: VOICE_MODE_GUIDE.md"
echo ""
echo "For troubleshooting, check:"
echo "   - README.md"
echo "   - VOICE_MODE_GUIDE.md"
echo "   - logs/chef_assistant.log"
echo ""