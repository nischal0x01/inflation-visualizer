"""
UI Theme and Color Management
==============================
Centralized theme configuration and color palette
"""

# ============ THEME CONSTANTS ============
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Background Colors
BG_DARK_PRIMARY = (0.03, 0.04, 0.06, 1.0)  # Deep dark blue-black
BG_PANEL = (0.06, 0.08, 0.12, 0.98)  # Slightly lighter panel background
BG_HOVER = (0.2, 0.25, 0.35, 1.0)  # Hover state

# Text Colors
TEXT_PRIMARY = (1.0, 1.0, 1.0, 1.0)  # White
TEXT_SECONDARY = (0.75, 0.78, 0.85, 1.0)  # Light gray
TEXT_MUTED = (0.4, 0.42, 0.48, 1.0)  # Muted gray
TEXT_LABEL = (0.7, 0.72, 0.78, 1.0)  # Label gray

# Accent Colors
ACCENT_BLUE = (0.3, 0.7, 1.0)
ACCENT_GOLD = (1.0, 0.75, 0.0)
ACCENT_GOLD_ALT = (1.0, 0.8, 0.3)
ACCENT_YELLOW = (0.95, 0.75, 0.2)
ACCENT_RED = (0.95, 0.3, 0.25)
ACCENT_GREEN = (0.3, 0.75, 0.5)

# Value Status Colors
COLOR_HEALTHY = (0.2, 0.85, 0.5)  # Green - healthy purchasing power
COLOR_MODERATE = (0.95, 0.75, 0.2)  # Yellow - moderate loss
COLOR_SEVERE = (0.95, 0.35, 0.25)  # Red - severe loss

# UI Element Colors
BORDER_COLOR = (0.3, 0.35, 0.45, 1.0)
GRID_COLOR = (0.08, 0.1, 0.14, 0.5)
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.4)

# ============ SIZING ============
BORDER_RADIUS = 12
BORDER_RADIUS_SMALL = 8
SHADOW_OFFSET = 6
SHADOW_BLUR = 6

# ============ ANIMATION SPEEDS ============
ANIMATION_SPEED_FAST = 0.15
ANIMATION_SPEED_NORMAL = 0.5
ANIMATION_SPEED_SLOW = 1.0

SCALE_ANIMATION_SPEED = 5
POWER_ANIMATION_SPEED = 8
DENOM_TRANSITION_SPEED = 4

# ============ SIZES ============
MONEY_WIDTH = 380
MONEY_HEIGHT = 190

FONT_TITLE = 44
FONT_HEADING = 28
FONT_BUTTON = 24
FONT_NORMAL = 22
FONT_SMALL = 18
FONT_TINY = 14

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
        return COLOR_HEALTHY
    elif purchasing_power > 40:
        return COLOR_MODERATE
    else:
        return COLOR_SEVERE


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
