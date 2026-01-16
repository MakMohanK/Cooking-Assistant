# test_quantity_estimator.py
"""
Unit tests for Quantity Estimator module
Tests fill ratio mapping, OCR parsing, and quantity fusion logic.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from quantity_estimator import QuantityEstimator, QuantityEstimate


class TestQuantityEstimate:
    """Test QuantityEstimate dataclass."""
    
    def test_creation(self):
        """Test creating a quantity estimate."""
        est = QuantityEstimate(
            amount=0.5,
            unit="teaspoon",
            confidence=0.8,
            method="spoon_fill_ratio"
        )
        
        assert est.amount == 0.5
        assert est.unit == "teaspoon"
        assert est.confidence == 0.8
        assert est.method == "spoon_fill_ratio"
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        est = QuantityEstimate(1.0, "tablespoon", 0.9, "ocr_mark")
        d = est.to_dict()
        
        assert isinstance(d, dict)
        assert d["amount"] == 1.0
        assert d["unit"] == "tablespoon"
        assert d["confidence"] == 0.9
        assert d["method"] == "ocr_mark"
    
    def test_str_representation(self):
        """Test string representation."""
        est = QuantityEstimate(0.25, "teaspoon", 0.75, "heuristic")
        s = str(est)
        
        assert "0.25" in s
        assert "teaspoon" in s
        assert "75%" in s
        assert "heuristic" in s


class TestQuantityEstimator:
    """Test QuantityEstimator class."""
    
    @pytest.fixture
    def estimator(self):
        """Create estimator instance."""
        return QuantityEstimator()
    
    @pytest.fixture
    def calibrated_estimator(self):
        """Create calibrated estimator."""
        calib_data = {
            "pixels_per_cm": 40.0,
            "spoons": {
                "teaspoon": {"bowl_diameter_cm": 3.2, "bowl_area_cm2": 8.0},
                "tablespoon": {"bowl_diameter_cm": 3.9, "bowl_area_cm2": 12.3}
            }
        }
        return QuantityEstimator(calib_data)
    
    def test_initialization(self, estimator):
        """Test estimator initialization."""
        assert estimator is not None
        assert isinstance(estimator.calibration_data, dict)
    
    def test_spoon_detection_quarter_teaspoon(self, estimator):
        """Test quarter teaspoon detection."""
        vlm_json = {
            "tools": [
                {"name": "teaspoon", "fill_ratio": 0.2, "heaped": False}
            ]
        }
        
        result = estimator.estimate_quantity(vlm_json, "")
        
        assert result is not None
        assert result.amount == 0.25
        assert result.unit == "teaspoon"
        assert result.method == "spoon_fill_ratio"
        assert result.confidence > 0.5
    
    def test_spoon_detection_half_teaspoon(self, estimator):
        """Test half teaspoon detection."""
        vlm_json = {
            "tools": [
                {"name": "teaspoon", "fill_ratio": 0.5, "heaped": False}
            ]
        }
        
        result = estimator.estimate_quantity(vlm_json, "")
        
        assert result.amount == 0.5
        assert result.unit == "teaspoon"
    
    def test_spoon_detection_full_teaspoon(self, estimator):
        """Test full teaspoon detection."""
        vlm_json = {
            "tools": [
                {"name": "teaspoon", "fill_ratio": 1.0, "heaped": False}
            ]
        }
        
        result = estimator.estimate_quantity(vlm_json, "")
        
        assert result.amount == 1.0
        assert result.unit == "teaspoon"
    
    def test_spoon_detection_heaped(self, estimator):
        """Test heaped teaspoon detection."""
        vlm_json = {
            "tools": [
                {"name": "teaspoon", "fill_ratio": 0.5, "heaped": True}
            ]
        }
        
        result = estimator.estimate_quantity(vlm_json, "")
        
        assert result.amount == 0.75  # Heaped adds extra
        assert result.unit == "teaspoon"
    
    def test_ocr_parsing_fraction(self, estimator):
        """Test OCR parsing with fractions."""
        test_cases = [
            ("1/2 tsp", 0.5, "teaspoon"),
            ("½ tsp", 0.5, "teaspoon"),
            ("1/4 tsp", 0.25, "teaspoon"),
            ("¼ tsp", 0.25, "teaspoon"),
            ("1 tsp", 1.0, "teaspoon"),
            ("1 tbsp", 1.0, "tablespoon")
        ]
        
        for ocr_text, expected_amount, expected_unit in test_cases:
            result = estimator.estimate_quantity({}, ocr_text)
            
            assert result is not None, f"Failed for: {ocr_text}"
            assert result.amount == expected_amount, f"Amount mismatch for: {ocr_text}"
            assert result.unit == expected_unit, f"Unit mismatch for: {ocr_text}"
            assert result.method == "ocr_mark"
            assert result.confidence > 0.7
    
    def test_ocr_parsing_grams(self, estimator):
        """Test OCR parsing with grams."""
        result = estimator.estimate_quantity({}, "100g")
        
        assert result.amount == 100.0
        assert result.unit == "grams"
        assert result.method == "ocr_mark"
    
    def test_priority_ocr_over_spoon(self, estimator):
        """Test that high-confidence OCR takes priority."""
        vlm_json = {
            "tools": [
                {"name": "teaspoon", "fill_ratio": 0.3, "heaped": False}
            ]
        }
        
        # OCR should take priority if confidence is high
        result = estimator.estimate_quantity(vlm_json, "1/2 tsp")
        
        assert result.amount == 0.5
        assert result.method == "ocr_mark"
    
    def test_fallback_heuristic(self, estimator):
        """Test fallback to heuristic when no data available."""
        result = estimator.estimate_quantity({}, "")
        
        assert result is not None
        assert result.method == "heuristic"
        assert result.confidence < 0.5
    
    def test_calibrated_estimator(self, calibrated_estimator):
        """Test calibrated estimator has calibration data."""
        assert calibrated_estimator.pixels_per_cm == 40.0
        assert "teaspoon" in calibrated_estimator.spoon_data
        assert calibrated_estimator.spoon_data["teaspoon"]["bowl_diameter_cm"] == 3.2


class TestOCRParsing:
    """Test OCR text parsing utilities."""
    
    def test_parse_amount_fractions(self):
        """Test parsing fraction amounts."""
        from quantity_estimator import QuantityEstimator
        estimator = QuantityEstimator()
        
        assert estimator._parse_amount("1/2") == 0.5
        assert estimator._parse_amount("1/4") == 0.25
        assert estimator._parse_amount("3/4") == 0.75
        assert estimator._parse_amount("½") == 0.5
        assert estimator._parse_amount("¼") == 0.25
        assert estimator._parse_amount("¾") == 0.75
    
    def test_parse_amount_decimals(self):
        """Test parsing decimal amounts."""
        from quantity_estimator import QuantityEstimator
        estimator = QuantityEstimator()
        
        assert estimator._parse_amount("0.5") == 0.5
        assert estimator._parse_amount("1.5") == 1.5
        assert estimator._parse_amount("2.0") == 2.0
    
    def test_normalize_unit(self):
        """Test unit normalization."""
        from quantity_estimator import QuantityEstimator
        estimator = QuantityEstimator()
        
        assert estimator._normalize_unit("tsp") == "teaspoon"
        assert estimator._normalize_unit("tbsp") == "tablespoon"
        assert estimator._normalize_unit("g") == "grams"
        assert estimator._normalize_unit("ml") == "milliliters"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
