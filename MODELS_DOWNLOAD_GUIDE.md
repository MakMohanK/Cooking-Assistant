# Model Download Guide

## Required Models

### 1. Vision Model (Moondream2 or LLaVA)
Download from Hugging Face:
- Moondream2: https://huggingface.co/vikhyatk/moondream2
- LLaVA: https://huggingface.co/mys/ggml_llava-v1.5-7b

Save GGUF file to: models/vision/
Recommended: moondream2-q4.gguf (~2GB)

### 2. Whisper Model (STT)
Download from:
https://huggingface.co/ggerganov/whisper.cpp

Recommended files:
- ggml-base.en.bin (~140MB, English only)
- ggml-small.en.bin (~460MB, better accuracy)

Save to: models/stt/

### 3. Piper Voice (TTS)
Download from:
https://github.com/rhasspy/piper/releases

Recommended voice:
- en_US-amy-low.onnx (~10MB)
- en_US-lessac-medium.onnx (~20MB, better quality)

Save to: models/tts/

### 4. Optional: ONNX Models
- Spoon detector: Train custom or use YOLOv8-nano
- Depth estimation: MiDaS small

## Quick Download Script
Run: python scripts/download_models.py
