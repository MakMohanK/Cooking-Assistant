# recipe_validator.py
"""
Recipe Validator Module
Compares observed ingredient additions vs recipe expectations (with tolerance),
flags deviations, and suggests actionable corrections.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


@dataclass
class Deviation:
    """Represents a deviation from the recipe with correction suggestions."""
    item: str
    expected_amount: float
    expected_unit: str
    observed_amount: float
    observed_unit: str
    severity: str  # "minor" | "major"
    suggestion: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return (f"{self.severity.upper()}: {self.item} - "
                f"expected {self.expected_amount} {self.expected_unit}, "
                f"observed {self.observed_amount} {self.observed_unit}")


# Tolerance settings per ingredient type
TOLERANCE = {
    # Spices (more forgiving)
    "turmeric": {"teaspoon": 0.25, "tablespoon": 0.25},
    "cumin": {"teaspoon": 0.25, "tablespoon": 0.25},
    "coriander": {"teaspoon": 0.25, "tablespoon": 0.25},
    "chili_powder": {"teaspoon": 0.20, "tablespoon": 0.20},
    
    # Salt (less forgiving)
    "salt": {"teaspoon": 0.15, "tablespoon": 0.15, "pinch": 0.5},
    
    # Liquids and volumes (percentage-based)
    "oil": {"cup": 0.1, "tablespoon": 0.25, "teaspoon": 0.25},
    "water": {"cup": 0.15, "tablespoon": 0.25},
    
    # Default fallback
    "__default__": {"teaspoon": 0.25, "tablespoon": 0.25, "cup": 0.1, "grams": 10}
}


# Correction suggestions based on over/under and ingredient type
CORRECTION_SUGGESTIONS = {
    "turmeric": {
        "over": "Balance bitterness with yogurt, lemon juice, or a pinch of sugar.",
        "under": "Add a small pinch more to reach the recipe amount."
    },
    "salt": {
        "over": "Balance with lemon juice, sugar, or add more liquid/base ingredients.",
        "under": "Add a small pinch more carefully."
    },
    "chili_powder": {
        "over": "Balance heat with yogurt, cream, or coconut milk.",
        "under": "Add more carefully to taste."
    },
    "cumin": {
        "over": "The flavor is strong. Consider balancing with coriander or more base.",
        "under": "Add a bit more for the intended flavor profile."
    },
    "__default__": {
        "over": "Remove some or balance with complementary ingredients.",
        "under": "Add a bit more to reach the recipe amount."
    }
}


class RecipeValidator:
    """Validates ingredient additions against recipe expectations."""
    
    def __init__(self, recipe: Dict[str, Any], tolerance_override: Optional[Dict] = None):
        """
        Initialize recipe validator.
        
        Args:
            recipe: Recipe dictionary with ingredients and steps
            tolerance_override: Optional custom tolerance settings
        """
        self.recipe = recipe
        self.tolerance = tolerance_override or TOLERANCE
        self.session_state = {
            "current_step": 0,
            "added_ingredients": [],
            "deviations": []
        }
        logger.info(f"Initialized validator for recipe: {recipe.get('name', 'Unknown')}")
    
    def validate_step(
        self, 
        step: Dict[str, Any], 
        observed: Dict[str, Any]
    ) -> Optional[Deviation]:
        """
        Validate a single ingredient addition against recipe expectations.
        
        Args:
            step: Recipe step with expected ingredient, amount, unit
                  e.g., {"ingredient":"turmeric", "amount":0.5, "unit":"teaspoon"}
            observed: Observed ingredient data with estimate
                     e.g., {"ingredient":"turmeric", "estimate":{"amount":0.75, "unit":"teaspoon"}}
        
        Returns:
            Deviation object if there's a significant deviation, None otherwise
        """
        # Extract expected values
        ingredient = step.get("ingredient", "unknown")
        exp_amt = step.get("amount", 0)
        exp_unit = step.get("unit", "")
        
        # Extract observed values
        obs_data = observed.get("estimate")
        if not obs_data:
            logger.warning(f"No estimate data for {ingredient}")
            return None
        
        obs_amt = obs_data.get("amount", 0)
        obs_unit = obs_data.get("unit", "")
        obs_ingredient = observed.get("ingredient", ingredient)
        
        logger.debug(f"Validating {obs_ingredient}: expected {exp_amt} {exp_unit}, observed {obs_amt} {obs_unit}")
        
        # Check unit mismatch
        if obs_unit != exp_unit:
            return Deviation(
                item=ingredient,
                expected_amount=exp_amt,
                expected_unit=exp_unit,
                observed_amount=obs_amt,
                observed_unit=obs_unit,
                severity="major",
                suggestion="Use the correct measuring unit as specified in the recipe."
            )
        
        # Get tolerance for this ingredient and unit
        ingredient_tol = self.tolerance.get(ingredient, self.tolerance["__default__"])
        tol_value = ingredient_tol.get(exp_unit, 0.25)
        
        # Calculate difference
        diff = obs_amt - exp_amt
        abs_diff = abs(diff)
        
        # For percentage-based units (cups, grams), use percentage tolerance
        if exp_unit in ["cup", "grams"]:
            rel_diff = abs_diff / max(exp_amt, 1e-6)
            is_major = rel_diff > tol_value
        else:
            # For teaspoons/tablespoons, use absolute tolerance
            is_major = abs_diff > tol_value
        
        # Determine severity
        severity = "major" if is_major else "minor"
        
        # Get correction suggestion
        direction = "over" if diff > 0 else "under"
        suggestions = CORRECTION_SUGGESTIONS.get(ingredient, CORRECTION_SUGGESTIONS["__default__"])
        suggestion = suggestions.get(direction, "Adjust the amount as needed.")
        
        # For minor deviations, be more lenient
        if severity == "minor":
            suggestion = "This is close enough. You can proceed to the next step."
        
        # Log the deviation
        deviation = Deviation(
            item=ingredient,
            expected_amount=exp_amt,
            expected_unit=exp_unit,
            observed_amount=obs_amt,
            observed_unit=obs_unit,
            severity=severity,
            suggestion=suggestion
        )
        
        if severity == "major":
            logger.warning(f"Major deviation detected: {deviation}")
        else:
            logger.info(f"Minor deviation: {deviation}")
        
        # Track in session state
        self.session_state["deviations"].append(deviation.to_dict())
        
        return deviation
    
    def add_ingredient(self, ingredient: str, amount: float, unit: str):
        """
        Track an ingredient addition in the session state.
        
        Args:
            ingredient: Ingredient name
            amount: Amount added
            unit: Unit of measurement
        """
        self.session_state["added_ingredients"].append({
            "ingredient": ingredient,
            "amount": amount,
            "unit": unit,
            "step": self.session_state["current_step"]
        })
        logger.info(f"Added {amount} {unit} of {ingredient} at step {self.session_state['current_step']}")
    
    def advance_step(self):
        """Advance to the next recipe step."""
        self.session_state["current_step"] += 1
        logger.info(f"Advanced to step {self.session_state['current_step']}")
    
    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get the current recipe step."""
        steps = self.recipe.get("steps", [])
        idx = self.session_state["current_step"]
        if 0 <= idx < len(steps):
            return steps[idx]
        return None
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current cooking session."""
        return {
            "recipe_name": self.recipe.get("name", "Unknown"),
            "current_step": self.session_state["current_step"],
            "total_steps": len(self.recipe.get("steps", [])),
            "ingredients_added": len(self.session_state["added_ingredients"]),
            "deviations": self.session_state["deviations"],
            "major_deviations": len([d for d in self.session_state["deviations"] if d["severity"] == "major"])
        }
    
    def reset_session(self):
        """Reset the session state for a new cooking session."""
        self.session_state = {
            "current_step": 0,
            "added_ingredients": [],
            "deviations": []
        }
        logger.info("Session state reset")


def unit_conversion(amount: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Convert between common cooking units (basic conversions).
    
    Args:
        amount: Amount to convert
        from_unit: Source unit
        to_unit: Target unit
    
    Returns:
        Converted amount or None if conversion not supported
    """
    # Normalize unit names
    from_unit = from_unit.lower().strip()
    to_unit = to_unit.lower().strip()
    
    # Conversion factors (to teaspoons as base)
    to_tsp = {
        "teaspoon": 1.0,
        "tsp": 1.0,
        "tablespoon": 3.0,
        "tbsp": 3.0,
        "cup": 48.0,
        "pinch": 0.125
    }
    
    if from_unit in to_tsp and to_unit in to_tsp:
        # Convert to teaspoons, then to target unit
        tsp_amount = amount * to_tsp[from_unit]
        return tsp_amount / to_tsp[to_unit]
    
    return None
