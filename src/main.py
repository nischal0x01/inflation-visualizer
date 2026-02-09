"""
🇳🇵 Nepal Inflation Visualizer - Enhanced Edition
==================================================
Beautiful, modular visualization of how inflation affects purchasing power.

Architecture:
  - formulas.py: Pure financial calculations
  - config.json: Centralized configuration and data
  - ui_theme.py: Color palette and styling constants
  - graphics_utils.py: Reusable OpenGL drawing functions
  - main.py: Application logic and rendering

Controls:
  Mouse/Touch: Drag sliders, tap buttons
  W/S or UP/DOWN: Inflation
  A/D or LEFT/RIGHT: Years
  1-7: Select denomination
  SPACE: Toggle auto mode
  R: Reset | ESC: Exit
"""

import glfw
from OpenGL.GL import *
from PIL import Image
import numpy as np
import json
import math
import os
import random
from pathlib import Path

# Local imports
import formulas as calc
import ui_theme
from graphics_utils import GLDrawer, TextRenderer, flip_y


# ============ CONFIG LOADING ============

def load_config():
    """Load configuration from JSON."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, 'r') as f:
        return json.load(f)


CONFIG = load_config()
WINDOW_WIDTH = CONFIG["window"]["width"]
WINDOW_HEIGHT = CONFIG["window"]["height"]
DENOMINATIONS = CONFIG["denominatons"]
MONEY_REGIONS = CONFIG["money_regions"]
PURCHASE_ITEMS = CONFIG["purchase_items"]
CONTROLS = CONFIG["controls"]
TEXT = CONFIG["text"]


# ============ PARTICLE SYSTEM ============


class Particle:
    """Individual particle for visual effects."""
    
    def __init__(self, x: float, y: float, color: tuple, particle_type: str = "spark"):
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

    def update(self, dt: float) -> bool:
        """Update particle. Returns True if still alive."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rot_speed * dt

        if self.type == "evaporate":
            self.vx += random.uniform(-20, 20) * dt
            self.vy += 10 * dt
        elif self.type == "money_dust":
            self.vy -= 150 * dt
            self.vx *= 0.99
        else:
            self.vy -= 400 * dt

        self.life -= dt
        return self.life > 0




# ============ MAIN APPLICATION ============

