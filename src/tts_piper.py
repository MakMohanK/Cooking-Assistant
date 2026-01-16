# tts_piper.py
"""
Text-to-Speech Module using Piper
Offline TTS for voice output in the Chef Assistant.
Warm, calm, practical voice for accessibility.
"""

import logging
import subprocess
import wave
from pathlib import Path
from typing import Optional
import numpy as np
import tempfile

logger = logging.getLogger(__name__)


class PiperTTS:
    """
    Offline Text-to-Speech using Piper.
    Optimized for low-latency voice output on Raspberry Pi.
    """
    
    def __init__(
        self,
        model_path: str,
        speaker_id: int = 0,
        speed: float = 1.0,
        output_sample_rate: int = 22050
    ):
        """
        Initialize Piper TTS.
        
        Args:
            model_path: Path to Piper ONNX model file
            speaker_id: Speaker ID for multi-speaker models
            speed: Speech speed multiplier (0.5-2.0)
            output_sample_rate: Output audio sample rate
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            logger.warning(f"Piper model not found: {model_path}")
        
        self.speaker_id = speaker_id
        self.speed = speed
        self.output_sample_rate = output_sample_rate
        
        self.piper_path = self._find_piper()
        logger.info(f"Initialized Piper TTS with model: {model_path}")
    
    def _find_piper(self) -> Optional[Path]:
        """Find Piper executable."""
        possible_paths = [
            Path("./piper/piper"),
            Path("/usr/local/bin/piper"),
            Path("./models/tts/piper"),
            Path("./piper/build/piper")
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found Piper at: {path}")
                return path
        
        logger.warning("Piper not found - using mock mode")
        return None
    
    def speak(self, text: str, output_path: Optional[str] = None, blocking: bool = True) -> bool:
        """
        Convert text to speech and play/save audio.
        
        Args:
            text: Text to speak
            output_path: Optional path to save WAV file
            blocking: If True, wait for speech to complete
        
        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return False
        
        # Clean and prepare text for TTS
        text = self._prepare_text(text)
        logger.info(f"Speaking: '{text[:50]}...'")
        
        if self.piper_path:
            return self._run_piper(text, output_path, blocking)
        else:
            return self._mock_speak(text, output_path)
    
    def _prepare_text(self, text: str) -> str:
        """
        Prepare text for natural TTS output.
        - Break long sentences
        - Add pauses for clarity
        - Handle measurements and numbers
        """
        # Replace common cooking abbreviations
        replacements = {
            "tsp": "teaspoon",
            "tbsp": "tablespoon",
            "oz": "ounce",
            "lb": "pound",
            "°F": "degrees Fahrenheit",
            "°C": "degrees Celsius"
        }
        
        for abbr, full in replacements.items():
            text = text.replace(abbr, full)
        
        # Add slight pauses after periods for clarity
        text = text.replace(". ", "... ")
        
        return text.strip()
    
    def _run_piper(self, text: str, output_path: Optional[str], blocking: bool) -> bool:
        """Run Piper TTS inference."""
        try:
            # Determine output path
            if output_path is None:
                output_path = str(Path(tempfile.gettempdir()) / "chef_tts_output.wav")
            
            cmd = [
                str(self.piper_path),
                "--model", str(self.model_path),
                "--output_file", output_path,
                "--length_scale", str(1.0 / self.speed)
            ]
            
            # Add speaker ID if applicable
            if self.speaker_id > 0:
                cmd.extend(["--speaker", str(self.speaker_id)])
            
            # Run Piper
            result = subprocess.run(
                cmd,
                input=text,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Play audio if blocking mode
                if blocking:
                    self._play_audio(output_path)
                logger.info("TTS successful")
                return True
            else:
                logger.error(f"Piper failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Piper timeout")
            return False
        except Exception as e:
            logger.error(f"Piper error: {e}")
            return False
    
    def _play_audio(self, audio_path: str):
        """Play audio file using system audio player."""
        audio_path = Path(audio_path)
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return
        
        try:
            # Try different audio players (cross-platform)
            players = ["aplay", "paplay", "ffplay", "powershell -c (New-Object Media.SoundPlayer '%s').PlaySync()"]
            
            for player in players:
                try:
                    if player.startswith("powershell"):
                        # Windows PowerShell
                        cmd = player % audio_path
                        subprocess.run(cmd, shell=True, timeout=30)
                    else:
                        # Linux audio players
                        subprocess.run([player, str(audio_path)], timeout=30, stderr=subprocess.DEVNULL)
                    logger.info(f"Played audio with {player}")
                    return
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    continue
            
            logger.warning("No audio player found - audio file saved but not played")
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def _mock_speak(self, text: str, output_path: Optional[str]) -> bool:
        """Mock TTS for testing."""
        logger.info(f"[MOCK TTS] Would speak: '{text}'")
        
        # Create a silent audio file if output path specified
        if output_path:
            self._create_silent_wav(output_path, duration=1.0)
        
        return True
    
    def _create_silent_wav(self, output_path: str, duration: float = 1.0):
        """Create a silent WAV file for testing."""
        samples = int(self.output_sample_rate * duration)
        audio_data = np.zeros(samples, dtype=np.int16)
        
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.output_sample_rate)
            wav_file.writeframes(audio_data.tobytes())
    
    def speak_safety_warning(self, warning_type: str) -> bool:
        """
        Speak a safety warning with appropriate urgency.
        
        Args:
            warning_type: Type of warning ("hot", "knife", "steam", "pressure")
        
        Returns:
            True if successful
        """
        warnings = {
            "hot": "Caution! Hot surface ahead. Please be careful.",
            "knife": "Sharp knife in use. Please handle with care.",
            "steam": "Warning! Hot steam. Keep your face and hands back.",
            "pressure": "Pressure cooker warning! Do not open until pressure is fully released.",
            "oil": "Caution! Hot oil can splatter. Stand back while adding ingredients."
        }
        
        warning_text = warnings.get(warning_type, "Please exercise caution.")
        return self.speak(warning_text, blocking=True)
    
    def speak_step(self, step_text: str, step_number: int, total_steps: int) -> bool:
        """
        Speak a recipe step with context.
        
        Args:
            step_text: The step instruction
            step_number: Current step number (1-indexed)
            total_steps: Total number of steps
        
        Returns:
            True if successful
        """
        intro = f"Step {step_number} of {total_steps}. "
        full_text = intro + step_text
        return self.speak(full_text, blocking=True)
    
    def confirm_action(self, action: str) -> bool:
        """
        Request confirmation for an action.
        
        Args:
            action: Action to confirm
        
        Returns:
            True if successful
        """
        text = f"{action} Please say yes to confirm, or no to cancel."
        return self.speak(text, blocking=True)


def format_quantity_speech(amount: float, unit: str) -> str:
    """
    Format quantity for natural speech.
    
    Args:
        amount: Numeric amount
        unit: Unit name
    
    Returns:
        Natural language quantity string
    """
    # Handle fractions
    if amount == 0.25:
        return f"a quarter {unit}"
    elif amount == 0.5:
        return f"half a {unit}"
    elif amount == 0.75:
        return f"three quarters of a {unit}"
    elif amount == 1.0:
        return f"one {unit}"
    elif amount < 1.0:
        return f"{amount} {unit}"
    else:
        # Pluralize unit if needed
        unit_plural = unit if unit.endswith('s') else f"{unit}s"
        return f"{amount} {unit_plural}"
