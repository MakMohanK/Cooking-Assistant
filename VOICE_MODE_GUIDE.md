# 🎤 Voice Mode Guide - Continuous Voice Listening

## Overview

The Chef Assistant now supports **continuous voice listening mode** with Voice Activity Detection (VAD). This allows hands-free operation - just speak naturally and the assistant will listen, transcribe, and respond automatically.

---

## ✨ Features

### Continuous Listening
- Always listening in the background
- Automatic voice activity detection
- No need to press buttons or trigger keywords
- Processes commands as you speak

### Voice Activity Detection (VAD)
- Detects when you start speaking
- Automatically captures speech segments
- Filters out background noise
- Ends capture after silence period

### Smart Processing
- Queues speech for transcription
- Prevents command overlap
- Provides spoken feedback
- Handles errors gracefully

---

## 🚀 Quick Start

### 1. Install PyAudio (Required)

**Linux/Raspberry Pi:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Windows:**
```bash
pip install pyaudio
# Usually works without additional steps
```

### 2. Run Voice Mode

**Start with a recipe:**
```bash
./run_chef.sh --voice --recipe recipes/poha.json
```

**Start without a recipe (for testing):**
```bash
./run_chef.sh --voice
```

**Windows:**
```cmd
run_chef.bat --voice --recipe recipes\poha.json
```

### 3. Optional: Calibrate VAD

When starting voice mode, you'll be asked:
```
Calibrate voice detection? (y/n):
```

- Say **'y'** to calibrate (recommended first time)
- Remain silent for 3 seconds during calibration
- System will set optimal threshold for your environment

---

## 🎯 How It Works

### Voice Activity Detection Flow

```
Microphone → Audio Stream (100ms chunks)
              ↓
         VAD Analysis (RMS energy threshold)
              ↓
    Is Voice Detected? ─ NO → Continue listening
              │
             YES
              ↓
    Start capturing speech buffer
              ↓
    Continue until 1.5s of silence
              ↓
    Speech duration ≥ 0.5s? ─ NO → Discard
              │
             YES
              ↓
    Queue for transcription
              ↓
    Whisper.cpp transcription
              ↓
    Process command & speak response
```

### Parameters (Configurable)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `sample_rate` | 16000 Hz | Audio sample rate (whisper requirement) |
| `vad_threshold` | 0.02 | RMS energy threshold for voice detection |
| `silence_duration` | 1.5s | Silence to end speech segment |
| `min_speech_duration` | 0.5s | Minimum speech length to process |
| `chunk_size` | 100ms | Audio processing chunk size |

---

## 🗣️ Voice Commands

### During Voice Mode

Simply speak naturally:

| Say This | What Happens |
|----------|-------------|
| "Next step" | Proceed to next recipe instruction |
| "What is this?" | Identify ingredient in camera view |
| "How much?" | Check quantity of ingredient |
| "Repeat" | Hear last instruction again |
| "Help" | List available commands |
| "Stop" | End cooking session |

### Examples

**Good commands:**
- ✅ "Next step"
- ✅ "What is this"
- ✅ "How much do I have"
- ✅ "Repeat that"

**Avoid:**
- ❌ Very short utterances (< 0.5s)
- ❌ Talking while assistant is speaking
- ❌ Multiple commands in quick succession

---

## 🔧 Troubleshooting

### "PyAudio not installed" Error

**Symptoms:** Voice mode starts but shows mock mode messages

**Solution:**
```bash
# Linux/Raspberry Pi
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio

# Verify installation
python3 -c "import pyaudio; print('PyAudio OK')"
```

### Voice Not Detected

**Symptoms:** Speaking but no response

**Solutions:**
1. **Calibrate VAD:**
   - Restart with calibration option
   - Ensure quiet environment during calibration

2. **Check microphone:**
   ```bash
   # Linux - test microphone
   arecord -d 5 test.wav
   aplay test.wav
   ```

3. **Adjust threshold manually:**
   ```python
   # In code, increase sensitivity
   self.stt.set_vad_threshold(0.01)  # Lower = more sensitive
   ```

### False Triggers (Too Sensitive)

**Symptoms:** Background noise triggers recognition

**Solutions:**
1. **Calibrate in actual environment** (not in quiet room)
2. **Increase threshold:**
   ```python
   self.stt.set_vad_threshold(0.05)  # Higher = less sensitive
   ```
3. **Reduce background noise** (close windows, turn off fans)

### Slow Response Time

**Symptoms:** Long delay between speaking and response

**Solutions:**
1. **Use faster Whisper model:**
   ```bash
   export WHISPER_MODEL=./models/stt/ggml-tiny.en.bin
   ```

2. **Reduce silence duration:**
   ```python
   # In stt_whisper.py __init__
   silence_duration=1.0  # Faster end detection
   ```

3. **Check CPU load** on Raspberry Pi

### Commands Not Understood

**Symptoms:** "I didn't understand that" responses

**Solutions:**
1. **Speak clearly** and at normal pace
2. **Reduce background noise**
3. **Use exact command phrases** (see table above)
4. **Check transcription** in logs:
   ```bash
   tail -f logs/chef_assistant.log | grep "Transcription result"
   ```

---

## 🎛️ Advanced Configuration

### Custom VAD Threshold

Set via code or config:

```python
# In chef_assistant.py, after STT initialization
assistant.stt.set_vad_threshold(0.03)
```

### Silence Duration

Adjust how quickly speech ends:

