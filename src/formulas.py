"""
Pure mathematical formulas for inflation calculations
====================================================
Keep all financial calculations isolated and testable
"""

import math


def calculate_purchasing_power(inflation_rate: float, years: int) -> float:
    """
    Calculate remaining purchasing power after inflation erodes the value.
    
    Formula: PP = 100 / ((1 + r/100)^y)
    Where r = inflation rate (%), y = years
    
    Args:
        inflation_rate: Annual inflation rate as percentage (e.g., 7.0 for 7%)
        years: Number of years
    
    Returns:
        Remaining purchasing power as percentage (0-100)
    """
    if inflation_rate < 0:
        inflation_rate = 0
    if years < 0:
        years = 0
    
    return 100 / ((1 + inflation_rate / 100) ** years)


def calculate_scale_factor(purchasing_power: float) -> float:
    """
    Convert purchasing power to visual scale (for drawing money size).
    
    Maps purchasing power percentage to scale: 100% → 1.0, 0% → 0.25
    
    Args:
        purchasing_power: Purchasing power as percentage (0-100)
    
    Returns:
        Scale factor (0.25 to 1.0)
    """
    scale = max(0.25, min(1.0, purchasing_power / 100))
    return scale


def calculate_value_loss_percentage(purchasing_power: float) -> float:
    """
    Calculate percentage of value lost.
    
    Args:
        purchasing_power: Remaining purchasing power (0-100)
    
    Returns:
        Value loss as percentage
    """
    return 100 - purchasing_power


def calculate_purchasing_quantity(
    denomination_value: float,
    item_price: float,
    purchasing_power: float
) -> tuple[float, float]:
    """
    Calculate how much of an item can be purchased.
    
    Args:
        denomination_value: Value of note (e.g., 1000 for Rs. 1000)
        item_price: Price per unit of item
        purchasing_power: Current purchasing power (0-100)
    
    Returns:
        Tuple of (current_quantity, original_quantity)
    """
    original_quantity = denomination_value / item_price
    current_quantity = original_quantity * (purchasing_power / 100)
    return current_quantity, original_quantity


def interpolate(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values."""
    return start + (end - start) * t


def ease_out_cubic(t: float) -> float:
    """Easing function for smooth animations."""
    return 1 - pow(1 - t, 3)


def ease_in_out_sine(t: float) -> float:
    """Smooth easing function."""
    return -(math.cos(math.pi * t) - 1) / 2


def ease_in_out_quad(t: float) -> float:
    """Quadratic easing function."""
    return 3 * t * t - 2 * t * t * t


def ease_out_quad(t: float) -> float:
    """Quadratic out easing."""
    return 1 - (1 - t) * (1 - t)


def get_inflation_stage(purchasing_power: float) -> str:
    """Categorize inflation severity."""
    if purchasing_power >= 70:
        return "healthy"
    elif purchasing_power >= 40:
        return "moderate"
    else:
        return "severe"


def get_color_for_value(purchasing_power: float) -> tuple[float, float, float]:
    """Get color based on purchasing power (green → yellow → red)."""
    if purchasing_power > 70:
        return (0.25, 0.90, 0.55)  # Fresh green
    elif purchasing_power > 40:
        return (1.0, 0.78, 0.25)  # Warm yellow
    else:
        return (1.0, 0.38, 0.32)  # Clean red
