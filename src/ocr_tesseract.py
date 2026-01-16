# ocr_tesseract.py
"""
OCR Module using Tesseract
Reads labels and measuring marks in English and Devanagari (Hindi/Marathi).
Extracts ingredient names and quantity markings from containers and measuring tools.
"""

import logging
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class TesseractOCR:
    """
    Offline OCR using Tesseract with multi-language support.
    Optimized for reading ingredient labels and measuring marks.
    """
    
    def __init__(self, languages: str = "eng+deva"):
        """
        Initialize Tesseract OCR.
        
        Args:
            languages: Language codes separated by + (e.g., "eng+deva" for English and Devanagari)
        """
        self.languages = languages
        self.tesseract_path = self._find_tesseract()
        
        if not self.tesseract_path:
            logger.warning("Tesseract not found - OCR will be limited")
        
        logger.info(f"Initialized Tesseract OCR with languages: {languages}")
    
    def _find_tesseract(self) -> Optional[str]:
        """Find Tesseract executable."""
        try:
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                logger.info("Found Tesseract")
                return "tesseract"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        # Try Windows path
        windows_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if Path(windows_path).exists():
            logger.info(f"Found Tesseract at: {windows_path}")
            return windows_path
        
        return None
    
    def read_text(self, image: np.ndarray, preprocess: bool = True) -> str:
        """
        Extract text from image.
        
        Args:
            image: Image as numpy array (BGR format)
            preprocess: Whether to preprocess image for better OCR
        
        Returns:
            Extracted text
        """
        if self.tesseract_path is None:
            return self._mock_ocr(image)
        
        # Preprocess if requested
        if preprocess:
            image = self._preprocess_image(image)
        
        # Save to temp file
        temp_path = Path("/tmp/chef_ocr_temp.png")
        self._save_image(image, temp_path)
        
        # Run Tesseract
        text = self._run_tesseract(temp_path)
        
        return text
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results.
        - Convert to grayscale
        - Increase contrast
        - Denoise
        """
        try:
            import cv2
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply adaptive thresholding
            processed = cv2.adaptiveThreshold(
                gray,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Denoise
            processed = cv2.fastNlMeansDenoising(processed, h=10)
            
            return processed
            
        except ImportError:
            logger.warning("OpenCV not available for preprocessing")
            return image
    
    def _save_image(self, image: np.ndarray, path: Path):
        """Save numpy array as image file."""
        pil_image = Image.fromarray(image)
        pil_image.save(path)
    
    def _run_tesseract(self, image_path: Path) -> str:
        """Run Tesseract OCR."""
        try:
            cmd = [
                self.tesseract_path,
                str(image_path),
                "stdout",
                "-l", self.languages,
                "--psm", "6",  # Assume uniform block of text
                "--oem", "1"   # Use LSTM neural nets
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                text = result.stdout.strip()
                logger.debug(f"OCR result: '{text}'")
                return text
            else:
                logger.error(f"Tesseract failed: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            logger.error("Tesseract timeout")
            return ""
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return ""
    
    def _mock_ocr(self, image: np.ndarray) -> str:
        """Mock OCR for testing."""
        logger.debug("Using mock OCR")
        return "Haldi (Turmeric) 100g"
    
    def extract_measurements(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract measurement quantities from OCR text.
        
        Args:
            text: OCR text containing measurements
        
        Returns:
            List of detected measurements with amount and unit
        """
        measurements = []
        
        # Pattern for common measurements
        patterns = [
            # Fractions with units: 1/2 tsp, ½ tbsp, etc.
            (r'(\d+/\d+|½|¼|¾|⅓|⅔)\s*(tsp|tbsp|cup|oz|lb|g|kg|ml|l)', 'fraction_unit'),
            # Decimals with units: 0.5 tsp, 2.5 cups
            (r'(\d+\.?\d*)\s*(tsp|tbsp|cup|oz|lb|g|kg|ml|l)', 'decimal_unit'),
            # Whole numbers with units: 1 tsp, 2 cups
            (r'(\d+)\s*(teaspoon|tablespoon|cup|ounce|pound|gram|kilogram)', 'word_unit'),
            # Weight markings: 100g, 250ml
            (r'(\d+)\s*(g|kg|ml|l)\b', 'metric')
        ]
        
        for pattern, pattern_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1)
                unit = match.group(2).lower()
                
                # Convert fraction to decimal
                amount = self._parse_amount(amount_str)
                
                # Normalize unit
                unit = self._normalize_unit(unit)
                
                measurements.append({
                    'amount': amount,
                    'unit': unit,
                    'raw_text': match.group(0),
                    'confidence': 0.9 if pattern_type in ['fraction_unit', 'decimal_unit'] else 0.7
                })
        
        return measurements
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float (handles fractions)."""
        # Unicode fractions
        fraction_map = {
            '½': 0.5, '¼': 0.25, '¾': 0.75,
            '⅓': 0.333, '⅔': 0.667,
            '⅛': 0.125, '⅜': 0.375, '⅝': 0.625, '⅞': 0.875
        }
        
        if amount_str in fraction_map:
            return fraction_map[amount_str]
        
        # Regular fractions like 1/2, 3/4
        if '/' in amount_str:
            parts = amount_str.split('/')
            if len(parts) == 2:
                try:
                    return float(parts[0]) / float(parts[1])
                except (ValueError, ZeroDivisionError):
                    return 1.0
        
        # Regular decimal
        try:
            return float(amount_str)
        except ValueError:
            return 1.0
    
    def _normalize_unit(self, unit: str) -> str:
        """Normalize unit names to standard forms."""
        unit_map = {
            'tsp': 'teaspoon',
            'tbsp': 'tablespoon',
            'oz': 'ounce',
            'lb': 'pound',
            'g': 'grams',
            'kg': 'kilograms',
            'ml': 'milliliters',
            'l': 'liters'
        }
        
        return unit_map.get(unit.lower(), unit.lower())
    
    def detect_ingredient_names(self, text: str) -> List[str]:
        """
        Detect ingredient names from OCR text.
        
        Args:
            text: OCR text
        
        Returns:
            List of detected ingredient names
        """
        # Common ingredient keywords
        ingredients = []
        
        # English ingredients
        english_ingredients = [
            'turmeric', 'haldi', 'cumin', 'jeera', 'coriander', 'dhania',
            'chili', 'mirch', 'salt', 'namak', 'sugar', 'chini',
            'mustard', 'rai', 'pepper', 'garam masala', 'oil', 'tel'
        ]
        
        text_lower = text.lower()
        for ingredient in english_ingredients:
            if ingredient in text_lower:
                ingredients.append(ingredient)
        
        return ingredients


def extract_label_info(ocr_text: str) -> Dict[str, Any]:
    """
    Extract structured information from ingredient label.
    
    Args:
        ocr_text: OCR text from label
    
    Returns:
        Dictionary with ingredient name, brand, quantity, expiry, etc.
    """
    info = {
        'ingredient_names': [],
        'brand': None,
        'quantity': None,
        'expiry_date': None,
        'batch_number': None
    }
    
    # Extract measurements
    ocr = TesseractOCR()
    measurements = ocr.extract_measurements(ocr_text)
    if measurements:
        info['quantity'] = measurements[0]
    
    # Extract ingredient names
    info['ingredient_names'] = ocr.detect_ingredient_names(ocr_text)
    
    # Extract expiry date (common patterns)
    expiry_patterns = [
        r'exp[iry]*\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{2,4})',
        r'best\s*before\s*:?\s*(\d{2}[/-]\d{2}[/-]\d{2,4})'
    ]
    
    for pattern in expiry_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            info['expiry_date'] = match.group(1)
            break
    
    return info