```python
# In src/stt_whisper.py
WhisperSTT(
    model_path,
    silence_duration=1.0,  # Faster (default 1.5)
    min_speech_duration=0.3  # Shorter minimum (default 0.5)
)
```

### Continuous Loop Without PyAudio (Mock Mode)

For testing without microphone:

- Voice mode will auto-detect PyAudio absence
- Generates test commands every 5 seconds
- Useful for development/debugging

---

## 📊 Performance

### Raspberry Pi 4 (8GB)

| Operation | Latency | Notes |
|-----------|---------|-------|
| VAD detection | <10ms | Per 100ms chunk |
| Speech capture | 0.5-5s | Depends on speech length |
| Whisper transcription | 1-3s | With base model |
| Command processing | <500ms | Vision queries add 2-3s |
| TTS response | 0.5-1s | With low-latency voice |
| **Total round-trip** | **2-10s** | Depends on command type |

### Optimization Tips

1. **Use `ggml-tiny.en.bin`** for faster STT (less accurate)
2. **Enable swap** if memory constrained
3. **Close background apps** on Raspberry Pi
4. **Use low-latency Piper voices**

---

## 🔐 Privacy

### Voice Mode Privacy Features

✅ **Fully Offline:** No audio sent to cloud  
✅ **Local Processing:** All transcription on-device  
✅ **No Recording:** Audio not saved (temp files deleted)  
✅ **No Telemetry:** Zero data collection  

### What's Captured

- Audio is processed in **100ms chunks**
- Speech segments saved **temporarily** to `/tmp/chef_stt_temp.wav`
- File **overwritten** on each new command
- **No persistent storage** of audio

---

## 🧪 Testing Voice Mode

### Test Without Recipe

```bash
./run_chef.sh --voice
```

Then say:
1. "Help" - Should list commands
2. "What is this" - Should activate camera
3. "Stop" - Should exit

### Test With Recipe

```bash
./run_chef.sh --voice --recipe recipes/poha.json
```

Then say:
1. "Next step" - Should read first step
2. "Repeat" - Should repeat the step
3. "How much" - Should check quantity (if applicable)

### Check Logs

Monitor real-time activity:
```bash
tail -f logs/chef_assistant.log
```

Look for:
- "Speech started" / "Speech ended"
- "Transcription result: ..."
- "Processing command: ..."

---

## 🆚 Voice Mode vs Interactive Mode

| Feature | Voice Mode | Interactive Mode |
|---------|-----------|------------------|
| **Input** | Spoken commands | Typed commands |
| **Hands-free** | ✅ Yes | ❌ No (need keyboard) |
| **Always listening** | ✅ Yes | ❌ No |
| **Setup complexity** | Medium (PyAudio) | Low |
| **Latency** | 2-10s | <1s |
| **Accessibility** | ✅ Excellent | ⚠️ Limited |
| **Best for** | Actual cooking | Testing/debugging |

---

## 💡 Tips for Best Experience

### Do's ✅

- **Speak clearly** at normal pace
- **Wait for response** before next command
- **Use exact phrases** from command list
- **Calibrate VAD** in cooking environment
- **Keep microphone** 30-50cm away
- **Minimize background noise**

### Don'ts ❌

- Don't speak while assistant is talking
- Don't use very short utterances
- Don't calibrate in different environment
- Don't expect instant responses (2-10s is normal)
- Don't move microphone during session

---

## 🔄 Workflow Example

**Complete Voice Mode Cooking Session:**

```
1. Start:
   $ ./run_chef.sh --voice --recipe recipes/poha.json
   
2. Calibrate (optional):
   Calibrate voice detection? (y/n): y
   [Remain silent for 3 seconds]
   
3. Begin cooking:
   YOU: "Next step"
   ASSISTANT: "Step 1 of 8. Rinse 2 cups poha and drain."
   
4. Identify ingredient:
   YOU: "What is this"
   ASSISTANT: "Hold item steady... This looks like poha."
   
5. Check quantity:
   YOU: "How much"
   ASSISTANT: "I see approximately 2 cups. That matches the recipe perfectly!"
   
6. Continue:
   YOU: "Next step"
   ASSISTANT: "Step 2 of 8. Heat 2 teaspoons oil. Caution: hot oil."
   
7. End session:
   YOU: "Stop"
   ASSISTANT: "Ending session. You completed 2 of 8 steps. Goodbye!"
```

---

## 🐛 Known Limitations

1. **No keyword activation** - Always listening (can't say "Hey Chef")
2. **Single command at a time** - Can't queue multiple commands
3. **No interrupt** - Must wait for response to complete
4. **PyAudio required** - Mock mode available but limited
5. **English only** - Multi-language support planned

---

## 🚀 Future Enhancements

- [ ] Wake word detection ("Hey Chef")
- [ ] Interrupt/cancel current command
- [ ] Command queuing
- [ ] Multi-language voice commands
- [ ] webrtcvad integration (better VAD)
- [ ] Adaptive threshold adjustment
- [ ] Background noise cancellation

---

## 📞 Support

### Voice Mode Not Working?

1. Check PyAudio installation
2. Test microphone separately
3. Review logs for errors
4. Try calibration
5. Test in interactive mode first

### Need Help?

- See main README.md
- Check logs/chef_assistant.log
- Review troubleshooting section above

---

**Voice mode makes the Chef Assistant truly hands-free and accessible!** 🎤🍳
