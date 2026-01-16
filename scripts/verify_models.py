#!/usr/bin/env python3
"""
Model Verification Script for Chef Assistant
Checks if all required models are downloaded and placed correctly.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def check_file_exists(filepath: Path, min_size_mb: float = 0) -> Tuple[bool, str]:
    """
    Check if a file exists and meets minimum size requirement.
    
    Args:
        filepath: Path to file
        min_size_mb: Minimum size in MB
    
    Returns:
        (exists_and_valid, message)
    """
    if not filepath.exists():
        return False, f"{Colors.RED}✗ NOT FOUND{Colors.END}"
    
    size_mb = filepath.stat().st_size / (1024 * 1024)
    
    if size_mb < min_size_mb:
        return False, f"{Colors.YELLOW}⚠ Found but too small ({size_mb:.1f}MB < {min_size_mb}MB){Colors.END}"
    
    return True, f"{Colors.GREEN}✓ Found ({size_mb:.1f}MB){Colors.END}"


def verify_models() -> Dict[str, bool]:
    """
    Verify all required models are present.
    
    Returns:
        Dictionary of model categories and their status
    """
    print(f"\n{Colors.BOLD}{'='*60}")
    print("Chef Assistant - Model Verification")
    print(f"{'='*60}{Colors.END}\n")
    
    results = {}
    
    # Define required models
    models = {
        "Vision Models (VLM)": [
            {
                "name": "Moondream2 (GGUF)",
                "paths": [
                    "models/vision/moondream2-q4.gguf",
                    "models/vision/moondream2-text-model-f16.gguf",
                    "models/vision/moondream2.gguf"
                ],
                "min_size_mb": 100,
                "required": True,
                "download_url": "https://huggingface.co/vikhyatk/moondream2"
            },
            {
                "name": "LLaVA (Alternative)",
                "paths": [
                    "models/vision/llava-q4.gguf",
                    "models/vision/ggml-model-q4_k.gguf"
                ],
                "min_size_mb": 500,
                "required": False,
                "download_url": "https://huggingface.co/mys/ggml_llava-v1.5-7b"
            }
        ],
        "Speech-to-Text (STT)": [
            {
                "name": "Whisper Base English",
                "paths": ["models/stt/ggml-base.en.bin"],
                "min_size_mb": 100,
                "required": True,
                "download_url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.en.bin"
            },
            {
                "name": "Whisper Small English (Better accuracy)",
                "paths": ["models/stt/ggml-small.en.bin"],
                "min_size_mb": 400,
                "required": False,
                "download_url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin"
            },
            {
                "name": "Whisper Tiny English (Faster)",
                "paths": ["models/stt/ggml-tiny.en.bin"],
                "min_size_mb": 50,
                "required": False,
                "download_url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin"
            }
        ],
        "Text-to-Speech (TTS)": [
            {
                "name": "Piper Amy Voice (Low)",
                "paths": ["models/tts/en_US-amy-low.onnx"],
                "min_size_mb": 5,
                "required": True,
                "download_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx"
            },
            {
                "name": "Piper Amy Voice Config",
                "paths": ["models/tts/en_US-amy-low.onnx.json"],
                "min_size_mb": 0.001,
                "required": True,
                "download_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/low/en_US-amy-low.onnx.json"
            }
        ],
        "Optional Models": [
            {
                "name": "Spoon Detector (ONNX)",
                "paths": ["models/detectors/spoon_tiny.onnx"],
                "min_size_mb": 1,
                "required": False,
                "download_url": "Train custom or use YOLOv8-nano"
            },
            {
                "name": "MiDaS Depth (Small)",
                "paths": ["models/depth/midas_small.onnx"],
                "min_size_mb": 5,
                "required": False,
                "download_url": "https://github.com/isl-org/MiDaS"
            }
        ]
    }
    
    # Check each category
    for category, model_list in models.items():
        print(f"\n{Colors.BOLD}{Colors.BLUE}{category}:{Colors.END}")
        print("-" * 60)
        
        category_ok = False
        
        for model in model_list:
            found = False
            status_msg = ""
            
            # Check all possible paths for this model
            for path_str in model["paths"]:
                path = Path(path_str)
                exists, msg = check_file_exists(path, model["min_size_mb"])
                
                if exists:
                    found = True
                    status_msg = msg
                    break
            
            # Display result
            required_str = f"{Colors.RED}[REQUIRED]{Colors.END}" if model["required"] else "[OPTIONAL]"
            print(f"  {model['name']}: {required_str}")
            
            if found:
                print(f"    Status: {status_msg}")
                print(f"    Path: {path}")
                if model["required"]:
                    category_ok = True
            else:
                print(f"    Status: {Colors.RED}✗ NOT FOUND{Colors.END}")
                print(f"    Expected: {model['paths'][0]}")
                if model["required"]:
                    print(f"    {Colors.YELLOW}Download: {model['download_url']}{Colors.END}")
            
            print()
        
        # Store category result
        results[category] = category_ok or not any(m["required"] for m in model_list)
    
    return results


def print_summary(results: Dict[str, bool]):
    """Print verification summary."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}{Colors.END}\n")
    
    all_ok = all(results.values())
    
    for category, status in results.items():
        status_str = f"{Colors.GREEN}✓ OK{Colors.END}" if status else f"{Colors.RED}✗ MISSING{Colors.END}"
        print(f"  {category}: {status_str}")
    
    print()
    
    if all_ok:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All required models are present!{Colors.END}")
        print("\nYou can now run the Chef Assistant:")
        print("  ./run_chef.sh --interactive")
        print("  ./run_chef.sh --voice --recipe recipes/poha.json")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some required models are missing!{Colors.END}")
        print("\nPlease download missing models:")
        print("  python scripts/download_models.py")
        print("\nOr see the download instructions above.")
    
    print()


