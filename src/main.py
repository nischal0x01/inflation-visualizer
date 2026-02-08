"""
🇳🇵 Nepal Inflation Visualizer - Enhanced Edition
==================================================
Beautiful, touch-friendly visualization of how inflation affects purchasing power.

Features:
  - Ghost outline showing original value
  - Animated particles showing money "evaporating"
  - Year-by-year timeline visualization
  - Touch-friendly large controls
  - Real-time purchasing power comparison
  - Dramatic visual effects

Controls:
  Mouse/Touch: Drag sliders, tap buttons
  W/S or UP/DOWN: Inflation
  A/D or LEFT/RIGHT: Years
  1-7: Select note
  SPACE: Auto mode
  R: Reset | ESC: Exit
"""

import glfw
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import math
import os
import random

# ============ CONFIG ============
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900

# Money sprite regions - CORRECTED measurements from 803x1000 image
MONEY_REGIONS = {
    "50":   (472, 174, 267, 134),
    "5":    (77, 365, 267, 135),
    "100":  (472, 365, 267, 135),
    "10":   (77, 549, 267, 135),
    "500":  (472, 549, 267, 135),
    "20":   (77, 733, 267, 135),
    "1000": (472, 733, 267, 135),
}

DENOM_INFO = {
    "5":    {"color": (0.91, 0.30, 0.51), "animal": "Yak", "value": 5},
    "10":   {"color": (0.25, 0.52, 0.35), "animal": "Deer", "value": 10},
    "20":   {"color": (0.55, 0.45, 0.38), "animal": "Swamp Deer", "value": 20},
    "50":   {"color": (0.45, 0.52, 0.55), "animal": "Himalayan Tahr", "value": 50},
    "100":  {"color": (0.30, 0.58, 0.40), "animal": "One-Horned Rhino", "value": 100},
    "500":  {"color": (0.72, 0.52, 0.30), "animal": "Tiger", "value": 500},
    "1000": {"color": (0.58, 0.35, 0.55), "animal": "Elephant", "value": 1000},
}

# Nepal-relevant purchase items with 2024 prices
PURCHASE_ITEMS = [
    ("🍚 Rice", 75, "kg", (0.95, 0.90, 0.80)),
    ("🥛 Milk", 95, "L", (0.95, 0.95, 1.0)),
    ("🍗 Chicken", 450, "kg", (1.0, 0.85, 0.75)),
    ("🫘 Dal", 240, "kg", (0.90, 0.80, 0.50)),
    ("🚌 Bus Ride", 35, "trip", (0.70, 0.85, 0.95)),
    ("☕ Tea", 25, "cup", (0.85, 0.70, 0.50)),
]


def flip_y(y):
    """Convert top-down Y to OpenGL Y"""
    return WINDOW_HEIGHT - y


def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)


def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def lerp(a, b, t):
    return a + (b - a) * t


class Particle:
    def __init__(self, x, y, color, particle_type="spark"):
        self.type = particle_type
        angle = random.uniform(0, 2 * math.pi)

        if particle_type == "evaporate":
            # Float upward like smoke
            speed = random.uniform(30, 80)
            self.vx = math.cos(angle) * speed * 0.3
            self.vy = random.uniform(50, 120)
            self.life = random.uniform(1.5, 3.0)
            self.size = random.uniform(8, 20)
        elif particle_type == "money_dust":
            # Fall like confetti
            speed = random.uniform(50, 150)
            self.vx = math.cos(angle) * speed
            self.vy = random.uniform(-20, 50)
            self.life = random.uniform(1.0, 2.0)
            self.size = random.uniform(3, 8)
        else:
            # Spark burst
            speed = random.uniform(150, 450)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.life = random.uniform(0.5, 1.2)
            self.size = random.uniform(4, 12)

        self.x = x
        self.y = y
        self.max_life = self.life
        self.color = color
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-180, 180)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rot_speed * dt

        if self.type == "evaporate":
            self.vx += random.uniform(-20, 20) * dt  # Wobble
            self.vy += 10 * dt  # Accelerate upward
        elif self.type == "money_dust":
            self.vy -= 150 * dt  # Gravity
            self.vx *= 0.99  # Air resistance
        else:
            self.vy -= 400 * dt

        self.life -= dt
        return self.life > 0


