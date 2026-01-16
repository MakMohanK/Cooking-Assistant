# vision_vlm.py
"""
Vision Language Model (VLM) Wrapper
Interfaces with Moondream2 or LLaVA-Phi-3 via llama.cpp for offline vision analysis.
Returns structured JSON with ingredient recognition, quantity estimates, spatial info.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from PIL import Image
import io
import tempfile

logger = logging.getLogger(__name__)


class VisionVLM:
    """
    Wrapper for offline Vision Language Models (Moondream2 or LLaVA-Phi-3).
    Uses llama.cpp for efficient CPU inference on Raspberry Pi.
    """
    
    def __init__(
        self, 
        model_path: str,
        prompt_template: str = "moondream",
        max_tokens: int = 512,
        temperature: float = 0.2
    ):
        """
        Initialize VLM wrapper.
        
        Args:
            model_path: Path to GGUF model file
            prompt_template: Template type ("moondream" or "llava")
            max_tokens: Maximum tokens for response
            temperature: Sampling temperature (lower = more deterministic)
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        
        self.prompt_template = prompt_template
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Check if llama.cpp is available
        self.llama_cpp_path = self._find_llama_cpp()
        logger.info(f"Initialized VLM with model: {model_path}")
    
    def _find_llama_cpp(self) -> Optional[Path]:
        """Find llama.cpp executable (llava-cli or main)."""
        # Common paths to check
        possible_paths = [
            Path("./llama.cpp/llava-cli"),
            Path("./llama.cpp/build/bin/llava-cli"),
            Path("/usr/local/bin/llava-cli"),
            Path("./llama.cpp/main"),
            Path("./llama.cpp/build/bin/main")
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"Found llama.cpp at: {path}")
                return path
        
        logger.warning("llama.cpp not found - will use mock mode for testing")
        return None
    
    def analyze_frame(
        self, 
        image: np.ndarray, 
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a video frame and return structured ingredient data.
        
        Args:
            image: Image as numpy array (BGR format from OpenCV)
            prompt: Optional custom prompt (uses default if None)
        
        Returns:
            Structured JSON with recognized items, quantities, spatial info
        """
        if prompt is None:
            prompt = self._build_default_prompt()
        
        # Save image temporarily
        temp_image_path = Path(tempfile.gettempdir()) / "chef_frame.jpg"
        self._save_image(image, temp_image_path)
        
        # Run inference
        if self.llama_cpp_path:
            result = self._run_inference(temp_image_path, prompt)
        else:
            # Mock mode for testing without llama.cpp
            result = self._mock_inference(image, prompt)
        
        # Parse and structure the response
        structured_result = self._parse_response(result)
        
        return structured_result
    
    def _build_default_prompt(self) -> str:
        """Build the default structured prompt for ingredient analysis."""
        return """Analyze this cooking scene and provide a JSON response with:
1. recognized_items: List of ingredients/spices visible with:
   - name: ingredient name
   - confidence: 0-1 confidence score
   - bbox: [x, y, width, height] bounding box
   - estimated_quantity: {amount, unit, confidence, method}
2. containers: List of jars/bottles with type, color, label_text
3. tools: List of utensils (spoon/cup) with name, fill_ratio (0-1)
4. locations: Spatial relationships (left_of, right_of, front_of, behind)
5. uncertainties: List of items you're unsure about

Focus on common Indian cooking ingredients. Be specific about spices and quantities."""
    
    def _save_image(self, image: np.ndarray, path: Path):
        """Save numpy array as JPEG image."""
        # Convert BGR to RGB if needed
        if len(image.shape) == 3 and image.shape[2] == 3:
            image_rgb = image[:, :, ::-1]  # BGR to RGB
        else:
            image_rgb = image
        
        pil_image = Image.fromarray(image_rgb.astype(np.uint8))
        pil_image.save(path, "JPEG", quality=85)
    
    def _run_inference(self, image_path: Path, prompt: str) -> str:
        """Run inference using llama.cpp."""
        try:
            cmd = [
                str(self.llama_cpp_path),
                "-m", str(self.model_path),
                "--image", str(image_path),
                "-p", prompt,
                "-n", str(self.max_tokens),
                "--temp", str(self.temperature),
                "-ngl", "0",  # CPU only
                "--no-display-prompt"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Inference failed: {result.stderr}")
                return self._mock_response()
                
        except subprocess.TimeoutExpired:
            logger.error("Inference timeout")
            return self._mock_response()
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return self._mock_response()
    
    def _mock_inference(self, image: np.ndarray, prompt: str) -> str:
        """Mock inference for testing without actual model."""
        logger.info("Using mock inference (no model loaded)")
        return self._mock_response()
    
    def _mock_response(self) -> str:
        """Generate mock response for testing."""
        return json.dumps({
            "recognized_items": [
                {
                    "name": "turmeric",
                    "confidence": 0.82,
                    "bbox": [120, 150, 80, 60],
                    "estimated_quantity": {
                        "amount": 0.5,
                        "unit": "teaspoon",
                        "confidence": 0.75,
                        "method": "spoon_fill_ratio"
                    }
                }
            ],
            "containers": [
                {"type": "jar", "color": "yellow", "label_text": "Haldi"}
            ],
            "tools": [
                {"name": "teaspoon", "fill_ratio": 0.55}
            ],
            "locations": [
                {"item": "turmeric", "relation": "left_of", "reference": "stove"}
            ],
            "uncertainties": []
        })
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and ensure valid JSON structure."""
        try:
            # Try to parse as JSON directly
            data = json.loads(response)
            return self._validate_structure(data)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                try:
                    data = json.loads(json_str)
                    return self._validate_structure(data)
                except json.JSONDecodeError:
                    pass
            
            # Fallback: return empty structure
            logger.warning("Could not parse VLM response as JSON")
            return self._empty_structure()
    
    def _validate_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure the data has all required fields."""
        required_fields = {
            "recognized_items": [],
            "containers": [],
            "tools": [],
            "locations": [],
            "uncertainties": []
        }
        
        for field, default in required_fields.items():
            if field not in data:
                data[field] = default
        
        return data
    
    def _empty_structure(self) -> Dict[str, Any]:
        """Return empty but valid structure."""
        return {
            "recognized_items": [],
            "containers": [],
            "tools": [],
            "locations": [],
            "uncertainties": ["Could not analyze image"]
        }


def detect_spoons_opencv(image: np.ndarray) -> List[Dict[str, Any]]:
    """
    Detect spoons using basic OpenCV (fallback if no ONNX detector).
    Simple shape-based detection for measuring spoons.
    
    Args:
        image: Input image as numpy array
    
    Returns:
        List of detected spoons with bbox and fill_ratio estimates
    """
    # Placeholder implementation
    # In production, this would use cv2.findContours, shape matching, etc.
    logger.debug("Using basic spoon detection (OpenCV)")
    return []


def estimate_fill_ratio(spoon_region: np.ndarray) -> float:
    """
    Estimate fill ratio of a spoon from 0.0 (empty) to 1.0 (full/heaped).
    
    Args:
        spoon_region: Cropped image of spoon
    
    Returns:
        Fill ratio estimate (0.0 to 1.5 for heaped)
    """
    # Placeholder implementation
    # In production: segment bowl, compute area vs convex hull, detect heaping
    logger.debug("Estimating fill ratio")
    return 0.5  # Mock value