def check_directories():
    """Check if model directories exist."""
    print(f"\n{Colors.BOLD}Checking directory structure...{Colors.END}")
    
    required_dirs = [
        "models/vision",
        "models/stt",
        "models/tts",
        "models/detectors",
        "models/depth"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  {Colors.GREEN}✓{Colors.END} {dir_path}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} {dir_path} - Creating...")
            path.mkdir(parents=True, exist_ok=True)
            all_exist = False
    
    if all_exist:
        print(f"\n{Colors.GREEN}All directories exist.{Colors.END}")
    else:
        print(f"\n{Colors.YELLOW}Created missing directories.{Colors.END}")


def check_binaries():
    """Check if required binaries are installed."""
    print(f"\n{Colors.BOLD}Checking required binaries...{Colors.END}\n")
    
    binaries = {
        "llama.cpp/llava-cli": "Vision LLM inference",
        "whisper.cpp/main": "Speech-to-text",
        "piper/piper": "Text-to-speech",
        "tesseract": "OCR (system binary)"
    }
    
    for binary, description in binaries.items():
        if '/' in binary:
            # File path
            path = Path(binary)
            if path.exists():
                print(f"  {Colors.GREEN}✓{Colors.END} {description}: {binary}")
            else:
                print(f"  {Colors.RED}✗{Colors.END} {description}: {binary} not found")
        else:
            # System command
            import shutil
            if shutil.which(binary):
                print(f"  {Colors.GREEN}✓{Colors.END} {description}: {binary}")
            else:
                print(f"  {Colors.YELLOW}⚠{Colors.END} {description}: {binary} not in PATH")


def main():
    """Main verification function."""
    # Check directories
    check_directories()
    
    # Verify models
    results = verify_models()
    
    # Check binaries
    check_binaries()
    
    # Print summary
    print_summary(results)
    
    # Return exit code
    sys.exit(0 if all(results.values()) else 1)


if __name__ == '__main__':
    main()
