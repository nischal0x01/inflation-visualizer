"""
Graphics Utilities - Drawing Primitives and Text Rendering
===========================================================
Reusable OpenGL drawing functions
"""

from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os


def flip_y(y: int, window_height: int) -> float:
    """Convert top-down Y to OpenGL Y coordinates."""
    return window_height - y


class TextRenderer:
    """Efficient text rendering with caching."""
    
    def __init__(self):
        self.cache = {}
        self._font_cache = {}

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """Get or load a font at the specified size."""
        if size in self._font_cache:
            return self._font_cache[size]

        # Try common font paths across platforms
        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/gnu-free/FreeSansBold.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial.ttf",
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    self._font_cache[size] = ImageFont.truetype(path, size)
                    return self._font_cache[size]
                except:
                    pass
        
        self._font_cache[size] = ImageFont.load_default()
        return self._font_cache[size]

    def render(self, text: str, x: float, y_top: float, window_height: int, 
               size: int = 24, color: tuple = (1, 1, 1, 1), center: bool = False) -> tuple[float, float]:
        """
        Render text at the specified position.
        
        Returns:
            Tuple of (width, height) of rendered text
        """
        cache_key = (text, size)

        if cache_key not in self.cache:
            self._create_texture(text, size)

        tex_id, width, height = self.cache[cache_key]

        if center:
            x -= width // 2

        gl_y = flip_y(y_top, window_height) - height

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(*color)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, gl_y)
        glTexCoord2f(1, 0); glVertex2f(x + width, gl_y)
        glTexCoord2f(1, 1); glVertex2f(x + width, gl_y + height)
        glTexCoord2f(0, 1); glVertex2f(x, gl_y + height)
        glEnd()

        glDisable(GL_TEXTURE_2D)
        return width, height

    def _create_texture(self, text: str, size: int):
        """Create and cache a text texture."""
        cache_key = (text, size)
        font = self.get_font(size)

        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0] + 8
        height = bbox[3] - bbox[1] + 8

        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.text((4, 4 - bbox[1]), text, font=font, fill=(255, 255, 255, 255))

        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        data = np.array(img, dtype=np.uint8)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, data)

        self.cache[cache_key] = (tex_id, width, height)


