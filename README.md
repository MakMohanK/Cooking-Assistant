# 🍳 Offline Vision + Voice Chef Assistant

A privacy-preserving, offline cooking assistant designed for visually impaired users. Runs entirely on Raspberry Pi (or Windows) with **no internet connection** required during operation. Features **continuous voice listening** for truly hands-free cooking.

## 🎯 Key Features

- **🎤 Continuous Voice Mode** - Hands-free operation with automatic voice detection (NEW!)
- **👁️ Live Ingredient Recognition** - Identify spices and ingredients with spatial guidance
- **📏 Quantity Detection** - Detect teaspoons, tablespoons, cups, grams using visual analysis
- **✅ Recipe Adherence** - Track what's added, compare against recipe, suggest corrections
- **🔊 Voice-First UX** - Offline speech-to-text and text-to-speech
- **⚠️ Safety Warnings** - Alerts for hot surfaces, knives, steam, and dangerous steps
- **🔒 Strictly Offline** - All models and data on device, zero telemetry
- **🖥️ Cross-Platform** - Works on Raspberry Pi OS, Linux, and Windows

## 🌟 What Makes This Special

### Truly Hands-Free Cooking
Unlike traditional voice assistants that require wake words or button presses, our **Continuous Voice Loop** is always listening. Just speak naturally:

```
YOU: "Next step"
ASSISTANT: "Step 2 of 8. Heat 2 teaspoons oil. Caution: hot oil."

YOU: "What is this?"
ASSISTANT: "Hold the item steady... This looks like turmeric, about half a teaspoon."

YOU: "How much do I need?"
ASSISTANT: "Recipe needs a quarter teaspoon. Shall I guide you to remove some?"
```

No wake words. No buttons. Just cooking.

### Privacy-First Design
- ✅ **100% offline** - No internet required during cooking
- ✅ **Zero telemetry** - No data collection or tracking
- ✅ **Local processing** - All AI runs on your device
- ✅ **Temporary audio** - Voice data never saved permanently

### Accessible by Design
- ♿ **Built for visually impaired users** - Voice-first interface
- 🗣️ **Natural language** - Warm, calm, practical instructions
- 🔁 **Repetition on demand** - "Repeat" command anytime
- 📍 **Spatial guidance** - "Left of stove", "front right"
- ⚠️ **Safety confirmations** - Extra warnings for dangerous steps

---

## 📋 Hardware Requirements

### Raspberry Pi (Recommended for Production)
- **Board**: Raspberry Pi 4/5 with 8GB RAM
- **Storage**: 128GB+ SD card
- **Camera**: USB webcam (640x480 minimum)
- **Microphone**: USB or 3.5mm omnidirectional mic
- **Audio Output**: HDMI, 3.5mm, or USB speakers
- **Optional**: Cooling fan

### Windows PC (Development/Testing)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Camera**: Built-in or USB webcam
- **Microphone**: Built-in or external
- **Audio**: Any speakers or headphones

---

## 🚀 Quick Start

### Step 1: Installation

#### Raspberry Pi OS / Linux
```bash
chmod +x install_offline_linux.sh
./install_offline_linux.sh
```

#### Windows
```cmd
install_offline_windows.bat
```

### Step 2: Download Models

```bash
python scripts/download_models.py
```

**Manual Vision Model Download:**
- Visit: https://huggingface.co/vikhyatk/moondream2
- Download: `moondream2-text-model-f16.gguf` (or Q4 quantized)
- Save to: `models/vision/moondream2-q4.gguf`

### Step 3: Run

#### 🎤 Voice Mode (Hands-Free)

```bash
# Linux/Raspberry Pi
./run_chef.sh --voice --recipe recipes/poha.json

# Windows
run_chef.bat --voice --recipe recipes\poha.json
```

#### ⌨️ Interactive Mode (Testing)

```bash
./run_chef.sh --interactive
```

---

## 🎤 Voice Commands

Just speak naturally:

- **"Next step"** - Proceed to next instruction
- **"What is this?"** - Identify ingredient
- **"How much?"** - Check quantity
- **"Repeat"** - Hear last instruction again
- **"Help"** - List available commands
- **"Stop"** - End cooking session

---

## 📖 Usage Example

```
ASSISTANT: "Hello! Let's cook Poha together. Say 'next step' when ready."

YOU: "Next step"
ASSISTANT: "Step 1 of 8. Rinse 2 cups poha and drain."

YOU: "What is this?"
ASSISTANT: "Hold the item steady... This looks like poha."

YOU: "How much?"
ASSISTANT: "I see approximately 2 cups. That matches the recipe perfectly!"
```

---

## 🔧 Configuration

Edit `config/default_config.yaml`:

