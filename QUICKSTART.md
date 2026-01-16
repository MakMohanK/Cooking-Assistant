# 🚀 Chef Assistant - Quick Start Guide

Get up and running with the Chef Assistant in 5 minutes!

## Prerequisites

- **Raspberry Pi**: Pi 4/5 with 8GB RAM, or any Linux system
- **Windows**: Windows 10/11 with 8GB+ RAM
- **Python**: 3.8 or higher
- **Camera**: USB webcam
- **Audio**: Microphone and speakers

## Installation (5 minutes)

### For Linux/Raspberry Pi:

```bash
# 1. Clone or download the project
cd chef-assistant

# 2. Run installation script
chmod +x install_offline_linux.sh
./install_offline_linux.sh

# 3. Download models (follow prompts)
python3 scripts/download_models.py
```

### For Windows:

```cmd
REM 1. Open Command Prompt in project directory
cd chef-assistant

REM 2. Run installation script
install_offline_windows.bat

REM 3. Download models (follow prompts)
python scripts\download_models.py
```

## First Run (Interactive Mode)

Test the system without a recipe:

### Linux/Raspberry Pi:
```bash
./run_chef.sh --interactive
```

### Windows:
```cmd
run_chef.bat --interactive
```

**Try these commands:**
- `help` - See available commands
- `what is this` - Identify an ingredient (hold to camera)
- `how much` - Check quantity in a spoon
- `exit` - Quit

## Cooking with a Recipe

### Linux/Raspberry Pi:
```bash
./run_chef.sh --recipe recipes/poha.json
```

### Windows:
```cmd
run_chef.bat --recipe recipes\poha.json
```

**Voice commands during cooking:**
- "Next step" - Proceed to next instruction
- "What is this?" - Identify ingredient
- "How much?" - Check if quantity is correct
- "Repeat" - Hear last instruction again
- "Help" - List commands
- "Stop" - End session

## Sample Recipe Flow

1. **Start**: `./run_chef.sh --recipe recipes/poha.json`
2. **Listen**: Assistant introduces the recipe
3. **Say**: "Next step"
4. **Follow**: Assistant guides through each step
5. **Check**: Show ingredients to camera when prompted
6. **Verify**: Assistant checks quantities and warns if off
7. **Complete**: Enjoy your meal!

## Troubleshooting

### "Models not found"
```bash
# Download models manually
python scripts/download_models.py

# Or download Vision model from:
# https://huggingface.co/vikhyatk/moondream2
# Save to: models/vision/moondream2-q4.gguf
```

### "Camera not detected"
```bash
# Linux - Check camera
ls -l /dev/video*

# Test with Python
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### "No audio output"
```bash
# Linux - Test speakers
speaker-test -t wav -c 2

# Windows - Check volume and default audio device
```

### Performance issues (Raspberry Pi)
- Use smaller models (base.en for Whisper, Q4 for Vision)
- Reduce camera resolution in config
- Enable swap file: `sudo dphys-swapfile swapoff && sudo nano /etc/dphys-swapfile`
  - Set `CONF_SWAPSIZE=4096`
  - `sudo dphys-swapfile setup && sudo dphys-swapfile swapon`

## What's Happening Behind the Scenes?

1. **Camera** captures frames of ingredients/spoons
2. **Vision LLM** (Moondream2) identifies what's in view
3. **OCR** (Tesseract) reads labels and measuring marks
4. **Quantity Estimator** fuses vision + OCR to estimate amounts
5. **Recipe Validator** compares to recipe and suggests corrections
6. **TTS** (Piper) speaks instructions and feedback
7. **STT** (Whisper) listens to your voice commands

All processing happens **locally** - no internet needed!

## Next Steps

- **Calibrate** (optional): `python scripts/calibrate.py`
  - Improves quantity detection accuracy
  - Takes 5 minutes

- **Add recipes**: Create JSON files in `recipes/` folder
  - See `recipes/poha.json` for format

- **Customize**: Edit `config/default_config.yaml`
  - Adjust camera settings
  - Change model paths
  - Set language preferences

## Tips for Best Results

✅ **DO:**
- Use good lighting
- Position camera 30-50cm from workspace
- Show ingredients clearly to camera
- Use standard measuring spoons/cups
- Speak clearly for voice commands

❌ **DON'T:**
- Obstruct camera view
- Use non-standard measuring tools
- Rush through steps
- Skip safety warnings

## Safety Reminders

⚠️ The Chef Assistant provides **guidance only**:
- Always supervise cooking
- Follow safety warnings
- Verify critical measurements
- Use common sense
- Keep fire extinguisher nearby

## Need Help?

- 📖 Read full documentation: `README.md`
- 🧪 Run tests: `pytest tests/ -v`
- 🐛 Report issues: Open GitHub issue
- 📧 Ask questions: Check documentation first

---

**Happy Cooking! 🍳**
