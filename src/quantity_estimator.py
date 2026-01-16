# quantity_estimator.py
"""
Quantity Estimator Module
Fuses spoon/container detections, fill ratios, OCR marks, and optional depth
to produce quantity estimates for cooking ingredients.
"""

from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class QuantityEstimate:
    """Represents an estimated quantity with confidence and method."""
    amount: float  # numeric amount
    unit: str  # "teaspoon", "tablespoon", "cup", "grams", "pinch"
    confidence: float  # 0..1
    method: str  # "spoon_fill_ratio" | "ocr_mark" | "depth_volume" | "heuristic"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.amount} {self.unit} (confidence: {self.confidence:.2f}, method: {self.method})"


class QuantityEstimator:
    """Estimates ingredient quantities from vision data."""
    
    def __init__(self, calibration_data: Optional[Dict] = None):
        """
        Initialize the quantity estimator.
        
        Args:
            calibration_data: Optional calibration data with pixels_per_cm and spoon dimensions
        """
        self.calibration_data = calibration_data or {}
        self.pixels_per_cm = self.calibration_data.get("pixels_per_cm", 35.0)
        self.spoon_data = self.calibration_data.get("spoons", {
            "teaspoon": {"bowl_diameter_cm": 3.2, "bowl_area_cm2": 8.0},
            "tablespoon": {"bowl_diameter_cm": 3.9, "bowl_area_cm2": 12.3}
        })
        
    def estimate_quantity(
        self, 
        vlm_json: Dict[str, Any], 
        ocr_text: str = "", 
        depth_map: Optional[Any] = None
    ) -> Optional[QuantityEstimate]:
        """
        Fuse spoon/container detections, fill ratios, OCR marks, and optional depth
        to produce a quantity estimate. Optimized for CPU performance.
        
        Args:
            vlm_json: Vision LLM output with detected items, tools, containers
            ocr_text: OCR text from labels or measuring marks
            depth_map: Optional depth map for volume estimation
            
        Returns:
            QuantityEstimate or None if unable to estimate
        """
        logger.debug(f"Estimating quantity from VLM: {vlm_json.keys()}, OCR: '{ocr_text[:50]}'")
        
        # Priority 1: Spoon detection & fill ratio from VLM/YOLO detections
        spoon_estimate = self._estimate_from_spoon(vlm_json)
        if spoon_estimate and spoon_estimate.confidence > 0.6:
            logger.info(f"Spoon estimate: {spoon_estimate}")
            return spoon_estimate
        
        # Priority 2: OCR marks like "1/2 tsp", "100 g"
        if ocr_text:
            ocr_estimate = self._estimate_from_ocr(ocr_text)
            if ocr_estimate and ocr_estimate.confidence > 0.7:
                logger.info(f"OCR estimate: {ocr_estimate}")
                return ocr_estimate
        
        # Priority 3: Depth-assisted volume (optional, slower)
        if depth_map is not None:
            depth_estimate = self._estimate_from_depth(depth_map, vlm_json)
            if depth_estimate:
                logger.info(f"Depth estimate: {depth_estimate}")
                return depth_estimate
        
        # Priority 4: Fallback heuristic based on detected items
        if spoon_estimate:  # Return lower-confidence spoon estimate if available
            return spoon_estimate
            
        # Last resort: generic heuristic
        logger.warning("Using fallback heuristic estimate")
        return QuantityEstimate(
            amount=0.25, 
            unit="teaspoon", 
            confidence=0.3, 
            method="heuristic"
        )
    
    def _estimate_from_spoon(self, vlm_json: Dict[str, Any]) -> Optional[QuantityEstimate]:
        """Extract quantity from spoon detection and fill ratio."""
        tools = vlm_json.get("tools", [])
        
        for tool in tools:
            if tool.get("name", "").lower() in ["teaspoon", "tablespoon", "spoon"]:
                fill_ratio = tool.get("fill_ratio", 0.5)
                heaped = tool.get("heaped", False)
                spoon_type = tool.get("name", "teaspoon").lower()
                
                # Map fill ratio to quantity
                return self._map_ratio_to_quantity(fill_ratio, heaped, spoon_type)
        
        return None
    
    def _map_ratio_to_quantity(self, ratio: float, heaped: bool, spoon_type: str) -> Optional[QuantityEstimate]:
        """Map fill ratio to actual quantity."""
        # Normalize spoon type
        if "table" in spoon_type:
            unit = "tablespoon"
            base_multiplier = 1.0
        else:
            unit = "teaspoon"
            base_multiplier = 1.0
        
        # Determine amount based on fill ratio
        if ratio < 0.2:
            amount = 0.25 * base_multiplier
            confidence = 0.6
        elif 0.4 <= ratio <= 0.6:
            amount = 0.5 * base_multiplier
            if heaped:
                amount = 0.75 * base_multiplier
            confidence = 0.75
        elif ratio >= 0.9:
            amount = 1.0 * base_multiplier
            if heaped:
                amount = 1.25 * base_multiplier
            confidence = 0.8
        else:
            # Intermediate values
            amount = ratio * base_multiplier
            confidence = 0.65
        
        return QuantityEstimate(amount, unit, confidence, "spoon_fill_ratio")
    
    def _estimate_from_ocr(self, text: str) -> Optional[QuantityEstimate]:
        """Extract quantity from OCR text."""
        # Pattern matching for common measurements
        patterns = [
            (r'(\d+/\d+|½|¼|¾)\s*(tsp|teaspoon)', 'teaspoon'),
            (r'(\d+/\d+|½|¼|¾)\s*(tbsp|tablespoon)', 'tablespoon'),
            (r'(\d+\.?\d*)\s*(tsp|teaspoon)', 'teaspoon'),
            (r'(\d+\.?\d*)\s*(tbsp|tablespoon)', 'tablespoon'),
            (r'(\d+\.?\d*)\s*(g|grams?)', 'grams'),
            (r'(\d+\.?\d*)\s*(cup|cups)', 'cup')
        ]
        
        text_lower = text.lower()
        
        for pattern, unit in patterns:
            match = re.search(pattern, text_lower)
            if match:
                amount_str = match.group(1)
                amount = self._parse_amount(amount_str)
                normalized_unit = self._normalize_unit(unit)
                
                return QuantityEstimate(amount, normalized_unit, 0.9, "ocr_mark")
        
        return None
    
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
            'g': 'grams',
            'gram': 'grams',
        }
        
        return unit_map.get(unit.lower(), unit.lower())
    
    def _estimate_from_depth(self, depth_map, vlm_json: Dict[str, Any]) -> Optional[QuantityEstimate]:
        """Estimate volume from depth map (placeholder for future implementation)."""
        # This would use relative depth differences over spice mask region
        # to fit a simple mound model and estimate volume
        logger.debug("Depth-based estimation not yet fully implemented")
        return QuantityEstimate(1.0, "teaspoon", 0.5, "depth_volume")
