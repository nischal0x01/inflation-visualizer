"""
Economic formulas for inflation calculations
"""

def calculate_purchasing_power(inflation_rate: float, years: int) -> float:
    """
    Calculate the purchasing power of money after inflation.
    
    Formula: PP = 100 / (1 + rate/100)^years
    
    Args:
        inflation_rate: Annual inflation rate as percentage (0-25)
        years: Number of years (1-30)
    
    Returns:
        Purchasing power as percentage (0-100)
    """
    if inflation_rate == 0 or years == 0:
        return 100.0
    return 100.0 / ((1 + inflation_rate / 100) ** years)


def calculate_scale_factor(purchasing_power: float, min_scale: float = 0.25) -> float:
    """
    Convert purchasing power to visual scale (0.25 to 1.0).
    
    Args:
        purchasing_power: Purchasing power percentage
        min_scale: Minimum scale factor
    
    Returns:
        Visual scale factor
    """
    return max(min_scale, min(1.0, purchasing_power / 100))


def calculate_value_loss_percentage(purchasing_power: float) -> float:
    """
    Calculate the percentage of value lost.
    
    Args:
        purchasing_power: Current purchasing power percentage
    
    Returns:
        Value loss as percentage
    """
    return 100.0 - purchasing_power


def calculate_purchasing_quantity(denom_value: float, item_price: float, 
                                 purchasing_power: float) -> tuple:
    """
    Calculate what quantity of an item can be purchased.
    
    Args:
        denom_value: Money denomination value
        item_price: Price per unit of item
        purchasing_power: Current purchasing power percentage
    
    Returns:
        Tuple of (current_quantity, original_quantity)
    """
    original_qty = denom_value / item_price
    current_qty = original_qty * (purchasing_power / 100)
    return current_qty, original_qty


def get_color_for_ratio(ratio: float) -> tuple:
    """
    Get color based on ratio (0-1).
    Green: > 0.7
    Yellow: 0.4-0.7
    Red: < 0.4
    
    Args:
        ratio: Value ratio (0-1)
    
    Returns:
        RGB tuple
    """
    if ratio > 0.7:
        return (0.2, 0.85, 0.5)  # Green
    elif ratio > 0.4:
        return (0.95, 0.75, 0.2)  # Yellow
    else:
        return (0.95, 0.35, 0.25)  # Red


def get_color_for_power(power: float) -> tuple:
    """
    Get color based on purchasing power.
    
    Args:
        power: Purchasing power percentage
    
    Returns:
        RGB tuple
    """
    if power > 70:
        return (0.2, 0.8, 0.4)  # Green
    elif power > 40:
        return (0.95, 0.75, 0.2)  # Yellow
    else:
        return (0.95, 0.35, 0.25)  # Red
