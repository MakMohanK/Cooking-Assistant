#!/usr/bin/env python3
# chef_assistant.py
"""
Main Orchestrator for Offline Vision + Voice Chef Assistant
Coordinates all modules: Vision VLM, STT, TTS, OCR, Quantity Estimation, Recipe Validation
Designed for visually impaired users with voice-first UX and safety warnings.
"""

import os
import sys
import logging
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from quantity_estimator import QuantityEstimator, QuantityEstimate
from recipe_validator import RecipeValidator, Deviation
from vision_vlm import VisionVLM
from stt_whisper import WhisperSTT
from tts_piper import PiperTTS
from ocr_tesseract import TesseractOCR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/chef_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ChefAssistant:
    """
    Main orchestrator for the Chef Assistant system.
    Manages the complete workflow from voice input to vision analysis to voice output.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Chef Assistant with configuration.
        
        Args:
            config: Configuration dictionary with paths and settings
        """
        self.config = config
        logger.info("Initializing Chef Assistant...")
        
        # Initialize all modules
        self._init_modules()
        
        # Session state
        self.session = {
            'active': False,
            'recipe': None,
            'validator': None,
            'current_frame': None,
            'last_recognition': None,
            'voice_mode': False,
            'processing_command': False
        }
        
        logger.info("Chef Assistant initialized successfully")
    
    def _init_modules(self):
        """Initialize all component modules."""
        # Vision VLM
        vision_model = self.config.get('VISION_MODEL', './models/vision/moondream2-q4.gguf')
        self.vision = VisionVLM(vision_model)
        logger.info("Vision module initialized")
        
        # STT (Whisper)
        whisper_model = self.config.get('WHISPER_MODEL', './models/stt/ggml-base.en.bin')
        self.stt = WhisperSTT(whisper_model)
        logger.info("STT module initialized")
        
        # TTS (Piper)
        piper_voice = self.config.get('PIPER_VOICE', './models/tts/en_US-amy-low.onnx')
        self.tts = PiperTTS(piper_voice)
        logger.info("TTS module initialized")
        
        # OCR (Tesseract)
        ocr_langs = self.config.get('OCR_LANGS', 'eng+deva')
        self.ocr = TesseractOCR(ocr_langs)
        logger.info("OCR module initialized")
        
        # Quantity Estimator
        calib_file = self.config.get('CALIB_FILE')
        calib_data = self._load_calibration(calib_file) if calib_file else None
        self.quantity_estimator = QuantityEstimator(calib_data)
        logger.info("Quantity estimator initialized")
        
        # Camera (placeholder - will be initialized when needed)
        self.camera = None
    
    def _load_calibration(self, calib_file: str) -> Optional[Dict]:
        """Load calibration data from YAML file."""
        try:
            import yaml
            with open(calib_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Could not load calibration: {e}")
            return None
    
    def start_session(self, recipe_path: str):
        """
        Start a new cooking session with a recipe.
        
        Args:
            recipe_path: Path to recipe JSON file
        """
        logger.info(f"Starting session with recipe: {recipe_path}")
        
        # Load recipe
        try:
            with open(recipe_path, 'r') as f:
                recipe = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load recipe: {e}")
            self.tts.speak("Sorry, I couldn't load the recipe. Please check the file.")
            return
        
        # Initialize recipe validator
        self.session['recipe'] = recipe
        self.session['validator'] = RecipeValidator(recipe)
        self.session['active'] = True
        
        # Greet user and introduce recipe
        recipe_name = recipe.get('name', 'Unknown')
        serves = recipe.get('serves', 'unknown')
        total_steps = len(recipe.get('steps', []))
        
        greeting = (f"Hello! Let's cook {recipe_name} together. "
                   f"This recipe serves {serves} and has {total_steps} steps. "
                   f"I'll guide you through each step with safety reminders. "
                   f"Say 'next step' when you're ready to begin.")
        
        self.tts.speak(greeting)
        logger.info(f"Session started: {recipe_name}")
    
    def process_voice_command(self, command: str) -> str:
        """
        Process a voice command and return response.
        
        Args:
            command: Transcribed voice command
        
        Returns:
            Response text
        """
        # Prevent concurrent command processing
        if self.session.get('processing_command', False):
            logger.debug("Already processing a command, ignoring")
            return ""

        self.session['processing_command'] = True
        try:
            command = command.lower().strip()
            logger.info(f"Processing command: '{command}'")

            # Intent recognition (simple keyword matching)
            if any(kw in command for kw in ['next', 'continue', 'proceed']):
                response = self._handle_next_step()

            elif any(kw in command for kw in ['what', 'identify', 'recognize', 'see']):
                response = self._handle_identify_request(command)

            elif any(kw in command for kw in ['how much', 'quantity', 'measure']):
                response = self._handle_quantity_check()

            elif any(kw in command for kw in ['repeat', 'again', 'say again']):
                response = self._handle_repeat()

            elif any(kw in command for kw in ['help', 'what can']):
                response = self._handle_help()

            elif any(kw in command for kw in ['stop', 'exit', 'quit', 'end']):
                response = self._handle_stop()
            else:
                response = "I didn't understand that. Say 'help' for available commands."
            
            return response

        finally:
            self.session['processing_command'] = False

    def _handle_voice_callback(self, transcription: str):
        """
        Callback for continuous voice listening mode.

        Args:
            transcription: Transcribed text from STT
        """
        logger.info(f"Voice callback received: '{transcription}'")

        # Process the command
        response = self.process_voice_command(transcription)

        # Speak the response
        if response:
            self.tts.speak(response)

    def _handle_next_step(self) -> str:
        """Handle 'next step' command."""
        if not self.session['active']:
            return "No active cooking session. Please load a recipe first."
        
        validator = self.session['validator']
        current_step = validator.get_current_step()
        
        if current_step is None:
            return "Congratulations! You've completed all the steps. Enjoy your meal!"
        
        # Get step details
        instruction = current_step.get('instruction', '')
        safety_warnings = current_step.get('safety', [])
        check_ingredient = current_step.get('check')
        
        # Speak safety warnings first
        for warning in safety_warnings:
            self.tts.speak(warning)
            time.sleep(0.5)
        
        # Speak the instruction
        step_num = validator.session_state['current_step'] + 1
        total_steps = len(self.session['recipe'].get('steps', []))
        self.tts.speak_step(instruction, step_num, total_steps)
        
        # If this step requires checking an ingredient, prepare for validation
        if check_ingredient:
            self.tts.speak("Show me the ingredient when you're ready to add it.")
        
        # Advance step counter
        validator.advance_step()
        
        return instruction
    
    def _handle_identify_request(self, command: str) -> str:
        """Handle 'what is this' type requests."""
        self.tts.speak("Hold the item steady in front of the camera. Analyzing...")
        # Capture frame
        frame = self._capture_frame()
        if frame is None:
            return "Sorry, I couldn't access the camera."
        
        # Analyze with VLM
        vlm_result = self.vision.analyze_frame(frame)
        
        # Extract recognized items
        items = vlm_result.get('recognized_items', [])
        uncertainties = vlm_result.get('uncertainties', [])
        
        if not items:
            response = "I'm not sure what that is. Could you show me the label?"
            if uncertainties:
                response += f" {uncertainties[0]}"
            return response
        
        # Report the most confident item
        best_item = max(items, key=lambda x: x.get('confidence', 0))
        name = best_item.get('name', 'unknown')
        confidence = best_item.get('confidence', 0)
        
        if confidence > 0.7:
            response = f"This looks like {name}."
        else:
            response = f"This might be {name}, but I'm not very confident."
        
        # Check for quantity if present
        qty = best_item.get('estimated_quantity')
        if qty:
            response += f" I see about {qty['amount']} {qty['unit']}."
        
        # Store result for later reference
        self.session['last_recognition'] = vlm_result
        
        return response
    
    def _handle_quantity_check(self) -> str:
        """Handle quantity checking requests."""
        self.tts.speak("Hold the measuring spoon or cup steady. Checking quantity...")
        
        # Capture frame
        frame = self._capture_frame()
        if frame is None:
            return "Sorry, I couldn't access the camera."
        
        # Analyze with VLM
        vlm_result = self.vision.analyze_frame(frame)
        
        # Run OCR on the frame
        ocr_text = self.ocr.read_text(frame)
        
        # Estimate quantity
        qty_estimate = self.quantity_estimator.estimate_quantity(vlm_result, ocr_text)
        
        if qty_estimate:
            response = f"I see approximately {qty_estimate.amount} {qty_estimate.unit}."
            
            # If in active session, validate against recipe
            if self.session['active'] and self.session['validator']:
                validator = self.session['validator']
                current_step = validator.get_current_step()
                
                if current_step and current_step.get('check'):
                    # Get the ingredient being checked
                    ingredient = current_step['check'].get('ingredient', 'ingredient')
                    
                    # Create observed data
                    observed = {
                        'ingredient': ingredient,
                        'estimate': qty_estimate.to_dict()
                    }
                    
                    # Validate
                    deviation = validator.validate_step(current_step['check'], observed)
                    
                    if deviation:
                        if deviation.severity == 'major':
                            response += f" However, the recipe needs {deviation.expected_amount} {deviation.expected_unit}. "
                            response += deviation.suggestion
                        else:
                            response += " That's close enough to the recipe amount."
                    else:
                        response += " That matches the recipe perfectly!"
            
            return response
        else:
            return "I couldn't determine the quantity. Make sure the measuring tool is clearly visible."
    
    def _handle_repeat(self) -> str:
        """Handle repeat request."""
        if self.session['active']:
            validator = self.session['validator']
            current_idx = validator.session_state['current_step']
            if current_idx > 0:
                prev_step = self.session['recipe']['steps'][current_idx - 1]
                instruction = prev_step.get('instruction', 'No previous step')
                self.tts.speak(instruction)
                return instruction
        
        return "There's no previous step to repeat."
    
    def _handle_help(self) -> str:
        """Handle help request."""
        help_text = (
            "I can help you cook step by step. "
            "Say 'next step' to continue. "
            "Say 'what is this' to identify ingredients. "
            "Say 'how much' to check quantities. "
            "Say 'repeat' to hear the last step again. "
            "Say 'stop' to end the session."
        )
        self.tts.speak(help_text)
        return help_text
    
    def _handle_stop(self) -> str:
        """Handle stop/exit request."""
        if self.session['active']:
            summary = self.session['validator'].get_session_summary()
            response = (f"Ending session. You completed {summary['current_step']} of {summary['total_steps']} steps. "
                       f"Goodbye!")
            self.tts.speak(response)
            self.session['active'] = False

            # Stop voice listening if active
            if self.session.get('voice_mode', False):
                self.stop_voice_mode()

            return response
        else:
            return "No active session to stop."
    
    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture a frame from the camera."""
        try:
            import cv2
            
            # Initialize camera if needed
            if self.camera is None:
                self.camera = cv2.VideoCapture(0)
                time.sleep(1)  # Camera warm-up
            
            # Capture frame
            ret, frame = self.camera.read()
            if ret:
                self.session['current_frame'] = frame
                return frame
            else:
                logger.error("Failed to capture frame")
                return None
                
        except ImportError:
            logger.error("OpenCV not available")
            # Return mock frame for testing
            return np.zeros((480, 640, 3), dtype=np.uint8)
    
    def run_interactive(self):
        """Run in interactive CLI mode (for testing without voice)."""
        print("\n" + "="*60)
        print("CHEF ASSISTANT - Interactive Mode")
        print("="*60)
        print("\nAvailable commands:")
        print("  - 'start <recipe_file>' : Start cooking with a recipe")
        print("  - 'next' : Next step")
        print("  - 'what is this' : Identify ingredient")
        print("  - 'how much' : Check quantity")
        print("  - 'help' : Show help")
        print("  - 'stop' : End session")
        print("  - 'exit' : Quit program")
        print("\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'exit':
                    print("Goodbye!")
                    break
                
                # Handle start command
                if user_input.lower().startswith('start '):
                    recipe_file = user_input[6:].strip()
                    self.start_session(recipe_file)
                    continue
                
                # Process as voice command
                response = self.process_voice_command(user_input)
                print(f"\nAssistant: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")
    
    def start_voice_mode(self):
        """Start continuous voice listening mode."""
        if self.session.get('voice_mode', False):
            logger.warning("Voice mode already active")
            return

        logger.info("Starting voice mode...")
        self.session['voice_mode'] = True

        # Optional: Calibrate VAD
        calibrate = input("Calibrate voice detection? (y/n): ").lower().strip()
        if calibrate == 'y':
            print("Calibrating... please remain silent for 3 seconds...")
            threshold = self.stt.calibrate_vad(duration=3.0)
            self.stt.set_vad_threshold(threshold)
            print(f"VAD threshold set to: {threshold:.4f}")

        # Start listening with callback
        self.tts.speak("Voice mode activated. I'm listening for your commands.")
        self.stt.start_listening(callback=self._handle_voice_callback)

        print("\n" + "="*60)
        print("VOICE MODE ACTIVE - Listening for commands...")
        print("="*60)
        print("\nSay one of:")
        print("  - 'Next step' - Continue to next instruction")
        print("  - 'What is this' - Identify ingredient")
        print("  - 'How much' - Check quantity")
        print("  - 'Repeat' - Hear last instruction")
        print("  - 'Help' - List commands")
        print("  - 'Stop' - End session")
        print("\nPress Ctrl+C to exit voice mode")
        print("="*60)
        print()

        # Keep main thread alive
        try:
            while self.session.get('voice_mode', False):
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\nExiting voice mode...")
            self.stop_voice_mode()

    def stop_voice_mode(self):
        """Stop continuous voice listening mode."""
        if not self.session.get('voice_mode', False):
            return

        logger.info("Stopping voice mode...")
        self.stt.stop_listening()
        self.session['voice_mode'] = False
        self.tts.speak("Voice mode deactivated.")
        print("Voice mode stopped.")

    def cleanup(self):
        """Cleanup resources."""
        if self.camera is not None:
            self.camera.release()

        if self.session.get('voice_mode', False):
            self.stop_voice_mode()

        logger.info("Chef Assistant shutdown")


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables."""
    config = {
        'VISION_MODEL': os.getenv('VISION_MODEL', './models/vision/moondream2-q4.gguf'),
        'WHISPER_MODEL': os.getenv('WHISPER_MODEL', './models/stt/ggml-base.en.bin'),
        'PIPER_VOICE': os.getenv('PIPER_VOICE', './models/tts/en_US-amy-low.onnx'),
        'OCR_LANGS': os.getenv('OCR_LANGS', 'eng+deva'),
        'SPOON_DETECTOR_ONNX': os.getenv('SPOON_DETECTOR_ONNX'),
        'DEPTH_MODEL_ONNX': os.getenv('DEPTH_MODEL_ONNX'),
        'CALIB_FILE': os.getenv('CALIB_FILE'),
        'OFFLINE_MODE': os.getenv('OFFLINE_MODE', '1') == '1'
    }
    return config


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Chef Assistant - Offline Vision + Voice Cooking Assistant')
    parser.add_argument('--recipe', '-r', help='Recipe JSON file to start with')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive CLI mode')
    parser.add_argument('--voice', '-v', action='store_true', help='Run in continuous voice mode')

    args = parser.parse_args()
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    # Load configuration
    config = load_config()
    
    # Initialize Chef Assistant
    try:
        assistant = ChefAssistant(config)
        
        # Start with recipe if provided
        if args.recipe:
            assistant.start_session(args.recipe)
        
        # Run in appropriate mode
        if args.voice:
            # Voice mode - continuous listening
            assistant.start_voice_mode()
        elif args.interactive or not args.voice:
            # Interactive CLI mode
            assistant.run_interactive()
        
        # Cleanup
        assistant.cleanup()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