```yaml
vision_model: ./models/vision/moondream2-q4.gguf
whisper_model: ./models/stt/ggml-base.en.bin
piper_voice: ./models/tts/en_US-amy-low.onnx
ocr_languages: eng+deva
sample_rate: 16000
vad_threshold: 0.02
```

---

## 🛠️ Troubleshooting

### Voice Not Detected

```bash
# Calibrate VAD when starting voice mode
./run_chef.sh --voice
# Say 'y' when asked to calibrate

# Test microphone
arecord -d 5 test.wav && aplay test.wav  # Linux
```

### PyAudio Not Installed

```bash
# Linux/Raspberry Pi
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```

### Performance Issues (Raspberry Pi)

- Use smaller models (ggml-tiny.en.bin for STT)
- Enable 4GB swap file
- Reduce camera resolution

See [VOICE_MODE_GUIDE.md](VOICE_MODE_GUIDE.md) for detailed troubleshooting.

---

## 📚 Documentation

- **[VOICE_MODE_GUIDE.md](VOICE_MODE_GUIDE.md)** - Complete voice mode documentation
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Technical overview
- **[REQUIREMENTS_AUDIT.md](REQUIREMENTS_AUDIT.md)** - Compliance status
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

---

## 📁 Project Structure

```
chef-assistant/
├── chef_assistant.py          # Main orchestrator with voice loop
├── src/
│   ├── quantity_estimator.py  # Quantity detection
│   ├── recipe_validator.py    # Recipe adherence
│   ├── vision_vlm.py          # Vision LLM wrapper
│   ├── stt_whisper.py         # Speech-to-text with continuous listening
│   ├── tts_piper.py           # Text-to-speech
│   └── ocr_tesseract.py       # OCR for labels
├── recipes/
│   ├── poha.json              # Sample: Poha
│   └── dal_tadka.json         # Sample: Dal Tadka
├── knowledge/
│   └── spices.yaml            # Spice knowledge base
├── models/                    # Model files (download separately)
├── scripts/
│   ├── download_models.py     # Model downloader
│   └── calibrate.py           # Calibration tool
└── tests/                     # Test suite (35+ tests)
```

---

## 🔒 Privacy & Offline Operation

- **No internet required** during cooking
- **No telemetry** or data collection
- All processing happens **locally**
- **Voice data never saved** permanently
- Logs stored only on local filesystem

---

## ⚠️ Safety Features

- Warns about hot surfaces, knives, steam
- Confirms dangerous actions before proceeding
- Allows pause and repetition of steps
- Uses clear spatial language

---

## 📏 Calibration (Optional)

```bash
python scripts/calibrate.py
```

Calibrates:
1. Camera scale (pixels to cm)
2. Measuring spoon dimensions
3. Voice Activity Detection threshold

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 🌍 Localization

Currently supports:
- **English** (primary)
- **Hindi/Marathi** (OCR for Devanagari labels)

---

## 📚 Adding Custom Recipes

Create JSON file in `recipes/` directory:

```json
{
  "name": "Your Recipe",
  "serves": 2,
  "ingredients": [
    {
      "ingredient": "turmeric",
      "amount": 0.5,
      "unit": "teaspoon"
    }
  ],
  "steps": [
    {
      "instruction": "Add turmeric and mix",
      "safety": ["Caution: hot pan"],
      "check": {
        "ingredient": "turmeric",
        "amount": 0.5,
        "unit": "teaspoon"
      }
    }
  ]
}
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Wake word detection
- Multi-language support
- More recipes
- Custom spoon detector
- Performance optimizations

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [llama.cpp](https://github.com/ggerganov/llama.cpp) - Vision LLM inference
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) - Speech recognition
- [Piper](https://github.com/rhasspy/piper) - Text-to-speech
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR
- [Moondream2](https://huggingface.co/vikhyatk/moondream2) - Vision model
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) - Audio I/O

---

## 🆕 What's New - Version 1.1

### Continuous Voice Loop (NEW!)
- ✅ Hands-free operation with automatic voice detection
- ✅ Always-listening mode with VAD
- ✅ No button presses required
- ✅ Speech segment capture and queuing
- ✅ Configurable VAD calibration
- ✅ Full PyAudio integration

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

---

## 🎯 Project Status

**Current Version:** 1.1.0  
**Status:** ✅ **Production Ready**  
**Requirements Met:** 98% (all core features complete)

---

## 📞 Support

- Open an issue on GitHub
- Check documentation
- Review troubleshooting section
- See [VOICE_MODE_GUIDE.md](VOICE_MODE_GUIDE.md)

---

**Made with ❤️ for accessible cooking**

*Empowering visually impaired users to cook independently with confidence.*
