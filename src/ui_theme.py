"""
UI Theme and Color Management
==============================
Centralized theme configuration and color palette
"""

# ============ THEME CONSTANTS ============
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Background Colors
BG_DARK_PRIMARY = (0.02, 0.03, 0.05, 1.0)  # Deep dark navy
BG_PANEL = (0.08, 0.10, 0.16, 0.95)  # Slightly lighter panel background
BG_HOVER = (0.15, 0.18, 0.28, 1.0)  # Subtle hover state

# Text Colors
TEXT_PRIMARY = (1.0, 1.0, 1.0, 1.0)  # Pure white
TEXT_SECONDARY = (0.78, 0.81, 0.90, 1.0)  # Light gray
TEXT_MUTED = (0.45, 0.48, 0.58, 1.0)  # Muted gray
TEXT_LABEL = (0.65, 0.68, 0.78, 1.0)  # Label gray

# Accent Colors - more refined
ACCENT_BLUE = (0.35, 0.75, 1.0)  # Brighter, cleaner blue
ACCENT_GOLD = (1.0, 0.80, 0.2)  # Refined gold
ACCENT_GOLD_ALT = (1.0, 0.85, 0.35)  # Gold variant
ACCENT_YELLOW = (1.0, 0.82, 0.25)  # Vibrant yellow
ACCENT_RED = (1.0, 0.35, 0.30)  # Clean red
ACCENT_GREEN = (0.35, 0.80, 0.55)  # Fresh green

# Value Status Colors - more pronounced
COLOR_HEALTHY = (0.25, 0.90, 0.55)  # Green - healthy purchasing power
COLOR_MODERATE = (1.0, 0.78, 0.25)  # Yellow - moderate loss
COLOR_SEVERE = (1.0, 0.38, 0.32)  # Red - severe loss

# UI Element Colors
BORDER_COLOR = (0.25, 0.30, 0.42, 0.6)  # More visible borders
GRID_COLOR = (0.06, 0.08, 0.12, 0.25)  # Subtle grid
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.35)

# ============ SIZING ============
BORDER_RADIUS = 14  # Slightly larger for modern look
BORDER_RADIUS_SMALL = 10
SHADOW_OFFSET = 8  # More prominent shadows
SHADOW_BLUR = 8

# ============ ANIMATION SPEEDS ============
ANIMATION_SPEED_FAST = 0.15
ANIMATION_SPEED_NORMAL = 0.5
ANIMATION_SPEED_SLOW = 1.0

SCALE_ANIMATION_SPEED = 3.0  # Smoother, slower animation
POWER_ANIMATION_SPEED = 6.0  # Smooth value transitions
DENOM_TRANSITION_SPEED = 3.0  # Smooth denomination switching

# ============ SIZES ============
MONEY_WIDTH = 380
MONEY_HEIGHT = 190

FONT_TITLE = 48  # Larger, more prominent title
FONT_HEADING = 30  # Clearer section headings
FONT_BUTTON = 24
FONT_NORMAL = 23  # Slightly larger for readability
FONT_SMALL = 19
FONT_TINY = 15

# ============ PANEL POSITIONS ============
PANEL_LEFT_X = 30
PANEL_CENTER_X = 410
PANEL_RIGHT_X = 1010

PANEL_WIDTH_SIDE = 370
PANEL_WIDTH_CENTER = 580
PANEL_WIDTH_RIGHT = 360

PANEL_HEIGHT = 610
PANEL_Y = 80

# ============ LAYOUT ============
GRID_SIZE = 40

# ============ PARTICLE COLORS ============
PARTICLE_OPACITY = 0.9

# ============ GRADIENTS AND EFFECTS ============

def lerp_color(color1: tuple, color2: tuple, t: float) -> tuple:
    """Linearly interpolate between two colors."""
    return tuple(
        color1[i] + (color2[i] - color1[i]) * t
        for i in range(len(color1))
    )


def get_status_color(purchasing_power: float) -> tuple:
    """Get color based on purchasing power status."""
    if purchasing_power > 70:
        return COLOR_HEALTHY  # Fresh green
    elif purchasing_power > 40:
        return COLOR_MODERATE  # Warm yellow
    else:
        return COLOR_SEVERE  # Clean red


def brighten_color(color: tuple, factor: float = 1.3) -> tuple:
    """Brighten a color."""
    return tuple(min(1.0, c * factor) for c in color[:3]) + color[3:]


def darken_color(color: tuple, factor: float = 0.7) -> tuple:
    """Darken a color."""
    return tuple(c * factor for c in color[:3]) + color[3:]


def add_alpha(color: tuple, alpha: float) -> tuple:
    """Add or replace alpha channel."""
    if len(color) == 3:
        return color + (alpha,)
    else:
        return color[:3] + (alpha,)