class TextRenderer:
    def __init__(self):
        self.cache = {}
        self._font_cache = {}

    def get_font(self, size):
        if size in self._font_cache:
            return self._font_cache[size]

        paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
            "/usr/share/fonts/gnu-free/FreeSansBold.ttf",
            "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
            "C:/Windows/Fonts/arial.ttf",
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

    def render(self, text, x, y_top, size=24, color=(1, 1, 1, 1), center=False):
        cache_key = (text, size)

        if cache_key not in self.cache:
            self._create_texture(text, size)

        tex_id, width, height = self.cache[cache_key]

        if center:
            x -= width // 2

        gl_y = flip_y(y_top) - height

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

    def _create_texture(self, text, size):
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


class InflationGame:
    def __init__(self):
        self.window = None
        self.money_texture = None
        self.atlas_w = 0
        self.atlas_h = 0
        self.text = None

        # State
        self.inflation = 7.0
        self.years = 5
        self.denom = "1000"
        self.auto_mode = False
        self.auto_dir = 1

        # Animation
        self.time = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.displayed_power = 100.0
        self.particles = []
        self.evaporate_timer = 0

        # Transition animation
        self.prev_denom = "1000"
        self.denom_transition = 0

        # Button press feedback
        self.button_press_time = {}

        # Mouse/Touch
        self.mouse_x = 0
        self.mouse_y = 0
        self.mouse_pressed = False
        self.mouse_clicked = False
        self.dragging_inflation = False
        self.dragging_years = False
        self.touch_start_x = 0
        self.touch_start_y = 0

        self.keys_prev = {}

    def init(self):
        if not glfw.init():
            return False

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT,
            "🇳🇵 Nepal Inflation Visualizer", None, None)
        if not self.window:
            glfw.terminate()
            return False

        glfw.make_context_current(self.window)
        glfw.swap_interval(1)

        glfw.set_cursor_pos_callback(self.window, self._on_mouse_move)
        glfw.set_mouse_button_callback(self.window, self._on_mouse_button)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if not self._load_texture():
            return False

        self.text = TextRenderer()
        return True

    def _on_mouse_move(self, window, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def _on_mouse_button(self, window, button, action, mods):
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.mouse_pressed = True
                self.mouse_clicked = True
                self.touch_start_x = self.mouse_x
                self.touch_start_y = self.mouse_y
            else:
                self.mouse_pressed = False
                self.dragging_inflation = False
                self.dragging_years = False

    def _load_texture(self):
        paths = ["../assets/fullmoneyasset.jpg", "fullmoneyasset.jpg"]

        img_path = None
        for p in paths:
            if os.path.exists(p):
                img_path = p
                break

        if not img_path:
            print("ERROR: Cannot find fullmoneyasset.jpg")
            return False

        try:
            img = Image.open(img_path).convert("RGBA")
            self.atlas_w = img.width
            self.atlas_h = img.height

            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            data = np.array(img, dtype=np.uint8)

            self.money_texture = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.money_texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                        0, GL_RGBA, GL_UNSIGNED_BYTE, data)

            print(f"Loaded texture: {self.atlas_w}x{self.atlas_h}")
            return True
        except Exception as e:
            print(f"Error loading texture: {e}")
            return False

    def get_uv(self, denom):
        x, y, w, h = MONEY_REGIONS[denom]
        u0 = x / self.atlas_w
        u1 = (x + w) / self.atlas_w
        v0 = 1.0 - (y + h) / self.atlas_h
        v1 = 1.0 - y / self.atlas_h
        return u0, v0, u1, v1

    def calc_power(self):
        return 100 / ((1 + self.inflation / 100) ** self.years)

    def calc_scale(self):
        power = self.calc_power()
        # More dramatic scaling - from 1.0 down to 0.25
        return max(0.25, min(1.0, power / 100))

    def spawn_particles(self, x, y_top, count=25, particle_type="spark"):
        color = DENOM_INFO[self.denom]["color"]
        gl_y = flip_y(y_top)
        for _ in range(count):
            self.particles.append(Particle(x, gl_y, color, particle_type))

    def spawn_evaporation(self):
        """Spawn particles showing money value evaporating"""
        power = self.calc_power()
        if power < 95:  # Only evaporate when there's loss
            color = DENOM_INFO[self.denom]["color"]
            cx = 700
            cy_gl = flip_y(420)

            # Spawn from edges of the money
            base_w = 380 * self.scale
            base_h = 190 * self.scale

            for _ in range(2):
                edge_x = cx + random.uniform(-base_w/2, base_w/2)
                edge_y = cy_gl + base_h/2 + random.uniform(-10, 10)
                self.particles.append(Particle(edge_x, edge_y, color, "evaporate"))

    def handle_input(self):
        mx, my = self.mouse_x, self.mouse_y

        # TOUCH-FRIENDLY: Larger slider areas
        inflation_slider = (50, 200, 320, 50)
        years_slider = (50, 320, 320, 50)

        # Check slider interaction
        if self.mouse_pressed:
            if self.dragging_inflation or (self.mouse_clicked and
                inflation_slider[0] - 20 <= mx <= inflation_slider[0] + inflation_slider[2] + 20 and
                inflation_slider[1] - 20 <= my <= inflation_slider[1] + inflation_slider[3] + 20):
                self.dragging_inflation = True
                ratio = (mx - inflation_slider[0]) / inflation_slider[2]
                ratio = max(0, min(1, ratio))
                self.inflation = ratio * 25

            elif self.dragging_years or (self.mouse_clicked and
                years_slider[0] - 20 <= mx <= years_slider[0] + years_slider[2] + 20 and
                years_slider[1] - 20 <= my <= years_slider[1] + years_slider[3] + 20):
                self.dragging_years = True
                ratio = (mx - years_slider[0]) / years_slider[2]
                ratio = max(0, min(1, ratio))
                self.years = 1 + ratio * 29

        # Button clicks
        if self.mouse_clicked:
            # Denomination buttons - LARGER touch targets
            denoms = ["5", "10", "20", "50", "100", "500", "1000"]
            for i, d in enumerate(denoms):
                bx = 415 + i * 90
                by = 780
                bw, bh = 82, 60
                if bx - 5 <= mx <= bx + bw + 5 and by - 5 <= my <= by + bh + 5:
                    if self.denom != d:
                        self.prev_denom = self.denom
                        self.denom = d
                        self.denom_transition = 0
                        self.spawn_particles(700, 420, 40, "spark")
                        self.button_press_time[d] = self.time

            # Auto button
            if 50 <= mx <= 190 and 430 <= my <= 490:
                self.auto_mode = not self.auto_mode
                self.button_press_time["auto"] = self.time

            # Reset button
            if 210 <= mx <= 350 and 430 <= my <= 490:
                self.inflation = 7.0
                self.years = 5
                self.denom = "1000"
                self.auto_mode = False
                self.spawn_particles(700, 420, 50, "spark")
                self.button_press_time["reset"] = self.time

        self.mouse_clicked = False

        # Keyboard
        def key_pressed(key):
            curr = glfw.get_key(self.window, key) == glfw.PRESS
            prev = self.keys_prev.get(key, False)
            self.keys_prev[key] = curr
            return curr and not prev

        def key_held(key):
            return glfw.get_key(self.window, key) == glfw.PRESS

        if key_pressed(glfw.KEY_ESCAPE):
            glfw.set_window_should_close(self.window, True)

        if key_held(glfw.KEY_UP) or key_held(glfw.KEY_W):
            self.inflation = min(25, self.inflation + 0.15)
        if key_held(glfw.KEY_DOWN) or key_held(glfw.KEY_S):
            self.inflation = max(0, self.inflation - 0.15)
        if key_held(glfw.KEY_RIGHT) or key_held(glfw.KEY_D):
            self.years = min(30, self.years + 0.08)
        if key_held(glfw.KEY_LEFT) or key_held(glfw.KEY_A):
            self.years = max(1, self.years - 0.08)

        denom_keys = {glfw.KEY_1: "5", glfw.KEY_2: "10", glfw.KEY_3: "20",
                      glfw.KEY_4: "50", glfw.KEY_5: "100", glfw.KEY_6: "500", glfw.KEY_7: "1000"}
        for k, d in denom_keys.items():
            if key_pressed(k) and self.denom != d:
                self.prev_denom = self.denom
                self.denom = d
                self.denom_transition = 0
                self.spawn_particles(700, 420, 40, "spark")

        if key_pressed(glfw.KEY_SPACE):
            self.auto_mode = not self.auto_mode
        if key_pressed(glfw.KEY_R):
            self.inflation = 7.0
            self.years = 5
            self.denom = "1000"
            self.auto_mode = False
            self.spawn_particles(700, 420, 50, "spark")

    def update(self, dt):
        self.time += dt

        if self.auto_mode:
            self.inflation += 4.0 * dt * self.auto_dir
            if self.inflation >= 22:
                self.auto_dir = -1
            elif self.inflation <= 1:
                self.auto_dir = 1

        self.target_scale = self.calc_scale()
        self.scale += (self.target_scale - self.scale) * min(1, dt * 5)

        # Smooth power display
        target_power = self.calc_power()
        self.displayed_power += (target_power - self.displayed_power) * min(1, dt * 8)

        # Denomination transition
        self.denom_transition = min(1, self.denom_transition + dt * 4)

        # Evaporation effect
        self.evaporate_timer += dt
        if self.evaporate_timer > 0.1:
            self.evaporate_timer = 0
            self.spawn_evaporation()

        self.particles = [p for p in self.particles if p.update(dt)]

    def draw_rect(self, x, y_top, w, h, color, filled=True):
        glDisable(GL_TEXTURE_2D)
        glColor4f(*color)
        y = flip_y(y_top) - h
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

    def draw_rounded_rect(self, x, y_top, w, h, color, radius=12):
        """Draw a rounded rectangle"""
        glDisable(GL_TEXTURE_2D)
        glColor4f(*color)
        y = flip_y(y_top) - h

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
        for cx, cy in [(x + radius, y + radius), (x + w - radius, y + radius),
                       (x + w - radius, y + h - radius), (x + radius, y + h - radius)]:
            start_angle = [(180, 270), (270, 360), (0, 90), (90, 180)][
                [(x + radius, y + radius), (x + w - radius, y + radius),
                 (x + w - radius, y + h - radius), (x + radius, y + h - radius)].index((cx, cy))]
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx, cy)
            for i in range(segments + 1):
                angle = math.radians(start_angle[0] + (start_angle[1] - start_angle[0]) * i / segments)
                glVertex2f(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
            glEnd()

    def draw_panel(self, x, y_top, w, h, title=None, accent_color=(1.0, 0.75, 0.0)):
        # Shadow
        self.draw_rounded_rect(x + 6, y_top + 6, w, h, (0.0, 0.0, 0.0, 0.4))
        # Background
        self.draw_rounded_rect(x, y_top, w, h, (0.06, 0.08, 0.12, 0.98))
        # Border glow
        glLineWidth(2)
        glColor4f(*accent_color, 0.3)
        y = flip_y(y_top) - h
        glBegin(GL_LINE_LOOP)
        for i in range(40):
            angle = 2 * math.pi * i / 40
            r = 12
            if i < 10:
                px, py = x + r + (w - 2*r) * i / 10, y
            elif i < 20:
                px, py = x + w, y + r + (h - 2*r) * (i - 10) / 10
            elif i < 30:
                px, py = x + w - r - (w - 2*r) * (i - 20) / 10, y + h
            else:
                px, py = x, y + h - r - (h - 2*r) * (i - 30) / 10
            glVertex2f(px, py)
        glEnd()

        # Top accent line
        self.draw_rect(x + 20, y_top, w - 40, 4, (*accent_color, 1.0))

        if title:
            self.text.render(title, x + 25, y_top + 22, size=28, color=(*accent_color, 1))

    def draw_slider(self, x, y_top, w, h, value, max_val, color, label, show_val):
        # Label
        self.text.render(label, x, y_top - 40, size=24, color=(0.8, 0.82, 0.88, 1))
        # Value - larger and colored
        self.text.render(show_val, x + w - 100, y_top - 40, size=28, color=(*color, 1))

        # Track background with gradient effect
        self.draw_rounded_rect(x, y_top, w, h, (0.1, 0.12, 0.18, 1.0), radius=h//2)

        # Glow under fill
        fill_w = max(h, w * (value / max_val))
        if fill_w > h:
            self.draw_rounded_rect(x - 2, y_top - 2, fill_w + 4, h + 4, (*color, 0.2), radius=h//2 + 2)

        # Fill
        if fill_w > 0:
            self.draw_rounded_rect(x, y_top, fill_w, h, (*color, 0.9), radius=h//2)

        # Handle - LARGER for touch
        handle_size = h + 20
        handle_x = x + fill_w - handle_size // 2
        handle_x = max(x, min(x + w - handle_size, handle_x))
        handle_y = y_top - 10

        # Handle glow
        self.draw_rounded_rect(handle_x - 3, handle_y - 3, handle_size + 6, handle_size + 6,
                              (*color, 0.4), radius=handle_size//2 + 3)
        # Handle body
        self.draw_rounded_rect(handle_x, handle_y, handle_size, handle_size,
                              (1, 1, 1, 0.95), radius=handle_size//2)
        # Handle inner color
        self.draw_rounded_rect(handle_x + 4, handle_y + 4, handle_size - 8, handle_size - 8,
                              (*color, 0.8), radius=(handle_size - 8)//2)

    def draw_button(self, x, y_top, w, h, label, selected=False, hover=False, color=None):
        # Press animation
        press_scale = 1.0
        if label in self.button_press_time:
            elapsed = self.time - self.button_press_time[label]
            if elapsed < 0.15:
                press_scale = 1.0 - 0.1 * math.sin(elapsed / 0.15 * math.pi)

        # Adjust for press
        if press_scale != 1.0:
            dx = w * (1 - press_scale) / 2
            dy = h * (1 - press_scale) / 2
            x += dx
            y_top += dy
            w *= press_scale
            h *= press_scale

        if selected:
            bg = color if color else (0.20, 0.75, 0.45, 1.0)
            text_col = (0.02, 0.02, 0.02, 1)
            # Glow
            self.draw_rounded_rect(x - 4, y_top - 4, w + 8, h + 8, (*bg[:3], 0.3), radius=14)
        elif hover:
            bg = (0.2, 0.25, 0.35, 1.0)
            text_col = (1, 1, 1, 1)
        else:
            bg = (0.1, 0.12, 0.18, 1.0)
            text_col = (0.75, 0.78, 0.85, 1)

        self.draw_rounded_rect(x, y_top, w, h, bg, radius=10)

        # Border
        glLineWidth(2)
        glColor4f(0.3, 0.35, 0.45, 1.0)

        self.text.render(label, x + w // 2, y_top + h // 2 - 12, size=24, color=text_col, center=True)

    def draw_money(self):
        power = self.calc_power()
        pulse = 1.0 + math.sin(self.time * 2.0) * 0.015
        scale = self.scale * pulse

        # Transition effect
        trans = ease_out_cubic(self.denom_transition)

        base_w = 380
        base_h = 190

        cx = 700
        cy_top = 420
        cy_gl = flip_y(cy_top)

        # GHOST OUTLINE - shows original size
        ghost_w = base_w
        ghost_h = base_h
        ghost_x = cx - ghost_w / 2
        ghost_y = cy_gl - ghost_h / 2

        # Draw dashed ghost outline
        glDisable(GL_TEXTURE_2D)
        glLineWidth(3)
        glColor4f(1, 1, 1, 0.15 + 0.1 * math.sin(self.time * 3))
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(2, 0xAAAA)
        glBegin(GL_LINE_LOOP)
        glVertex2f(ghost_x, ghost_y)
        glVertex2f(ghost_x + ghost_w, ghost_y)
        glVertex2f(ghost_x + ghost_w, ghost_y + ghost_h)
        glVertex2f(ghost_x, ghost_y + ghost_h)
        glEnd()
        glDisable(GL_LINE_STIPPLE)

        # "ORIGINAL VALUE" label
        self.text.render("Original Size", cx, cy_top - 135, size=16,
                        color=(0.5, 0.5, 0.5, 0.7), center=True)

        # Current money size
        w = base_w * scale
        h = base_h * scale
        x = cx - w / 2
        y = cy_gl - h / 2

        # Dramatic glow based on value loss
        glow_color = DENOM_INFO[self.denom]["color"]
        loss = 100 - power
        glow_intensity = 0.15 + loss / 100 * 0.25

        for i in range(8):
            gs = 1.08 + i * 0.04
            ga = glow_intensity - i * 0.02
            if ga > 0:
                gw, gh = w * gs, h * gs
                gx, gy = cx - gw / 2, cy_gl - gh / 2
                glColor4f(*glow_color, ga * trans)
                glBegin(GL_QUADS)
                glVertex2f(gx, gy)
                glVertex2f(gx + gw, gy)
                glVertex2f(gx + gw, gy + gh)
                glVertex2f(gx, gy + gh)
                glEnd()

        # Money texture
        u0, v0, u1, v1 = self.get_uv(self.denom)

        # Color tint based on value loss - more dramatic
        r, g, b = 1.0, 1.0, 1.0
        if power < 70:
            factor = power / 70
            # Shift toward red/desaturated as value drops
            r = 1.0
            g = 0.5 + 0.5 * factor
            b = 0.5 + 0.5 * factor

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.money_texture)
        glColor4f(r, g, b, trans)

        glBegin(GL_QUADS)
        glTexCoord2f(u0, v0); glVertex2f(x, y)
        glTexCoord2f(u1, v0); glVertex2f(x + w, y)
        glTexCoord2f(u1, v1); glVertex2f(x + w, y + h)
        glTexCoord2f(u0, v1); glVertex2f(x, y + h)
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # Value loss indicator
        if power < 100:
            loss_text = f"-{100-power:.1f}%"
            self.text.render(loss_text, cx + w/2 + 30, cy_top - 20, size=32,
                            color=(0.95, 0.3, 0.25, 0.9))

    def draw_timeline(self):
        """Draw year-by-year value timeline"""
        x_start = 430
        y_top = 680
        width = 540
        height = 80

        # Background
        self.draw_rounded_rect(x_start - 10, y_top - 10, width + 20, height + 30,
                              (0.05, 0.06, 0.1, 0.8), radius=8)

        years_to_show = min(int(self.years) + 1, 16)
        step = width / max(1, years_to_show - 1) if years_to_show > 1 else width

        # Draw timeline
        glLineWidth(2)
        glColor4f(0.3, 0.35, 0.45, 1)
        glBegin(GL_LINES)
        glVertex2f(x_start, flip_y(y_top + height//2))
        glVertex2f(x_start + width, flip_y(y_top + height//2))
        glEnd()

        # Draw year markers and values
        for i in range(years_to_show):
            x = x_start + i * step
            y_gl = flip_y(y_top + height//2)

            # Calculate value at this year
            power_at_year = 100 / ((1 + self.inflation / 100) ** i)
            bar_height = (power_at_year / 100) * 50

            # Color gradient from green to red
            if power_at_year > 70:
                color = (0.2, 0.8, 0.4)
            elif power_at_year > 40:
                color = (0.95, 0.75, 0.2)
            else:
                color = (0.95, 0.35, 0.25)

            # Value bar
            glColor4f(*color, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(x - 8, y_gl)
            glVertex2f(x + 8, y_gl)
            glVertex2f(x + 8, y_gl + bar_height)
            glVertex2f(x - 8, y_gl + bar_height)
            glEnd()

            # Year label
            if i % max(1, years_to_show // 8) == 0 or i == years_to_show - 1:
                self.text.render(f"Y{i}", x, y_top + height + 5, size=14,
                                color=(0.6, 0.65, 0.75, 1), center=True)

    def draw_left_panel(self):
        self.draw_panel(30, 80, 370, 430, "CONTROLS", (0.3, 0.7, 1.0))

        power = self.displayed_power

        # Inflation slider - LARGER
        self.draw_slider(50, 200, 320, 40, self.inflation, 25,
                        (0.95, 0.4, 0.3), "Inflation Rate", f"{self.inflation:.1f}%")

        # Years slider - LARGER
        self.draw_slider(50, 320, 320, 40, self.years - 1, 29,
                        (0.3, 0.6, 0.9), "Time Period", f"{int(self.years)} years")

        # Purchasing power display - MORE PROMINENT
        pwr_color = (0.2, 0.85, 0.5) if power > 70 else ((0.95, 0.75, 0.2) if power > 40 else (0.95, 0.35, 0.25))

        self.text.render("Purchasing Power", 50, 400, size=22, color=(0.7, 0.72, 0.78, 1))

        # Large power display with background
        self.draw_rounded_rect(50, 430, 150, 55, (*pwr_color, 0.15), radius=8)
        self.text.render(f"{power:.1f}%", 125, 442, size=48, color=(*pwr_color, 1), center=True)

        # Value lost
        lost = 100 - power
        self.text.render(f"Lost: {lost:.1f}%", 220, 450, size=20, color=(0.6, 0.62, 0.68, 1))

        # Buttons - LARGER for touch
        mx, my = self.mouse_x, self.mouse_y
        auto_hover = 50 <= mx <= 190 and 500 <= my <= 560
        reset_hover = 210 <= mx <= 350 and 500 <= my <= 560

        self.draw_button(50, 500, 140, 60, "AUTO", self.auto_mode, auto_hover,
                        (0.3, 0.75, 0.5, 1) if self.auto_mode else None)
        self.draw_button(210, 500, 140, 60, "RESET", False, reset_hover)

    def draw_center_panel(self):
        info = DENOM_INFO[self.denom]
        self.draw_panel(410, 80, 580, 610, f"Rs. {self.denom}", info["color"])

        # Animal name with icon effect
        self.text.render(f"🏔️ {info['animal']}", 700, 125, size=24,
                        color=(*info["color"], 0.9), center=True)

        # Draw money with ghost and effects
        self.draw_money()

        # Scale indicator
        scale_pct = self.scale * 100
        self.text.render(f"Current Size: {scale_pct:.0f}%", 700, 580, size=18,
                        color=(0.5, 0.52, 0.58, 1), center=True)

        # Timeline
        self.draw_timeline()

        # Denomination buttons - LARGER with better spacing
        denoms = ["5", "10", "20", "50", "100", "500", "1000"]
        mx, my = self.mouse_x, self.mouse_y
        for i, d in enumerate(denoms):
            bx = 415 + i * 90
            by = 780
            bw, bh = 82, 60
            hover = bx - 5 <= mx <= bx + bw + 5 and by - 5 <= my <= by + bh + 5
            selected = d == self.denom
            color = (*DENOM_INFO[d]["color"], 1.0) if selected else None
            self.draw_button(bx, by, bw, bh, d, selected, hover, color)

    def draw_right_panel(self):
        self.draw_panel(1010, 80, 360, 610, "💰 BUYING POWER", (1.0, 0.8, 0.3))

        power = self.displayed_power
        denom_value = DENOM_INFO[self.denom]["value"]

        self.text.render(f"What Rs.{denom_value} buys today:", 1030, 130, size=18, color=(0.75, 0.78, 0.85, 1))

        y = 170
        for name, price, unit, item_color in PURCHASE_ITEMS:
            original = denom_value / price
            current = original * (power / 100)
            ratio = min(1, current / original)

            # Color based on how much you can still buy
            if ratio > 0.7:
                bar_color = (0.25, 0.82, 0.5)
            elif ratio > 0.4:
                bar_color = (0.95, 0.75, 0.2)
            else:
                bar_color = (0.95, 0.35, 0.25)

            # Item name with subtle background
            self.draw_rounded_rect(1030, y, 320, 65, (*item_color, 0.08), radius=8)

            self.text.render(name, 1045, y + 8, size=22, color=(1, 1, 1, 1))

            # Quantity comparison
            qty_text = f"{current:.1f} / {original:.1f} {unit}"
            self.text.render(qty_text, 1330, y + 8, size=16, color=(0.7, 0.72, 0.78, 1))

            # Progress bar background
            self.draw_rounded_rect(1045, y + 40, 290, 16, (0.1, 0.12, 0.18, 1.0), radius=8)

            # Progress bar fill
            if ratio > 0:
                self.draw_rounded_rect(1045, y + 40, 290 * ratio, 16, (*bar_color, 0.9), radius=8)

            # Loss indicator
            if ratio < 1:
                loss_pct = (1 - ratio) * 100
                self.text.render(f"-{loss_pct:.0f}%", 1345, y + 38, size=14,
                                color=(0.95, 0.4, 0.35, 0.8))

            y += 80

    def draw_particles(self):
        glDisable(GL_TEXTURE_2D)
        for p in self.particles:
            alpha = (p.life / p.max_life) ** 0.7
            size = p.size * (0.3 + 0.7 * alpha)

            if p.type == "evaporate":
                # Smoke-like particles
                glColor4f(*p.color, alpha * 0.5)
                segments = 8
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(p.x, p.y)
                for i in range(segments + 1):
                    angle = 2 * math.pi * i / segments
                    glVertex2f(p.x + math.cos(angle) * size,
                              p.y + math.sin(angle) * size)
                glEnd()
            else:
                # Sparkle particles
                glColor4f(*p.color, alpha * 0.9)
                glBegin(GL_QUADS)
                glVertex2f(p.x - size, p.y - size)
                glVertex2f(p.x + size, p.y - size)
                glVertex2f(p.x + size, p.y + size)
                glVertex2f(p.x - size, p.y + size)
                glEnd()

    def draw_header(self):
        # Title with glow
        title = "🇳🇵 NEPAL INFLATION VISUALIZER"

        # Glow
        for i in range(3):
            offset = i * 0.5
            alpha = 0.15 - i * 0.04
            self.text.render(title, 700, 20 + offset, size=44,
                            color=(1, 0.85, 0.2, alpha), center=True)

        # Main title
        self.text.render(title, 700, 20, size=44,
                        color=(1, 0.9, 0.3, 1), center=True)

        # Subtitle
        self.text.render("See how inflation erodes your money's value over time",
                        700, 60, size=18, color=(0.6, 0.62, 0.68, 1), center=True)

    def draw(self):
        # Dark gradient background
        glClearColor(0.03, 0.04, 0.06, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Subtle grid pattern
        glColor4f(0.08, 0.1, 0.14, 0.5)
        glLineWidth(1)
        for i in range(0, WINDOW_WIDTH, 40):
            glBegin(GL_LINES)
            glVertex2f(i, 0)
            glVertex2f(i, WINDOW_HEIGHT)
            glEnd()
        for i in range(0, WINDOW_HEIGHT, 40):
            glBegin(GL_LINES)
            glVertex2f(0, i)
            glVertex2f(WINDOW_WIDTH, i)
            glEnd()

        # Header
        self.draw_header()

        # Panels
        self.draw_left_panel()
        self.draw_center_panel()
        self.draw_right_panel()

        # Particles on top
        self.draw_particles()

        # Footer
        self.text.render("W/S: Inflation • A/D: Years • 1-7: Notes • SPACE: Auto • R: Reset • ESC: Exit",
                        700, 865, size=15, color=(0.4, 0.42, 0.48, 1), center=True)

    def run(self):
        if not self.init():
            return

        print("\n" + "=" * 60)
        print("  🇳🇵 NEPAL INFLATION VISUALIZER - Enhanced Edition")
        print("  Touch-friendly • Beautiful visualizations")
        print("=" * 60 + "\n")

        last_time = glfw.get_time()

        while not glfw.window_should_close(self.window):
            curr_time = glfw.get_time()
            dt = min(curr_time - last_time, 0.1)
            last_time = curr_time

            glfw.poll_events()
            self.handle_input()
            self.update(dt)
            self.draw()
            glfw.swap_buffers(self.window)

        glfw.terminate()
        print("\nThank you for exploring inflation! 🙏")


def main():
    print("=" * 60)
    print("  🇳🇵 NEPAL INFLATION VISUALIZER - Enhanced Edition")
    print("=" * 60)
    print("\n  FEATURES:")
    print("    ✓ Ghost outline shows original money size")
    print("    ✓ Particles show value evaporating")
    print("    ✓ Year-by-year timeline visualization")
    print("    ✓ Touch-friendly large controls")
    print("    ✓ Real purchasing power comparison")
    print("\n  CONTROLS:")
    print("    Mouse/Touch: Drag sliders and tap buttons")
    print("    W/S: Inflation • A/D: Years")
    print("    1-7: Select note • SPACE: Auto mode")
    print("    R: Reset • ESC: Exit\n")
    print("=" * 60)

    try:
        game = InflationGame()
        game.run()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nInstall: pip install PyOpenGL glfw pillow numpy")


if __name__ == "__main__":
    main()
