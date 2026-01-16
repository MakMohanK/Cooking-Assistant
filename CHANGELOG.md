# Changelog

All notable changes to the Chef Assistant project will be documented in this file.

## [1.1.0] - 2024 - Continuous Voice Loop Implementation

### ✨ Added
- **Continuous Voice Listening Mode** - Hands-free operation with automatic voice detection
  - Always-on listening with Voice Activity Detection (VAD)
  - Automatic speech segment capture based on silence detection
  - Queued transcription processing to prevent command overlap
  - Configurable VAD threshold and silence duration
  - PyAudio integration for real-time audio capture
  - Mock mode for testing without microphone
  
- **Voice Mode Enhancements**
  - `start_voice_mode()` and `stop_voice_mode()` methods in orchestrator
  - `--voice` command-line flag for continuous voice mode
  - Voice command callback system for asynchronous processing
  - VAD calibration feature (`calibrate_vad()` method)
  - Dynamic threshold adjustment (`set_vad_threshold()`)
  
- **Audio Processing Loop**
  - Separate thread for audio capture (100ms chunks)
  - Separate thread for transcription processing
  - Thread-safe queue for speech segments
  - Minimum speech duration filter (0.5s default)
  - Silence detection (1.5s default)
  
- **Documentation**
  - `VOICE_MODE_GUIDE.md` - Comprehensive voice mode documentation
  - Voice mode sections in README.md
  - Troubleshooting guide for voice issues
  - Performance metrics for Raspberry Pi
  
- **Configuration**
  - `sample_rate` parameter (16000 Hz for Whisper)
  - `vad_threshold` parameter (0.02 default)
  - `silence_duration` parameter (1.5s default)
  - `min_speech_duration` parameter (0.5s default)

### 🔧 Changed
- Updated `src/stt_whisper.py` with continuous listening implementation
- Enhanced `chef_assistant.py` orchestrator with voice mode support
- Updated `requirements.txt` to include PyAudio as required dependency
- Modified `install_offline_linux.sh` to install portaudio19-dev
- Updated README.md with voice mode instructions and examples

### 🐛 Fixed
- Command processing now prevents concurrent execution
- Audio buffer management improved to prevent memory leaks
- Thread cleanup on exit ensures proper shutdown

### 📚 Documentation
- Added VOICE_MODE_GUIDE.md with complete usage instructions
- Updated README.md with voice mode quick start
- Added troubleshooting section for voice-specific issues
- Documented VAD calibration process
- Added performance benchmarks for Raspberry Pi

### 🧪 Testing
- Voice mode can be tested without PyAudio (mock mode)
- Generates test commands every 5 seconds in mock mode
- Logs show speech detection events for debugging

### ⚠️ Known Limitations
- PyAudio required for actual voice mode (mock mode available for testing)
- No wake word detection (always listening)
- Single command processing (no queue for multiple commands)
- English language only (multi-language planned)

---

## [1.0.0] - 2024 - Initial Release

### ✨ Added
- **Core Features**
  - Offline vision + voice cooking assistant
  - Ingredient recognition (30+ items)
  - Quantity detection (teaspoons, tablespoons, cups, grams)
  - Recipe adherence checking with tolerance bands
  - Deviation detection (major/minor) with correction suggestions
  - Safety warnings (hot surfaces, knives, steam, pressure cooker)
  - Accessibility features (spatial guidance, confidence levels)
  
- **Modules**
  - `chef_assistant.py` - Main orchestrator
  - `src/quantity_estimator.py` - Quantity detection with multi-source fusion
  - `src/recipe_validator.py` - Recipe adherence validation
  - `src/vision_vlm.py` - Vision LLM wrapper (Moondream2/LLaVA)
  - `src/stt_whisper.py` - Speech-to-text (whisper.cpp)
  - `src/tts_piper.py` - Text-to-speech (Piper)
  - `src/ocr_tesseract.py` - OCR (English + Devanagari)
  
- **Data & Knowledge**
  - `recipes/poha.json` - Sample Poha recipe
  - `recipes/dal_tadka.json` - Sample Dal Tadka recipe
  - `knowledge/spices.yaml` - Spice aliases, substitutions, tolerances
  
- **Installation & Setup**
  - `install_offline_linux.sh` - Linux/Raspberry Pi installer
  - `install_offline_windows.bat` - Windows installer
  - `run_chef.sh` - Linux run script
  - `run_chef.bat` - Windows run script
  - `scripts/download_models.py` - Model downloader
  - `scripts/calibrate.py` - Calibration tool
  
- **Testing**
  - `tests/test_quantity_estimator.py` - 20+ unit tests
  - `tests/test_recipe_validator.py` - 15+ unit tests
  - pytest integration
  
- **Documentation**
  - `README.md` - Main documentation
  - `QUICKSTART.md` - Quick start guide
  - `PROJECT_SUMMARY.md` - Complete project overview
  - `REQUIREMENTS_AUDIT.md` - Requirements compliance audit
  - `LICENSE` - MIT License

### 🎯 Features Implemented
- ✅ Offline operation (no internet required)
- ✅ Cross-platform (Windows + Raspberry Pi + Linux)
- ✅ Vision-based ingredient recognition
- ✅ OCR for labels (English + Devanagari)
- ✅ Quantity estimation (spoon fill ratio + OCR fusion)
- ✅ Recipe adherence checking
- ✅ Safety warnings and confirmations
- ✅ Interactive CLI mode
- ✅ Privacy-preserving (no telemetry)
- ✅ Comprehensive documentation
- ✅ Test coverage (35+ tests)

### 🔧 Technical Details
- **Python**: 3.8+ compatible
- **Models**: Moondream2/LLaVA (GGUF), Whisper (GGUF), Piper (ONNX)
- **Frameworks**: OpenCV, NumPy, Pillow, PyYAML
- **Tools**: llama.cpp, whisper.cpp, Piper, Tesseract OCR
- **Architecture**: Modular design with clear separation of concerns
- **Performance**: <3s vision queries, <1s TTS on Raspberry Pi 4

### 📊 Statistics
- **Total Lines of Code**: 4,000+
- **Modules**: 7 core modules
- **Tests**: 35+ unit tests
- **Recipes**: 2 complete sample recipes
- **Ingredients**: 30+ in knowledge base
- **Documentation**: 1,000+ lines

---

## Future Enhancements

### Planned Features
- [ ] Wake word detection ("Hey Chef")
- [ ] webrtcvad integration for better VAD
- [ ] Command interrupt/cancel functionality
- [ ] Multi-language voice commands (Hindi, Marathi)
- [ ] Custom ONNX spoon detector
- [ ] MiDaS depth estimation implementation
- [ ] Adaptive VAD threshold adjustment
- [ ] Background noise cancellation
- [ ] More recipes (50+ target)
- [ ] Shopping list generation
- [ ] Nutrition information
- [ ] Timer management

---

## Version History Summary

| Version | Date | Key Features | Status |
|---------|------|-------------|---------|
| 1.1.0 | 2024 | Continuous voice loop, VAD, hands-free operation | ✅ Current |
| 1.0.0 | 2024 | Initial release, core features, cross-platform | ✅ Released |

---

**For detailed requirements compliance, see REQUIREMENTS_AUDIT.md**
