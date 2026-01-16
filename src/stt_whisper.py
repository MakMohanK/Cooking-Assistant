# stt_whisper.py
"""
Speech-to-Text Module using Whisper.cpp
Offline voice recognition with Voice Activity Detection (VAD) for the Chef Assistant.
"""

import logging
import subprocess
import wave
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, Callable
import threading
import queue
import time
import tempfile

logger = logging.getLogger(__name__)


class WhisperSTT:
    """
    Offline Speech-to-Text using whisper.cpp with VAD.
    Optimized for Raspberry Pi CPU-only inference.
    """
    
    def __init__(
        self,
        model_path: str,
        sample_rate: int = 16000,
        vad_threshold: float = 0.02,
        language: str = "en",
        silence_duration: float = 1.5,
        min_speech_duration: float = 0.5
    ):
        """
        Initialize Whisper STT.
        
        Args:
            model_path: Path to whisper GGML model file
            sample_rate: Audio sample rate (whisper expects 16kHz)
            vad_threshold: Voice activity detection threshold (RMS energy)
            language: Language code ("en", "hi", "mr")
            silence_duration: Seconds of silence to end speech segment
            min_speech_duration: Minimum speech duration to process
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Whisper model not found: {model_path}")
        
        self.sample_rate = sample_rate
        self.vad_threshold = vad_threshold
        self.language = language
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        
        self.whisper_cpp_path = self._find_whisper_cpp()
        self.is_recording = False
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.result_callback = None
        
        # Audio buffering for continuous listening
        self.audio_buffer = []
        self.speech_buffer = []
        self.is_speech_active = False
        self.silence_counter = 0
        self.speech_start_time = 0
        
        logger.info(f"Initialized Whisper STT with model: {model_path}")
    
    def _find_whisper_cpp(self) -> Optional[Path]:
        """Find whisper.cpp executable."""
        possible_paths = [
            Path("./whisper.cpp/main"),
            Path("./whisper.cpp/build/bin/main"),
            Path("/usr/local/bin/whisper-cpp"),
            Path("./models/stt/whisper-cpp")
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found whisper.cpp at: {path}")
                return path
        
        logger.warning("whisper.cpp not found - using mock mode")
        return None
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to WAV audio file (16kHz, mono)
        
        Returns:
            Transcribed text
        """
        audio_path = Path(audio_path)
        if not audio_path.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return ""
        
        if self.whisper_cpp_path:
            return self._run_whisper(audio_path)
        else:
            return self._mock_transcribe(audio_path)
    
    def _run_whisper(self, audio_path: Path) -> str:
        """Run whisper.cpp inference."""
        try:
            cmd = [
                str(self.whisper_cpp_path),
                "-m", str(self.model_path),
                "-f", str(audio_path),
                "-l", self.language,
                "-nt",  # No timestamps
                "-np",  # No progress
                "--output-txt"  # Text output only
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Extract transcribed text from output
                text = self._parse_whisper_output(result.stdout)
                logger.info(f"Transcribed: '{text}'")
                return text
            else:
                logger.error(f"Whisper failed: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            logger.error("Whisper timeout")
            return ""
        except Exception as e:
            logger.error(f"Whisper error: {e}")
            return ""
    
    def _parse_whisper_output(self, output: str) -> str:
        """Parse whisper output to extract clean text."""
        # Remove timestamps and formatting
        lines = output.strip().split('\n')
        text_lines = [line for line in lines if line and not line.startswith('[')]
        return ' '.join(text_lines).strip()
    
    def _mock_transcribe(self, audio_path: Path) -> str:
        """Mock transcription for testing."""
        logger.info(f"Mock transcribing: {audio_path}")
        # Simulate some processing time
        time.sleep(0.5)
        return "What's in the spoon?"
    
    def detect_voice_activity(self, audio_data: np.ndarray) -> bool:
        """
        Voice activity detection using RMS energy threshold.
        
        Args:
            audio_data: Audio samples as numpy array (float32, -1.0 to 1.0)
        
        Returns:
            True if voice detected, False otherwise
        """
        if len(audio_data) == 0:
            return False
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Simple threshold-based VAD
        return rms > self.vad_threshold
    
    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """
        Start continuous listening mode with VAD (non-blocking).
        
        Args:
            callback: Function to call with transcription results callback(text: str)
        """
        if self.is_listening:
            logger.warning("Already listening")
            return
        
        self.is_listening = True
        self.result_callback = callback
        
        # Start audio capture thread
        self.capture_thread = threading.Thread(
            target=self._audio_capture_loop,
            daemon=True
        )
        self.capture_thread.start()
        
        # Start processing thread
        self.process_thread = threading.Thread(
            target=self._audio_process_loop,
            daemon=True
        )
        self.process_thread.start()
        
        logger.info("Started continuous listening with VAD")
    
    def stop_listening(self):
        """Stop continuous listening mode."""
        self.is_listening = False
        self.is_recording = False
        logger.info("Stopped listening")
    
    def _audio_capture_loop(self):
        """
        Main audio capture loop (runs in separate thread).
        Captures audio from microphone and performs VAD.
        """
        try:
            import pyaudio
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open audio stream
            chunk_size = int(self.sample_rate * 0.1)  # 100ms chunks
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            logger.info("Audio stream opened, listening for voice...")
            
            silence_chunks = int(self.silence_duration / 0.1)  # Number of chunks for silence duration
            speech_chunks = int(self.min_speech_duration / 0.1)  # Minimum speech chunks
            
            while self.is_listening:
                try:
                    # Read audio chunk
                    data = stream.read(chunk_size, exception_on_overflow=False)
                    audio_chunk = np.frombuffer(data, dtype=np.float32)
                    
                    # Detect voice activity
                    is_voice = self.detect_voice_activity(audio_chunk)
                    
                    if is_voice:
                        if not self.is_speech_active:
                            # Speech started
                            self.is_speech_active = True
                            self.speech_start_time = time.time()
                            self.speech_buffer = []
                            logger.debug("Speech started")
                        
                        # Add to speech buffer
                        self.speech_buffer.append(audio_chunk)
                        self.silence_counter = 0
                    else:
                        if self.is_speech_active:
                            # Potential silence during speech
                            self.silence_counter += 1
                            self.speech_buffer.append(audio_chunk)  # Keep capturing
                            
                            # Check if silence duration exceeded
                            if self.silence_counter >= silence_chunks:
                                # Speech ended
                                speech_duration = time.time() - self.speech_start_time
                                
                                # Check if speech was long enough
                                if speech_duration >= self.min_speech_duration:
                                    # Queue for transcription
                                    speech_audio = np.concatenate(self.speech_buffer)
                                    self.audio_queue.put(speech_audio)
                                    logger.debug(f"Speech ended (duration: {speech_duration:.2f}s), queued for transcription")
                                else:
                                    logger.debug(f"Speech too short ({speech_duration:.2f}s), ignored")
                                
                                # Reset
                                self.is_speech_active = False
                                self.speech_buffer = []
                                self.silence_counter = 0
                
                except Exception as e:
                    logger.error(f"Error reading audio: {e}")
                    time.sleep(0.1)
            
            # Cleanup
            stream.stop_stream()
            stream.close()
            audio.terminate()
            logger.info("Audio stream closed")
            
        except ImportError:
            logger.error("PyAudio not installed. Install with: pip install pyaudio")
            logger.info("Running in mock mode - generating periodic test transcriptions")
            
            # Mock mode: generate test transcriptions periodically
            test_commands = [
                "What is this?",
                "How much?",
                "Next step",
                "Repeat",
                "Help"
            ]
            cmd_index = 0
            
            while self.is_listening:
                time.sleep(5)  # Wait 5 seconds between mock commands
                if self.is_listening:
                    mock_audio = np.random.randn(self.sample_rate * 2).astype(np.float32) * 0.1
                    self.audio_queue.put(mock_audio)
                    logger.info(f"[MOCK] Generated test command: {test_commands[cmd_index]}")
                    cmd_index = (cmd_index + 1) % len(test_commands)
        
        except Exception as e:
            logger.error(f"Fatal error in audio capture loop: {e}")
    
    def _audio_process_loop(self):
        """
        Audio processing loop (runs in separate thread).
        Takes audio from queue, transcribes, and calls callback.
        """
        logger.info("Audio processing loop started")
        
        while self.is_listening:
            try:
                # Get audio from queue (with timeout to allow loop exit)
                try:
                    audio_data = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Save to temporary file
                temp_wav = Path(tempfile.gettempdir()) / "chef_stt_temp.wav"
                save_audio_wav(audio_data, str(temp_wav), self.sample_rate)
                
                # Transcribe
                logger.debug("Transcribing speech segment...")
                text = self.transcribe_audio(str(temp_wav))
                
                if text and text.strip():
                    logger.info(f"Transcription result: '{text}'")
                    
                    # Call callback if provided
                    if self.result_callback:
                        try:
                            self.result_callback(text)
                        except Exception as e:
                            logger.error(f"Error in transcription callback: {e}")
                else:
                    logger.debug("Transcription empty or failed")
                
                # Mark task as done
                self.audio_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.1)
        
        logger.info("Audio processing loop stopped")
    
    def set_vad_threshold(self, threshold: float):
        """
        Adjust VAD threshold dynamically.
        
        Args:
            threshold: New RMS threshold (0.01-0.1 typical range)
        """
        self.vad_threshold = threshold
        logger.info(f"VAD threshold set to: {threshold}")
    
    def calibrate_vad(self, duration: float = 3.0) -> float:
        """
        Calibrate VAD threshold by measuring ambient noise.
        
        Args:
            duration: Calibration duration in seconds
        
        Returns:
            Recommended threshold value
        """
        logger.info(f"Calibrating VAD for {duration} seconds...")
        logger.info("Please remain silent...")
        
        try:
            import pyaudio
            
            audio = pyaudio.PyAudio()
            chunk_size = int(self.sample_rate * 0.1)
            stream = audio.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=chunk_size
            )
            
            noise_levels = []
            num_chunks = int(duration / 0.1)
            
            for _ in range(num_chunks):
                data = stream.read(chunk_size, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.float32)
                rms = np.sqrt(np.mean(audio_chunk ** 2))
                noise_levels.append(rms)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Calculate threshold as mean + 3 * std dev
            mean_noise = np.mean(noise_levels)
            std_noise = np.std(noise_levels)
            recommended_threshold = mean_noise + (3 * std_noise)
            
            logger.info(f"Ambient noise level: {mean_noise:.4f} ± {std_noise:.4f}")
            logger.info(f"Recommended VAD threshold: {recommended_threshold:.4f}")
            
            return recommended_threshold
            
        except ImportError:
            logger.error("PyAudio not installed. Using default threshold.")
            return self.vad_threshold
        except Exception as e:
            logger.error(f"VAD calibration failed: {e}")
            return self.vad_threshold


def save_audio_wav(audio_data: np.ndarray, filename: str, sample_rate: int = 16000):
    """
    Save audio data as WAV file.
    
    Args:
        audio_data: Audio samples (float32 or int16)
        filename: Output filename
        sample_rate: Sample rate in Hz
    """
    # Normalize to int16
    if audio_data.dtype == np.float32 or audio_data.dtype == np.float64:
        # Clip to [-1, 1] and convert to int16
        audio_data = np.clip(audio_data, -1.0, 1.0)
        audio_data = (audio_data * 32767).astype(np.int16)
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())