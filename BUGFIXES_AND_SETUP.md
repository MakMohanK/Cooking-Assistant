# Bug Fixes and Setup Guide for Chef Assistant

## Critical Issues Identified

### 1. **Disk Space Issue (CRITICAL)**
- **Problem**: C: drive has only ~63MB free, cannot install opencv-python (39MB)
- **Solution**: Use temp directory or install to E: drive

### 2. **Missing Dependencies**
- **Missing**: opencv-python, pyaudio
- **Status**: Cannot install due to disk space

### 3. **Path Issues (Windows)**
- **Problem**: Code uses Linux paths like `/tmp/` which don't work on Windows
- **Files Affected**: 
  - `src/vision_vlm.py` (line 88: `/tmp/chef_frame.jpg`)
  - `src/stt_whisper.py` (line 277: `/tmp/chef_stt_temp.wav`)
  - `src/tts_piper.py` (line 110: `/tmp/chef_tts_output.wav`)

### 4. **Missing Model Files**
- Vision model (moondream2) not downloaded
- Whisper STT model not downloaded  
- Piper TTS model not downloaded
- llama.cpp, whisper.cpp, piper binaries not installed

### 5. **FileNotFoundError on Model Initialization**
- Models will fail to load if paths don't exist
- Need graceful fallback to mock mode

## Comprehensive Fix Script

The following script will:
1. Work around disk space issues
2. Fix Windows path compatibility
3. Download required models
4. Create proper directory structure
5. Enable mock mode for testing without models

## Next Steps

1. Apply path fixes for Windows compatibility
2. Download models to E: drive (has space)
3. Create symlinks or update config to use E: drive paths
4. Test in mock mode first
5. Download binaries separately

## Bug Priority

**P0 (Blocking):**
- Disk space issue
- Path compatibility (Windows)

**P1 (Required for functionality):**
- Missing models
- Missing binaries

**P2 (Nice to have):**
- Placeholder implementations (depth estimation)
- Advanced VAD (webrtcvad)
