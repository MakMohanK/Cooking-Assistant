# test_recipe_validator.py
"""
Unit tests for Recipe Validator module
Tests deviation detection, tolerance checking, and correction suggestions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from recipe_validator import RecipeValidator, Deviation, unit_conversion


class TestDeviation:
    """Test Deviation dataclass."""
    
    def test_creation(self):
        """Test creating a deviation."""
        dev = Deviation(
            item="turmeric",
            expected_amount=0.5,
            expected_unit="teaspoon",
            observed_amount=0.75,
            observed_unit="teaspoon",
            severity="major",
            suggestion="Remove some or balance with acid."
        )
        
        assert dev.item == "turmeric"
        assert dev.severity == "major"
        assert "Remove" in dev.suggestion
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        dev = Deviation("salt", 0.5, "teaspoon", 0.7, "teaspoon", "major", "Balance with lemon")
        d = dev.to_dict()
        
        assert isinstance(d, dict)
        assert d["item"] == "salt"
        assert d["severity"] == "major"


class TestRecipeValidator:
    """Test RecipeValidator class."""
    
    @pytest.fixture
    def sample_recipe(self):
        """Create a sample recipe."""
        return {
            "name": "Test Recipe",
            "serves": 2,
            "ingredients": [
                {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"},
                {"ingredient": "salt", "amount": 0.5, "unit": "teaspoon"}
            ],
            "steps": [
                {
                    "instruction": "Add turmeric",
                    "check": {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
                },
                {
                    "instruction": "Add salt",
                    "check": {"ingredient": "salt", "amount": 0.5, "unit": "teaspoon"}
                }
            ]
        }
    
    @pytest.fixture
    def validator(self, sample_recipe):
        """Create validator instance."""
        return RecipeValidator(sample_recipe)
    
    def test_initialization(self, validator, sample_recipe):
        """Test validator initialization."""
        assert validator is not None
        assert validator.recipe == sample_recipe
        assert validator.session_state["current_step"] == 0
    
    def test_exact_match(self, validator):
        """Test when observed matches expected exactly."""
        step = {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
        observed = {
            "ingredient": "turmeric",
            "estimate": {"amount": 0.5, "unit": "teaspoon"}
        }
        
        deviation = validator.validate_step(step, observed)
        
        # Should be minor or no deviation
        assert deviation is None or deviation.severity == "minor"
    
    def test_minor_deviation_within_tolerance(self, validator):
        """Test minor deviation within tolerance."""
        step = {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
        observed = {
            "ingredient": "turmeric",
            "estimate": {"amount": 0.6, "unit": "teaspoon"}  # +0.1, within 0.25 tolerance
        }
        
        deviation = validator.validate_step(step, observed)
        
        assert deviation is not None
        assert deviation.severity == "minor"
        assert "close enough" in deviation.suggestion.lower()
    
    def test_major_deviation_over(self, validator):
        """Test major deviation - too much added."""
        step = {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
        observed = {
            "ingredient": "turmeric",
            "estimate": {"amount": 1.0, "unit": "teaspoon"}  # +0.5, exceeds tolerance
        }
        
        deviation = validator.validate_step(step, observed)
        
        assert deviation is not None
        assert deviation.severity == "major"
        assert deviation.observed_amount > deviation.expected_amount
        assert "Remove" in deviation.suggestion or "balance" in deviation.suggestion.lower()
    
    def test_major_deviation_under(self, validator):
        """Test major deviation - too little added."""
        step = {"ingredient": "salt", "amount": 0.5, "unit": "teaspoon"}
        observed = {
            "ingredient": "salt",
            "estimate": {"amount": 0.2, "unit": "teaspoon"}  # -0.3, exceeds tolerance
        }
        
        deviation = validator.validate_step(step, observed)
        
        assert deviation is not None
        assert deviation.severity == "major"
        assert deviation.observed_amount < deviation.expected_amount
        assert "Add" in deviation.suggestion or "more" in deviation.suggestion.lower()
    
    def test_unit_mismatch(self, validator):
        """Test unit mismatch detection."""
        step = {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
        observed = {
            "ingredient": "turmeric",
            "estimate": {"amount": 0.5, "unit": "tablespoon"}  # Wrong unit!
        }
        
        deviation = validator.validate_step(step, observed)
        
        assert deviation is not None
        assert deviation.severity == "major"
        assert "correct" in deviation.suggestion.lower() and "unit" in deviation.suggestion.lower()
    
    def test_salt_stricter_tolerance(self, validator):
        """Test that salt has stricter tolerance than spices."""
        # Salt deviation
        salt_step = {"ingredient": "salt", "amount": 0.5, "unit": "teaspoon"}
        salt_observed = {
            "ingredient": "salt",
            "estimate": {"amount": 0.7, "unit": "teaspoon"}  # +0.2
        }
        
        salt_dev = validator.validate_step(salt_step, salt_observed)
        
        # Turmeric deviation (same amount)
        turmeric_step = {"ingredient": "turmeric", "amount": 0.5, "unit": "teaspoon"}
        turmeric_observed = {
            "ingredient": "turmeric",
            "estimate": {"amount": 0.7, "unit": "teaspoon"}  # +0.2
        }
        
        turmeric_dev = validator.validate_step(turmeric_step, turmeric_observed)
        
        # Salt should be more severe or turmeric should be minor
        assert salt_dev is not None
        if turmeric_dev:
            # Same absolute deviation, but salt should be treated more seriously
            assert salt_dev.severity == "major" or turmeric_dev.severity == "minor"
    
    def test_add_ingredient_tracking(self, validator):
        """Test ingredient addition tracking."""
        validator.add_ingredient("turmeric", 0.5, "teaspoon")
        
        assert len(validator.session_state["added_ingredients"]) == 1
        assert validator.session_state["added_ingredients"][0]["ingredient"] == "turmeric"
    
    def test_advance_step(self, validator):
        """Test step advancement."""
        initial_step = validator.session_state["current_step"]
        validator.advance_step()
        
        assert validator.session_state["current_step"] == initial_step + 1
    
    def test_get_current_step(self, validator):
        """Test getting current step."""
        step = validator.get_current_step()
        
        assert step is not None
        assert "instruction" in step
        assert step["instruction"] == "Add turmeric"
    
    def test_get_session_summary(self, validator):
        """Test session summary generation."""
        validator.add_ingredient("turmeric", 0.5, "teaspoon")
        validator.advance_step()
        
        summary = validator.get_session_summary()
        
        assert "recipe_name" in summary
        assert summary["recipe_name"] == "Test Recipe"
        assert summary["current_step"] == 1
        assert summary["ingredients_added"] == 1
    
    def test_reset_session(self, validator):
        """Test session reset."""
        validator.add_ingredient("turmeric", 0.5, "teaspoon")
        validator.advance_step()
        
        validator.reset_session()
        
        assert validator.session_state["current_step"] == 0
        assert len(validator.session_state["added_ingredients"]) == 0
        assert len(validator.session_state["deviations"]) == 0


class TestUnitConversion:
    """Test unit conversion utilities."""
    
    def test_teaspoon_to_tablespoon(self):
        """Test tsp to tbsp conversion."""
        result = unit_conversion(3.0, "teaspoon", "tablespoon")
        assert result == 1.0
    
    def test_tablespoon_to_teaspoon(self):
        """Test tbsp to tsp conversion."""
        result = unit_conversion(1.0, "tablespoon", "teaspoon")
        assert result == 3.0
    
    def test_teaspoon_to_cup(self):
        """Test tsp to cup conversion."""
        result = unit_conversion(48.0, "teaspoon", "cup")
        assert result == 1.0
    
    def test_cup_to_teaspoon(self):
        """Test cup to tsp conversion."""
        result = unit_conversion(1.0, "cup", "teaspoon")
        assert result == 48.0
    
    def test_same_unit(self):
        """Test conversion with same unit."""
        result = unit_conversion(5.0, "teaspoon", "teaspoon")
        assert result == 5.0
    
    def test_unsupported_conversion(self):
        """Test unsupported conversion returns None."""
        result = unit_conversion(1.0, "grams", "teaspoon")
        assert result is None
    
    def test_pinch_conversion(self):
        """Test pinch conversions."""
        result = unit_conversion(8.0, "pinch", "teaspoon")
        assert result == 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
