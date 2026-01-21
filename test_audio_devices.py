#!/usr/bin/env python3
"""Test script to list available audio input devices."""

import sys

try:
    import pyaudio
    
    print("=" * 60)
    print("Audio Device Information")
    print("=" * 60)
    
    audio = pyaudio.PyAudio()
    
    # Get default input device
    try:
        default_input = audio.get_default_input_device_info()
        print(f"\nDefault Input Device:")
        print(f"  Index: {default_input['index']}")
        print(f"  Name: {default_input['name']}")
        print(f"  Channels: {default_input['maxInputChannels']}")
        print(f"  Sample Rate: {int(default_input['defaultSampleRate'])} Hz")
    except Exception as e:
        print(f"\n[WARNING] No default input device found: {e}")
    
    # List all input devices
    print(f"\nAll Available Input Devices:")
    print("-" * 60)
    
    device_count = audio.get_device_count()
    input_devices = []
    
    for i in range(device_count):
        device_info = audio.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_devices.append(device_info)
            print(f"\nDevice {i}:")
            print(f"  Name: {device_info['name']}")
            print(f"  Channels: {device_info['maxInputChannels']}")
            print(f"  Sample Rate: {int(device_info['defaultSampleRate'])} Hz")
    
    audio.terminate()
    
    if len(input_devices) == 0:
        print("\n[ERROR] No input devices found!")
        print("\nTroubleshooting:")
        print("  1. Check that a microphone is connected")
        print("  2. Check Windows Sound Settings > Input devices")
        print("  3. Ensure microphone is enabled and not muted")
        print("  4. Try restarting your computer")
        print("\n[INFO] Voice mode will run in MOCK/DEMO mode without a microphone")
    else:
        print(f"\n[SUCCESS] Found {len(input_devices)} input device(s)")
        print("\nYou can now run the Chef Assistant in voice mode!")
    
except ImportError:
    print("[ERROR] PyAudio not installed!")
    print("\nInstall with: pip install pyaudio")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)