#!/usr/bin/env bash
# Run script for Chef Assistant on Linux/Raspberry Pi OS

set -euo pipefail

# Activate virtual environment
if [ -d "chef_venv" ]; then
    source chef_venv/bin/activate
else
    echo "Error: Virtual environment not found. Run install_offline_linux.sh first."
    exit 1
fi

# Set environment variables for offline mode
export OFFLINE_MODE=1
export VISION_MODEL="${VISION_MODEL:-./models/vision/moondream2-q4.gguf}"
export WHISPER_MODEL="${WHISPER_MODEL:-./models/stt/ggml-base.en.bin}"
export PIPER_VOICE="${PIPER_VOICE:-./models/tts/en_US-amy-low.onnx}"
export OCR_LANGS="${OCR_LANGS:-eng+deva}"
export SPOON_DETECTOR_ONNX="${SPOON_DETECTOR_ONNX:-}"
export DEPTH_MODEL_ONNX="${DEPTH_MODEL_ONNX:-}"
export CALIB_FILE="${CALIB_FILE:-}"

# Ensure logs directory exists
mkdir -p logs

# Display startup message
echo "=========================================="
echo "Chef Assistant - Offline Cooking Helper"
echo "=========================================="
echo ""
echo "Models:"
echo "  Vision: $VISION_MODEL"
echo "  STT: $WHISPER_MODEL"
echo "  TTS: $PIPER_VOICE"
echo "  OCR: $OCR_LANGS"
echo ""

# Check if models exist
missing_models=0
if [ ! -f "$VISION_MODEL" ]; then
    echo "⚠️  Warning: Vision model not found: $VISION_MODEL"
    echo "   Run: python3 scripts/download_models.py"
    missing_models=1
fi

if [ ! -f "$WHISPER_MODEL" ]; then
    echo "⚠️  Warning: Whisper model not found: $WHISPER_MODEL"
    missing_models=1
fi

if [ ! -f "$PIPER_VOICE" ]; then
    echo "⚠️  Warning: Piper voice not found: $PIPER_VOICE"
    missing_models=1
fi

if [ $missing_models -eq 1 ]; then
    echo ""
    echo "Some models are missing. The system will run in mock mode."
    echo "Download models with: python3 scripts/download_models.py"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run the Chef Assistant
python3 chef_assistant.py "$@"

# Cleanup on exit
trap "echo 'Shutting down Chef Assistant...'" EXIT