class GLDrawer:
    """Collection of OpenGL drawing utilities."""
    
    def __init__(self, window_height: int):
        self.window_height = window_height
        self.text_renderer = TextRenderer()

    def draw_rect(self, x: float, y_top: float, w: float, h: float, 
                  color: tuple, filled: bool = True):
        """Draw a rectangle (filled or outline)."""
        glDisable(GL_TEXTURE_2D)
        glColor4f(*color)
        y = flip_y(y_top, self.window_height) - h
        
        if filled:
            glBegin(GL_QUADS)
        else:
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
        
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

    def draw_rounded_rect(self, x: float, y_top: float, w: float, h: float, 
                         color: tuple, radius: float = 12):
        """Draw a rounded rectangle."""
        glDisable(GL_TEXTURE_2D)
        glColor4f(*color)
        y = flip_y(y_top, self.window_height) - h

        # Main body
        glBegin(GL_QUADS)
        glVertex2f(x + radius, y)
        glVertex2f(x + w - radius, y)
        glVertex2f(x + w - radius, y + h)
        glVertex2f(x + radius, y + h)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(x, y + radius)
        glVertex2f(x + radius, y + radius)
        glVertex2f(x + radius, y + h - radius)
        glVertex2f(x, y + h - radius)
        glEnd()

        glBegin(GL_QUADS)
        glVertex2f(x + w - radius, y + radius)
        glVertex2f(x + w, y + radius)
        glVertex2f(x + w, y + h - radius)
        glVertex2f(x + w - radius, y + h - radius)
        glEnd()

        # Corners
        segments = 8
        corner_positions = [
            (x + radius, y + radius, (180, 270)),
            (x + w - radius, y + radius, (270, 360)),
            (x + w - radius, y + h - radius, (0, 90)),
            (x + radius, y + h - radius, (90, 180))
        ]
        
        for cx, cy, (start_angle, end_angle) in corner_positions:
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
            for i in range(segments + 1):
                angle = math.radians(start_angle + (end_angle - start_angle) * i / segments)
                glVertex2f(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
            glEnd()

    def draw_circle(self, x: float, y_top: float, radius: float, 
                   color: tuple, filled: bool = True, segments: int = 32):
        """Draw a circle."""
        glDisable(GL_TEXTURE_2D)
        glColor4f(*color)
        y = flip_y(y_top, self.window_height)
        
        if filled:
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(x, y)
            for i in range(segments + 1):
                angle = 2 * math.pi * i / segments
                glVertex2f(x + math.cos(angle) * radius, y + math.sin(angle) * radius)
            glEnd()
        else:
            glLineWidth(2)
            glBegin(GL_LINE_LOOP)
            for i in range(segments):
                angle = 2 * math.pi * i / segments
                glVertex2f(x + math.cos(angle) * radius, y + math.sin(angle) * radius)
            glEnd()

    def draw_line(self, x1: float, y1_top: float, x2: float, y2_top: float, 
                  color: tuple, width: float = 1):
        """Draw a line."""
        glDisable(GL_TEXTURE_2D)
        glLineWidth(width)
        glColor4f(*color)
        y1 = flip_y(y1_top, self.window_height)
        y2 = flip_y(y2_top, self.window_height)
        
        glBegin(GL_LINES)
        glVertex2f(x1, y1)
        glVertex2f(x2, y2)
        glEnd()

    def draw_panel(self, x: float, y_top: float, w: float, h: float, 
                   title: str = None, accent_color: tuple = (1.0, 0.75, 0.0)):
        """Draw a clean panel with shadow and subtle border."""
        try:
            from . import ui_theme
        except ImportError:
            import ui_theme
        
        # Soft shadow for depth
        self.draw_rounded_rect(x + 5, y_top + 5, w, h, (0.0, 0.0, 0.0, 0.25))
        
        # Main panel background
        self.draw_rounded_rect(x, y_top, w, h, ui_theme.BG_PANEL)
        
        # Clean, subtle border
        y = flip_y(y_top, self.window_height) - h
        glLineWidth(1.5)
        glColor4f(0.25, 0.30, 0.42, 0.4)
        r = ui_theme.BORDER_RADIUS
        glBegin(GL_LINE_LOOP)
        # Simple rounded rectangle border
        glVertex2f(x + r, y)
        glVertex2f(x + w - r, y)
        glVertex2f(x + w, y + r)
        glVertex2f(x + w, y + h - r)
        glVertex2f(x + w - r, y + h)
        glVertex2f(x + r, y + h)
        glVertex2f(x, y + h - r)
        glVertex2f(x, y + r)
        glEnd()

        # Top accent line - more visible
        self.draw_rect(x + 20, y_top, w - 40, 4, (*accent_color, 0.95))

        if title:
            self.text_renderer.render(title, x + 25, y_top + 24, self.window_height,
                                     size=26, color=(*accent_color, 1))

    def draw_slider(self, x: float, y_top: float, w: float, h: float, 
                   value: float, max_val: float, color: tuple, 
                   label: str, show_val: str):
        """Draw a clean slider with label and value display."""
        # Label
        self.text_renderer.render(label, x, y_top - 40, self.window_height, 
                                 size=22, color=(0.70, 0.73, 0.82, 1))
        
        # Value display - more prominent
        self.text_renderer.render(show_val, x + w - 100, y_top - 40, self.window_height,
                                 size=28, color=(*color, 1))

        # Track background - darker
        self.draw_rounded_rect(x, y_top, w, h, (0.05, 0.07, 0.12, 1.0), radius=h//2)

        # Fill bar - solid color without glow
        fill_w = max(h, w * (value / max_val))
        if fill_w > 0:
            self.draw_rounded_rect(x, y_top, fill_w, h, (*color, 0.90), radius=h//2)

        # Clean handle
        handle_size = h + 14
        handle_x = x + fill_w - handle_size // 2
        handle_x = max(x - handle_size // 2, min(x + w - handle_size // 2, handle_x))
        handle_y = y_top - 7
        
        # Handle with clean shadow
        self.draw_rounded_rect(handle_x + 1, handle_y + 1, handle_size, handle_size,
                              (0.0, 0.0, 0.0, 0.15), radius=handle_size//2)
        
        # Handle body - pure white
        self.draw_rounded_rect(handle_x, handle_y, handle_size, handle_size,
                              (1, 1, 1, 0.98), radius=handle_size//2)
        
        # Handle inner accent
        inner_size = handle_size - 8
        self.draw_rounded_rect(handle_x + 4, handle_y + 4, inner_size, 
                              inner_size, (*color, 0.85), radius=inner_size//2)

    def draw_button(self, x: float, y_top: float, w: float, h: float, 
                   label: str, selected: bool = False, hover: bool = False, 
                   color: tuple = None, press_scale: float = 1.0):
        """Draw a clean button without animations."""
        if selected:
            bg = color if color else (0.25, 0.80, 0.50, 1.0)
            text_col = (0.02, 0.02, 0.02, 1)
            border_col = (*bg[:3], 0.7)
        elif hover:
            bg = (0.12, 0.15, 0.23, 1.0)
            text_col = (1, 1, 1, 1)
            border_col = (0.45, 0.50, 0.60, 0.9)
        else:
            bg = (0.08, 0.10, 0.16, 1.0)
            text_col = (0.70, 0.73, 0.82, 1)
            border_col = (0.20, 0.25, 0.35, 0.5)

        # Soft shadow for button depth
        self.draw_rounded_rect(x + 1, y_top + 1, w, h, (0.0, 0.0, 0.0, 0.15), radius=10)
        
        # Clean button background
        self.draw_rounded_rect(x, y_top, w, h, bg, radius=10)
        
        # Visible border
        y = flip_y(y_top, self.window_height) - h
        glLineWidth(1.5)
        glColor4f(*border_col)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x + 10, y)
        glVertex2f(x + w - 10, y)
        glVertex2f(x + w, y + 10)
        glVertex2f(x + w, y + h - 10)
        glVertex2f(x + w - 10, y + h)
        glVertex2f(x + 10, y + h)
        glVertex2f(x, y + h - 10)
        glVertex2f(x, y + 10)
        glEnd()

        self.text_renderer.render(label, x + w // 2, y_top + h // 2 - 12, 
                                 self.window_height, size=22, color=text_col, center=True)

    def draw_gradient_background(self, width: int, height: int):
        """Draw a subtle gradient background."""
        glDisable(GL_TEXTURE_2D)
        
        # Create subtle vertical gradient
        glBegin(GL_QUADS)
        glColor4f(0.02, 0.03, 0.05, 1.0)  # Top - very dark navy
        glVertex2f(0, height)
        glVertex2f(width, height)
        
        glColor4f(0.03, 0.04, 0.07, 1.0)  # Bottom - slightly lighter
        glVertex2f(width, 0)
        glVertex2f(0, 0)
        glEnd()

    def draw_grid(self, width: int, height: int, grid_size: int = 40):
        """Draw a subtle grid pattern."""
        glDisable(GL_TEXTURE_2D)
        glColor4f(0.06, 0.08, 0.12, 0.20)  # Very subtle grid
        glLineWidth(1)
        
        for i in range(0, width, grid_size):
            glBegin(GL_LINES)
            glVertex2f(i, 0)
            glVertex2f(i, height)
            glEnd()
        
        for i in range(0, height, grid_size):
            glBegin(GL_LINES)
            glVertex2f(0, i)
            glVertex2f(width, i)
            glEnd()