class InflationVisualizer:
    """Main application class."""
    
    def __init__(self):
        self.window = None
        self.drawer = None
        self.text_renderer = None
        self.money_texture = None
        self.atlas_w = 0
        self.atlas_h = 0

        # State
        self.inflation = CONFIG["defaults"]["inflation"]
        self.years = CONFIG["defaults"]["years"]
        self.denom = CONFIG["defaults"]["denomination"]
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
        self.prev_denom = self.denom
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

    def init(self) -> bool:
        """Initialize OpenGL and window."""
        if not glfw.init():
            return False

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.RESIZABLE, False)

        self.window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT,
            TEXT["title"], None, None)
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

        self.drawer = GLDrawer(WINDOW_HEIGHT)
        self.text_renderer = self.drawer.text_renderer
        return True

    def _on_mouse_move(self, window, x: float, y: float):
        self.mouse_x = x
        self.mouse_y = y

    def _on_mouse_button(self, window, button: int, action: int, mods: int):
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

    def _load_texture(self) -> bool:
        """Load money sprite texture."""
        paths = ["assets/fullmoneyasset.jpg", "fullmoneyasset.jpg"]

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

            print(f"✓ Loaded texture: {self.atlas_w}x{self.atlas_h}")
            return True
        except Exception as e:
            print(f"Error loading texture: {e}")
            return False

    def get_uv(self, denom: str) -> tuple:
        """Get UV coordinates for denomination."""
        x, y, w, h = [int(v) for v in MONEY_REGIONS[denom]]
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

    def spawn_particles(self, x: float, y_top: float, count: int = 25, particle_type: str = "spark"):
        """Spawn particles at location."""
        color = DENOMINATIONS[self.denom]["color"]
        gl_y = flip_y(y_top, WINDOW_HEIGHT)
        for _ in range(count):
            self.particles.append(Particle(x, gl_y, color, particle_type))

    def spawn_evaporation(self):
        """Spawn particles showing money value evaporating."""
        power = self.calc_power()
        if power < 95:
            color = DENOMINATIONS[self.denom]["color"]
            cx = 700
            cy_gl = flip_y(420, WINDOW_HEIGHT)

            base_w = ui_theme.MONEY_WIDTH * self.scale
            base_h = ui_theme.MONEY_HEIGHT * self.scale

            for _ in range(2):
                edge_x = cx + random.uniform(-base_w/2, base_w/2)
                edge_y = cy_gl + base_h/2 + random.uniform(-10, 10)
                self.particles.append(Particle(edge_x, edge_y, color, "evaporate"))

    def handle_input(self):
        """Process keyboard and mouse input."""
        mx, my = self.mouse_x, self.mouse_y

        # Slider interaction
        inflation_slider = CONTROLS["slider_inflation"]
        years_slider = CONTROLS["slider_years"]

        if self.mouse_pressed:
            # Inflation slider
            if self.dragging_inflation or (self.mouse_clicked and
                inflation_slider[0] - 20 <= mx <= inflation_slider[0] + inflation_slider[2] + 20 and
                inflation_slider[1] - 20 <= my <= inflation_slider[1] + inflation_slider[3] + 20):
                self.dragging_inflation = True
                ratio = (mx - inflation_slider[0]) / inflation_slider[2]
                ratio = max(0, min(1, ratio))
                self.inflation = ratio * 25

            # Years slider
            elif self.dragging_years or (self.mouse_clicked and
                years_slider[0] - 20 <= mx <= years_slider[0] + years_slider[2] + 20 and
                years_slider[1] - 20 <= my <= years_slider[1] + years_slider[3] + 20):
                self.dragging_years = True
                ratio = (mx - years_slider[0]) / years_slider[2]
                ratio = max(0, min(1, ratio))
                self.years = 1 + ratio * 29

        # Button clicks
        if self.mouse_clicked:
            # Denomination buttons
            denoms = list(DENOMINATIONS.keys())
            for i, d in enumerate(denoms):
                bx = CONTROLS["denomination_buttons_start_x"] + i * CONTROLS["denomination_button_spacing"]
                by = CONTROLS["denomination_buttons_y"]
                bw = CONTROLS["denomination_button_width"]
                bh = CONTROLS["denomination_button_height"]
                if bx - 5 <= mx <= bx + bw + 5 and by - 5 <= my <= by + bh + 5:
                    if self.denom != d:
                        self.prev_denom = self.denom
                        self.denom = d
                        self.denom_transition = 0
                        self.button_press_time[d] = self.time

            # Auto button
            auto_btn = CONTROLS["button_auto"]
            if auto_btn[0] <= mx <= auto_btn[0] + auto_btn[2] and auto_btn[1] <= my <= auto_btn[1] + auto_btn[3]:
                self.auto_mode = not self.auto_mode
                self.button_press_time["auto"] = self.time

            # Reset button
            reset_btn = CONTROLS["button_reset"]
            if reset_btn[0] <= mx <= reset_btn[0] + reset_btn[2] and reset_btn[1] <= my <= reset_btn[1] + reset_btn[3]:
                self.reset()

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

        denom_keys = {
            glfw.KEY_1: "5", glfw.KEY_2: "10", glfw.KEY_3: "20",
            glfw.KEY_4: "50", glfw.KEY_5: "100", glfw.KEY_6: "500", glfw.KEY_7: "1000"
        }
        for k, d in denom_keys.items():
            if key_pressed(k) and self.denom != d:
                self.prev_denom = self.denom
                self.denom = d
                self.denom_transition = 0

        if key_pressed(glfw.KEY_SPACE):
            self.auto_mode = not self.auto_mode
        if key_pressed(glfw.KEY_R):
            self.reset()

    def reset(self):
        """Reset to default state."""
        self.inflation = CONFIG["defaults"]["inflation"]
        self.years = CONFIG["defaults"]["years"]
        self.denom = CONFIG["defaults"]["denomination"]
        self.auto_mode = False
        self.button_press_time["reset"] = self.time

    def update(self, dt: float):
        """Update simulation state."""
        self.time += dt

        if self.auto_mode:
            self.inflation += 4.0 * dt * self.auto_dir
            if self.inflation >= 22:
                self.auto_dir = -1
            elif self.inflation <= 1:
                self.auto_dir = 1

        self.target_scale = self.calc_scale()
        self.scale += (self.target_scale - self.scale) * min(1, dt * ui_theme.SCALE_ANIMATION_SPEED)

        target_power = self.calc_power()
        self.displayed_power += (target_power - self.displayed_power) * min(1, dt * ui_theme.POWER_ANIMATION_SPEED)

        self.denom_transition = min(1, self.denom_transition + dt * ui_theme.DENOM_TRANSITION_SPEED)

        # Particles disabled for clean UI

    def draw_money(self):
        """Draw money with clean visual effects."""
        power = self.calc_power()
        scale = self.scale  # Clean scale without wobble

        trans = calc.ease_out_cubic(self.denom_transition)

        cx = 700
        cy_top = 420
        cy_gl = flip_y(cy_top, WINDOW_HEIGHT)

        # Ghost outline (static, clean)
        ghost_w = ui_theme.MONEY_WIDTH
        ghost_h = ui_theme.MONEY_HEIGHT
        ghost_x = cx - ghost_w / 2
        ghost_y = cy_gl - ghost_h / 2

        glDisable(GL_TEXTURE_2D)
        glLineWidth(2)
        glColor4f(1, 1, 1, 0.2)  # Static opacity
        glBegin(GL_LINE_LOOP)
        glVertex2f(ghost_x, ghost_y)
        glVertex2f(ghost_x + ghost_w, ghost_y)
        glVertex2f(ghost_x + ghost_w, ghost_y + ghost_h)
        glVertex2f(ghost_x, ghost_y + ghost_h)
        glEnd()

        self.text_renderer.render(TEXT["original_size"], cx, cy_top - 135, WINDOW_HEIGHT,
                                 size=16, color=(0.5, 0.5, 0.5, 0.7), center=True)

        # Current money
        w = ui_theme.MONEY_WIDTH * scale
        h = ui_theme.MONEY_HEIGHT * scale
        x = cx - w / 2
        y = cy_gl - h / 2

        # Subtle shadow under money
        shadow_offset = 4
        glColor4f(0, 0, 0, 0.25 * trans)
        glBegin(GL_QUADS)
        glVertex2f(x + shadow_offset, y - shadow_offset)
        glVertex2f(x + w + shadow_offset, y - shadow_offset)
        glVertex2f(x + w + shadow_offset, y + h - shadow_offset)
        glVertex2f(x + shadow_offset, y + h - shadow_offset)
        glEnd()

        # Money texture
        u0, v0, u1, v1 = self.get_uv(self.denom)

        r, g, b = 1.0, 1.0, 1.0
        if power < 70:
            factor = power / 70
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
            self.text_renderer.render(loss_text, cx + w/2 + 30, cy_top - 20, WINDOW_HEIGHT,
                                     size=32, color=(0.95, 0.3, 0.25, 0.9))

    def draw_timeline(self):
        """Draw year-by-year value timeline."""
        x_start = 430
        y_top = 680
        width = 540
        height = 80

        self.drawer.draw_rounded_rect(x_start - 10, y_top - 10, width + 20, height + 30,
                                     (0.05, 0.06, 0.1, 0.8), radius=8)

        years_to_show = min(int(self.years) + 1, 16)
        step = width / max(1, years_to_show - 1) if years_to_show > 1 else width

        glLineWidth(2)
        glColor4f(0.3, 0.35, 0.45, 1)
        glBegin(GL_LINES)
        glVertex2f(x_start, flip_y(y_top + height//2, WINDOW_HEIGHT))
        glVertex2f(x_start + width, flip_y(y_top + height//2, WINDOW_HEIGHT))
        glEnd()

        for i in range(years_to_show):
            x = x_start + i * step
            y_gl = flip_y(y_top + height//2, WINDOW_HEIGHT)

            power_at_year = calc.calculate_purchasing_power(self.inflation, i)
            bar_height = (power_at_year / 100) * 50

            color = calc.get_color_for_value(power_at_year)

            glColor4f(*color, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(x - 8, y_gl)
            glVertex2f(x + 8, y_gl)
            glVertex2f(x + 8, y_gl + bar_height)
            glVertex2f(x - 8, y_gl + bar_height)
            glEnd()

            if i % max(1, years_to_show // 8) == 0 or i == years_to_show - 1:
                self.text_renderer.render(f"Y{i}", x, y_top + height + 5, WINDOW_HEIGHT,
                                         size=14, color=(0.6, 0.65, 0.75, 1), center=True)

    def draw_left_panel(self):
        """Draw controls panel."""
        self.drawer.draw_panel(ui_theme.PANEL_LEFT_X, ui_theme.PANEL_Y, 
                              ui_theme.PANEL_WIDTH_SIDE, ui_theme.PANEL_HEIGHT,
                              TEXT["controls"], ui_theme.ACCENT_BLUE)

        power = self.displayed_power

        self.drawer.draw_slider(50, 200, 320, 40, self.inflation, 25,
                               (0.95, 0.4, 0.3), TEXT["inflation_rate"], f"{self.inflation:.1f}%")

        self.drawer.draw_slider(50, 320, 320, 40, self.years - 1, 29,
                               (0.3, 0.6, 0.9), TEXT["time_period"], f"{int(self.years)} {TEXT['years_label']}")

        pwr_color = calc.get_color_for_value(power)

        self.text_renderer.render(TEXT["purchasing_power"], 50, 400, WINDOW_HEIGHT,
                                 size=22, color=(0.7, 0.72, 0.78, 1))

        self.drawer.draw_rounded_rect(50, 430, 150, 55, (*pwr_color, 0.15), radius=8)
        self.text_renderer.render(f"{power:.1f}%", 125, 442, WINDOW_HEIGHT,
                                 size=48, color=(*pwr_color, 1), center=True)

        lost = 100 - power
        self.text_renderer.render(f"{TEXT['lost_label']} {lost:.1f}%", 220, 450, WINDOW_HEIGHT,
                                 size=20, color=(0.6, 0.62, 0.68, 1))

        mx, my = self.mouse_x, self.mouse_y
        auto_hover = CONTROLS["button_auto"][0] <= mx <= CONTROLS["button_auto"][0] + CONTROLS["button_auto"][2] and \
                    CONTROLS["button_auto"][1] <= my <= CONTROLS["button_auto"][1] + CONTROLS["button_auto"][3]
        reset_hover = CONTROLS["button_reset"][0] <= mx <= CONTROLS["button_reset"][0] + CONTROLS["button_reset"][2] and \
                     CONTROLS["button_reset"][1] <= my <= CONTROLS["button_reset"][1] + CONTROLS["button_reset"][3]

        self.drawer.draw_button(50, 500, 140, 60, TEXT["auto_button"], self.auto_mode, auto_hover,
                               (0.3, 0.75, 0.5, 1) if self.auto_mode else None)
        self.drawer.draw_button(210, 500, 140, 60, TEXT["reset_button"], False, reset_hover)

    def draw_center_panel(self):
        """Draw money display panel."""
        info = DENOMINATIONS[self.denom]
        self.drawer.draw_panel(ui_theme.PANEL_CENTER_X, ui_theme.PANEL_Y,
                              ui_theme.PANEL_WIDTH_CENTER, ui_theme.PANEL_HEIGHT,
                              f"Rs. {self.denom}", info["color"])

        self.text_renderer.render(f"🏔️ {info['animal']}", 700, 125, WINDOW_HEIGHT,
                                 size=24, color=(*info["color"], 0.9), center=True)

        self.draw_money()

        scale_pct = self.scale * 100
        self.text_renderer.render(f"{TEXT['current_size']} {scale_pct:.0f}%", 700, 580, WINDOW_HEIGHT,
                                 size=18, color=(0.5, 0.52, 0.58, 1), center=True)

        self.draw_timeline()

        denoms = list(DENOMINATIONS.keys())
        mx, my = self.mouse_x, self.mouse_y
        for i, d in enumerate(denoms):
            bx = CONTROLS["denomination_buttons_start_x"] + i * CONTROLS["denomination_button_spacing"]
            by = CONTROLS["denomination_buttons_y"]
            bw = CONTROLS["denomination_button_width"]
            bh = CONTROLS["denomination_button_height"]
            hover = bx - 5 <= mx <= bx + bw + 5 and by - 5 <= my <= by + bh + 5
            selected = d == self.denom
            color = (*DENOMINATIONS[d]["color"], 1.0) if selected else None
            self.drawer.draw_button(bx, by, bw, bh, d, selected, hover, color)

    def draw_right_panel(self):
        """Draw buying power comparison panel."""
        self.drawer.draw_panel(ui_theme.PANEL_RIGHT_X, ui_theme.PANEL_Y,
                              ui_theme.PANEL_WIDTH_RIGHT, ui_theme.PANEL_HEIGHT,
                              TEXT["buying_power"], ui_theme.ACCENT_GOLD)

        power = self.displayed_power
        denom_value = DENOMINATIONS[self.denom]["value"]

        what_buys = TEXT["what_buys_today"].format(denom=denom_value)
        self.text_renderer.render(what_buys, 1030, 130, WINDOW_HEIGHT,
                                 size=18, color=(0.75, 0.78, 0.85, 1))

        y = 170
        for item in PURCHASE_ITEMS:
            name = item["name"]
            price = item["price"]
            unit = item["unit"]
            item_color = item["color"]

            current, original = calc.calculate_purchasing_quantity(denom_value, price, power)
            ratio = min(1, current / original) if original > 0 else 0

            if ratio > 0.7:
                bar_color = (0.25, 0.82, 0.5)
            elif ratio > 0.4:
                bar_color = (0.95, 0.75, 0.2)
            else:
                bar_color = (0.95, 0.35, 0.25)

            self.drawer.draw_rounded_rect(1030, y, 320, 65, (*item_color, 0.08), radius=8)

            self.text_renderer.render(name, 1045, y + 8, WINDOW_HEIGHT,
                                     size=22, color=(1, 1, 1, 1))

            qty_text = f"{current:.1f} / {original:.1f} {unit}"
            self.text_renderer.render(qty_text, 1330, y + 8, WINDOW_HEIGHT,
                                     size=16, color=(0.7, 0.72, 0.78, 1))

            self.drawer.draw_rounded_rect(1045, y + 40, 290, 16, (0.1, 0.12, 0.18, 1.0), radius=8)

            if ratio > 0:
                self.drawer.draw_rounded_rect(1045, y + 40, 290 * ratio, 16, (*bar_color, 0.9), radius=8)

            if ratio < 1:
                loss_pct = (1 - ratio) * 100
                self.text_renderer.render(f"-{loss_pct:.0f}%", 1345, y + 38, WINDOW_HEIGHT,
                                         size=14, color=(0.95, 0.4, 0.35, 0.8))

            y += 80

    def draw_particles(self):
        """Draw particle effects."""
        glDisable(GL_TEXTURE_2D)
        for p in self.particles:
            alpha = (p.life / p.max_life) ** 0.7
            size = p.size * (0.3 + 0.7 * alpha)

            if p.type == "evaporate":
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
                glColor4f(*p.color, alpha * 0.9)
                glBegin(GL_QUADS)
                glVertex2f(p.x - size, p.y - size)
                glVertex2f(p.x + size, p.y - size)
                glVertex2f(p.x + size, p.y + size)
                glVertex2f(p.x - size, p.y + size)
                glEnd()

    def draw_header(self):
        """Draw title and subtitle."""
        title = TEXT["title"]

        # Clean title without glow
        self.text_renderer.render(title, 700, 20, WINDOW_HEIGHT, size=44,
                                 color=(1, 0.9, 0.3, 1), center=True)

        self.text_renderer.render(TEXT["subtitle"], 700, 60, WINDOW_HEIGHT,
                                 size=18, color=(0.6, 0.62, 0.68, 1), center=True)

    def draw(self):
        """Render frame."""
        glClearColor(*ui_theme.BG_DARK_PRIMARY)
        glClear(GL_COLOR_BUFFER_BIT)

        self.drawer.draw_grid(WINDOW_WIDTH, WINDOW_HEIGHT, ui_theme.GRID_SIZE)

        self.draw_header()
        self.draw_left_panel()
        self.draw_center_panel()
        self.draw_right_panel()
        # Particles disabled for clean UI

        self.text_renderer.render(TEXT["footer"], 700, 865, WINDOW_HEIGHT,
                                 size=15, color=(0.4, 0.42, 0.48, 1), center=True)

    def run(self):
        """Main application loop."""
        if not self.init():
            return

        print("\n" + "=" * 70)
        print("  🇳🇵 NEPAL INFLATION VISUALIZER - Enhanced Edition")
        print("  Modular • Beautiful • Efficient")
        print("=" * 70 + "\n")

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
        print("\nThank you for exploring inflation! 🙏\n")


def main():
    """Entry point."""
    print("=" * 70)
    print("  🇳🇵 NEPAL INFLATION VISUALIZER - Enhanced Edition")
    print("=" * 70)
    print("\n  ARCHITECTURE:")
    print("    ✓ Modularized: formulas.py, ui_theme.py, graphics_utils.py")
    print("    ✓ Config: config.json for all data and strings")
    print("    ✓ Features: Ghost outlines, particle effects, buying power visualization")
    print("\n  CONTROLS:")
    print("    Mouse/Touch: Drag sliders, tap buttons")
    print("    W/S: Inflation • A/D: Years • 1-7: Denomination")
    print("    SPACE: Auto • R: Reset • ESC: Exit\n")
    print("=" * 70 + "\n")

    try:
        app = InflationVisualizer()
        app.run()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nInstall: pip install PyOpenGL glfw pillow numpy")


if __name__ == "__main__":
    main()
