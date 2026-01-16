#!/usr/bin/env python3
"""
Model Download Script for Chef Assistant
Downloads required models from Hugging Face and other sources.
Ensures all models are placed in correct directories.
"""

import os
import sys
import urllib.request
import json
from pathlib import Path


def download_file(url, destination, description="File"):
    """Download a file with progress indicator."""
    print(f"\nDownloading {description}...")
    print(f"URL: {url}")
    print(f"Destination: {destination}")
    
    # Ensure destination directory exists
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                bar_length = 40
                filled = int(bar_length * percent / 100)
                bar = '=' * filled + '-' * (bar_length - filled)
                sys.stdout.write(f"\r[{bar}] {percent:.1f}% ({downloaded/1024/1024:.1f}MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, destination, progress_hook)
        print(f"\n✓ Downloaded successfully!")
        
        # Verify file was created
        if dest_path.exists():
            size_mb = dest_path.stat().st_size / (1024 * 1024)
            print(f"✓ File verified: {size_mb:.1f}MB")
            return True
        else:
            print(f"✗ Error: File not created at {destination}")
            return False
            
    except Exception as e:
        print(f"\n✗ Download failed: {e}")
        return False


def verify_directories():
    """Create all required model directories."""
    directories = [
        "models/vision",
        "models/stt",
        "models/tts",
        "models/detectors",
        "models/depth"
    ]
    
    print("\nVerifying directory structure...")
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    print()


def download_binaries_windows():
    """Download pre-built binaries for Windows."""
    print("\n" + "=" * 60)
    print("DOWNLOADING BINARIES (Windows)")
    print("=" * 60)
    print()
    
    binaries = {
        "piper": {
            "url": "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_windows_amd64.zip",
            "dest": "piper_windows.zip",
            "extract_to": "piper",
            "desc": "Piper TTS"
        }
    }
    
    choice = input("Download Windows binaries? (y/n): ").lower().strip()
    
    if choice == 'y':
        try:
            import zipfile
            
            for key, info in binaries.items():
                if Path(info['extract_to']).exists():
                    print(f"\n✓ {info['desc']}: Already exists, skipping")
                    continue
                
                # Download
                if download_file(info['url'], info['dest'], info['desc']):
                    # Extract
                    print(f"Extracting {info['desc']}...")
                    with zipfile.ZipFile(info['dest'], 'r') as zip_ref:
                        zip_ref.extractall(info['extract_to'])
                    
                    # Remove zip
                    Path(info['dest']).unlink()
                    print(f"✓ Extracted to {info['extract_to']}/")
        
        except ImportError:
            print("⚠ zipfile module not available, skipping binary downloads")
        except Exception as e:
            print(f"✗ Error downloading binaries: {e}")


def main():
    """Main download script."""
    print("=" * 60)
    print("Chef Assistant - Comprehensive Model Downloader")
    print("=" * 60)
    print()
    
    # Create model directories
    verify_directories()
    
    print("=" * 60)
    print("AVAILABLE DOWNLOADS")
    print("=" * 60)
    print()
    
    # All available models
    all_models = {
        # REQUIRED MODELS
        "whisper_base": {
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin",
            "dest": "models/stt/ggml-base.en.bin",
            "size": "~140MB",
            "desc": "Whisper Base English (STT)",
            "category": "REQUIRED",
            "required": True
        },
        "piper_voice": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx",
            "dest": "models/tts/en_US-amy-low.onnx",
            "size": "~10MB",
            "desc": "Piper Amy Voice (TTS)",
            "category": "REQUIRED",
            "required": True
        },
        "piper_config": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json",
            "dest": "models/tts/en_US-amy-low.onnx.json",
            "size": "~1KB",
            "desc": "Piper Voice Config",
            "category": "REQUIRED",
            "required": True
        },
        
        # OPTIONAL - FASTER STT
        "whisper_tiny": {
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin",
            "dest": "models/stt/ggml-tiny.en.bin",
            "size": "~75MB",
            "desc": "Whisper Tiny English (Faster STT)",
            "category": "OPTIONAL - Performance",
            "required": False
        },
        
        # OPTIONAL - BETTER ACCURACY STT
        "whisper_small": {
            "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin",
            "dest": "models/stt/ggml-small.en.bin",
            "size": "~460MB",
            "desc": "Whisper Small English (Better Accuracy)",
            "category": "OPTIONAL - Accuracy",
            "required": False
        },
        
        # OPTIONAL - ALTERNATIVE TTS VOICES
        "piper_lessac": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "dest": "models/tts/en_US-lessac-medium.onnx",
            "size": "~20MB",
            "desc": "Piper Lessac Voice (Better Quality TTS)",
            "category": "OPTIONAL - Quality",
            "required": False
        },
        "piper_lessac_config": {
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
            "dest": "models/tts/en_US-lessac-medium.onnx.json",
            "size": "~1KB",
            "desc": "Piper Lessac Voice Config",
            "category": "OPTIONAL - Quality",
            "required": False
        }
    }
    
    # Group by category
    categories = {}
    for key, info in all_models.items():
        cat = info["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((key, info))
    
    # Display all models
    for category, models in sorted(categories.items()):
        print(f"\n{category}:")
        print("-" * 60)
        for key, info in models:
            status = "[REQUIRED]" if info["required"] else "[OPTIONAL]"
            print(f"  {status} {info['desc']} ({info['size']})")
            print(f"      → {info['dest']}")
    
    print()
    print("=" * 60)
    
    # Download options
    print("\nDownload options:")
    print("  1. Download ALL models (required + optional) - ~700MB")
    print("  2. Download REQUIRED models only - ~150MB")
    print("  3. Download REQUIRED + Performance models (tiny whisper) - ~225MB")
    print("  4. Download REQUIRED + Quality models (small whisper + better voice) - ~600MB")
    print("  5. Custom selection")
    print("  6. Skip automatic downloads (manual only)")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    download_list = []
    
    if choice == "1":
        # Download all
        download_list = list(all_models.keys())
        print("\n✓ Will download ALL models")
    
    elif choice == "2":
        # Required only
        download_list = [k for k, v in all_models.items() if v["required"]]
        print("\n✓ Will download REQUIRED models only")
    
    elif choice == "3":
        # Required + performance
        download_list = [k for k, v in all_models.items() if v["required"]]
        download_list.append("whisper_tiny")
        print("\n✓ Will download REQUIRED + Performance models")
    
    elif choice == "4":
        # Required + quality
        download_list = [k for k, v in all_models.items() if v["required"]]
        download_list.extend(["whisper_small", "piper_lessac", "piper_lessac_config"])
        print("\n✓ Will download REQUIRED + Quality models")
    
    elif choice == "5":
        # Custom selection
        print("\nAvailable models:")
        for i, (key, info) in enumerate(all_models.items(), 1):
            print(f"  {i}. {info['desc']} ({info['size']})")
        
        selections = input("\nEnter numbers separated by commas (e.g., 1,2,3): ").strip()
        try:
            indices = [int(x.strip()) - 1 for x in selections.split(",")]
            keys = list(all_models.keys())
            download_list = [keys[i] for i in indices if 0 <= i < len(keys)]
            print(f"\n✓ Will download {len(download_list)} selected models")
        except:
            print("✗ Invalid selection, skipping downloads")
            download_list = []
    
    elif choice == "6":
        print("\n✓ Skipping automatic downloads")
        download_list = []
    
    else:
        print("✗ Invalid option, downloading required models only")
        download_list = [k for k, v in all_models.items() if v["required"]]
    
    # Download selected models
    if download_list:
        print()
        print("=" * 60)
        print("DOWNLOADING MODELS")
        print("=" * 60)
        
        success_count = 0
        failed = []
        skipped = []
        
        for key in download_list:
            info = all_models[key]
            dest_path = Path(info['dest'])
            
            # Check if already exists
            if dest_path.exists():
                size_mb = dest_path.stat().st_size / (1024 * 1024)
                print(f"\n✓ {info['desc']}: Already downloaded ({size_mb:.1f}MB)")
                print(f"  Location: {dest_path}")
                skipped.append(info['desc'])
                success_count += 1
                continue
            
            # Download
            if download_file(info['url'], str(dest_path), info['desc']):
                success_count += 1
            else:
                failed.append(info['desc'])
        
        print()
        print("=" * 60)
        print(f"DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"  Successful: {success_count}/{len(download_list)}")
        if skipped:
            print(f"  Skipped (already downloaded): {len(skipped)}")
        if failed:
            print(f"  Failed: {len(failed)}")
        
        if failed:
            print(f"\n⚠ Failed downloads:")
            for item in failed:
                print(f"  - {item}")
        print()
    
    # Download Windows binaries
    if sys.platform == "win32":
        download_binaries_windows()
    
    # Manual download instructions for large models
    print()
    print("=" * 60)
    print("MANUAL DOWNLOADS REQUIRED")
    print("=" * 60)
    print()
    print("The following models are too large for automatic download")
    print("or require special handling:\n")
    
    print("1. VISION MODEL - Moondream2 (REQUIRED)")
    print("   " + "-" * 56)
    print("   This is the main vision model for ingredient recognition.")
    print()
    print("   OPTION A: Moondream2 F16 (Recommended)")
    print("   URL: https://huggingface.co/vikhyatk/moondream2/resolve/main/moondream2-text-model-f16.gguf")
    print("   Size: ~2.7GB")
    print("   Quality: Best")
    print("   Save to: models/vision/moondream2-text-model-f16.gguf")
    print()
    print("   OPTION B: Moondream2 Q4 (Faster)")
    print("   URL: https://huggingface.co/vikhyatk/moondream2/resolve/main/moondream2-text-model-q4_k_m.gguf")
    print("   Size: ~1GB")
    print("   Quality: Good (quantized)")
    print("   Save to: models/vision/moondream2-q4.gguf")
    print()
    print("   Manual download steps:")
    print("   a) Visit: https://huggingface.co/vikhyatk/moondream2")
    print("   b) Click 'Files and versions' tab")
    print("   c) Download one of the GGUF files above")
    print("   d) Move to models/vision/ directory")
    print()
    
    print("2. ALTERNATIVE: LLaVA Vision Model (OPTIONAL)")
    print("   " + "-" * 56)
    print("   URL: https://huggingface.co/mys/ggml_llava-v1.5-7b/resolve/main/ggml-model-q4_k.gguf")
    print("   Size: ~3.5GB")
    print("   Save to: models/vision/llava-q4.gguf")
    print("   Note: Slower but more detailed vision understanding")
    print()
    
    print("3. REQUIRED BINARIES")
    print("   " + "-" * 56)
    print("   The following binaries must be downloaded separately:\n")
    print("   a) llama.cpp (for Vision LLM)")
    print("      URL: https://github.com/ggerganov/llama.cpp/releases")
    print("      Download: Latest Windows release ZIP")
    print("      Extract to: llama.cpp/ directory")
    print()
    print("   b) whisper.cpp (for Speech-to-Text)")
    print("      URL: https://github.com/ggerganov/whisper.cpp/releases")
    print("      Download: whisper-bin-x64.zip")
    print("      Extract to: whisper.cpp/ directory")
    print()
    print("   c) Piper TTS (for Text-to-Speech)")
    if sys.platform != "win32":
        print("      URL: https://github.com/rhasspy/piper/releases/tag/v1.2.0")
        print("      Download: piper_windows_amd64.zip (or appropriate version)")
        print("      Extract to: piper/ directory")
    else:
        print("      ✓ Can be auto-downloaded (see option above)")
    print()
    print("   d) Tesseract OCR")
    print("      URL: https://github.com/UB-Mannheim/tesseract/wiki")
    print("      Download: tesseract-ocr-w64-setup-v5.3.x.exe")
    print("      Install: Run installer with Admin rights")
    print("      Languages: Select English + Hindi during installation")
    print()
    
    print("=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    print()
    print("After downloading, verify all models are correctly placed:")
    print("  python scripts/verify_models.py")
    print()
    
    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Download the Vision Model manually (see instructions above)")
    print()
    print("2. Download required binaries (llama.cpp, whisper.cpp, piper, tesseract)")
    print()
    print("3. Verify installation:")
    print("   python scripts/verify_models.py")
    print()
    print("4. Test the system:")
    print("   python chef_assistant.py --interactive")
    print()
    print("5. Start cooking with voice:")
    print("   python chef_assistant.py --voice --recipe recipes/poha.json")
    print()
    print("For detailed setup instructions, see: README.md")
    print()


if __name__ == '__main__':
    main()