"""
रुपैयाँको यात्रा (Rupaiyako Yatra) - The Journey of Money
Interactive Inflation and Compound Interest Visual Simulator

CONTROLS:
    SPACE - Play/Pause
    R - Reset
    1 - Inflation Mode
    2 - Compound Interest Mode
    3 - Real Return Mode
    4 - Comparison Mode (default)
    Mouse Drag - Scrub timeline
    ESC - Quit

Author: Computer Graphics Project
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from finance import InflationCalculator, CompoundCalculator, RealReturnCalculator


# ============================================================================
# CURRENCY NOTE CLASS
# ============================================================================

class CurrencyNote:
    """Visual representation of Nepali currency that scales with value"""
    
    def __init__(self, x, y, width=200, height=100):
        self.x = x
        self.y = y
        self.base_w = width
        self.base_h = height
        self.scale = 1.0
        self.target_scale = 1.0
        self.color = (0.6, 0.4, 0.5)  # Purple-brown (NPR 500 note color)
    
    def set_scale(self, scale):
        """Set target scale"""
        self.target_scale = max(0.1, scale)
    
    def update(self):
        """Smooth interpolation to target scale"""
        self.scale += (self.target_scale - self.scale) * 0.15
    
    def render(self):
        """Draw the currency note"""
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glScalef(self.scale, self.scale, 1)
        
        w, h = self.base_w, self.base_h
        
        # Main note body
        glColor3f(*self.color)
        glBegin(GL_QUADS)
        glVertex2f(-w/2, -h/2)
        glVertex2f(w/2, -h/2)
        glVertex2f(w/2, h/2)
        glVertex2f(-w/2, h/2)
        glEnd()
        
        # Border
        glColor3f(0.3, 0.2, 0.3)
        glLineWidth(3)
        glBegin(GL_LINE_LOOP)
        glVertex2f(-w/2, -h/2)
        glVertex2f(w/2, -h/2)
        glVertex2f(w/2, h/2)
        glVertex2f(-w/2, h/2)
        glEnd()
        
        # Simple "Rs" text representation
        glColor3f(1, 1, 1)
        glLineWidth(4)
        scale = 0.25
        glBegin(GL_LINES)
        # R
        glVertex2f(-40*scale, -20*scale)
        glVertex2f(-40*scale, 20*scale)
        glVertex2f(-40*scale, 20*scale)
        glVertex2f(-25*scale, 20*scale)
        glVertex2f(-25*scale, 20*scale)
        glVertex2f(-25*scale, 0)
        glVertex2f(-25*scale, 0)
        glVertex2f(-40*scale, 0)
        # s
        glVertex2f(-15*scale, 15*scale)
        glVertex2f(-5*scale, 15*scale)
        glVertex2f(-5*scale, 15*scale)
        glVertex2f(-5*scale, 0)
        glVertex2f(-5*scale, 0)
        glVertex2f(-15*scale, 0)
        glVertex2f(-15*scale, 0)
        glVertex2f(-15*scale, -15*scale)
        glVertex2f(-15*scale, -15*scale)
        glVertex2f(-5*scale, -15*scale)
        glEnd()
        
        glPopMatrix()


# ============================================================================
# MAIN APPLICATION CLASS
# ============================================================================

class RupaiyakoYatra:
    """Main application"""
    
    # Modes
    INFLATION = 0
    COMPOUND = 1
    REAL_RETURN = 2
    COMPARISON = 3
    
    def __init__(self):
        # Window setup
        self.width, self.height = 1200, 700
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("रुपैयाँको यात्रा - The Journey of Money")
        
        # OpenGL setup
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.95, 0.95, 0.97, 1.0)
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Parameters (CUSTOMIZE HERE!)
        self.initial_amount = 100000  # NPR 100,000
        self.inflation_rate = 0.06    # 6% annual
        self.interest_rate = 0.10     # 10% annual
        self.years = 10               # 10 years
        self.freq = 12                # Monthly compounding
        
        # Calculators
        self.inflation_calc = InflationCalculator(self.initial_amount, self.inflation_rate, self.years)
        self.compound_calc = CompoundCalculator(self.initial_amount, self.interest_rate, self.years, self.freq)
        self.real_calc = RealReturnCalculator(self.initial_amount, self.interest_rate, 
                                             self.inflation_rate, self.years, self.freq)
        
        # Currency notes
        self.note_single = CurrencyNote(self.width/2, self.height/2, 250, 125)
        self.note_left = CurrencyNote(self.width/4, self.height/2, 200, 100)
        self.note_right = CurrencyNote(3*self.width/4, self.height/2, 200, 100)
        self.note_nominal = CurrencyNote(self.width/2 + 30, self.height/2 + 20, 220, 110)
        self.note_real = CurrencyNote(self.width/2 - 30, self.height/2 - 20, 220, 110)
        
        # Animation state
        self.mode = self.COMPARISON
        self.time = 0.0
        self.playing = False
        self.dragging = False
        
        # Clock
        self.clock = pygame.time.Clock()
        self.fps = 60
    
    def draw_text(self, text, x, y, font=None, color=(0, 0, 0)):
        """Draw text on screen"""
        if font is None:
            font = self.font
        
        if all(c <= 1 for c in color):
            color = tuple(int(c * 255) for c in color)
        
        surf = font.render(text, True, color)
        data = pygame.image.tostring(surf, "RGBA", True)
        gl_y = self.height - y - surf.get_height()
        
        glRasterPos2f(x, gl_y)
        glDrawPixels(surf.get_width(), surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    def draw_rect(self, x, y, w, h, color, filled=True):
        """Draw rectangle"""
        glColor3f(*color)
        glBegin(GL_QUADS if filled else GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
    
    def draw_timeline(self):
        """Draw interactive timeline"""
        x, y, w = 50, 30, self.width - 100
        
        # Track
        glColor3f(0.8, 0.8, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(x, y + 11)
        glVertex2f(x + w, y + 11)
        glVertex2f(x + w, y + 19)
        glVertex2f(x, y + 19)
        glEnd()
        
        # Progress
        progress = self.time / self.years if self.years > 0 else 0
        prog_w = w * progress
        glColor3f(0.3, 0.6, 0.9)
        glBegin(GL_QUADS)
        glVertex2f(x, y + 11)
        glVertex2f(x + prog_w, y + 11)
        glVertex2f(x + prog_w, y + 19)
        glVertex2f(x, y + 19)
        glEnd()
        
        # Handle
        handle_x = x + prog_w
        glColor3f(0.2, 0.4, 0.8)
        glBegin(GL_QUADS)
        glVertex2f(handle_x - 8, y)
        glVertex2f(handle_x + 8, y)
        glVertex2f(handle_x + 8, y + 30)
        glVertex2f(handle_x - 8, y + 30)
        glEnd()
        
        # Year display
        self.draw_text(f"Year {self.time:.1f} / {self.years}", 
                      self.width/2 - 60, self.height - y - 35)
    
    def draw_info_box(self, x, y, w, h, title, data, color):
        """Draw info panel"""
        # Background
        glColor4f(color[0], color[1], color[2], 0.1)
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        
        # Border
        glColor3f(*color)
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()
        
        # Title
        tc = tuple(int(c * 255) for c in color)
        self.draw_text(title, x + 10, self.height - (y + h - 10), self.font, tc)
        
        # Data
        line_y = y + h - 45
        for key, val in data.items():
            self.draw_text(f"{key}: {val}", x + 10, self.height - line_y, 
                          self.small_font, (0, 0, 0))
            line_y -= 25
    
    def update(self, dt):
        """Update animation"""
        if self.playing:
            self.time += dt
            if self.time > self.years:
                self.time = self.years
                self.playing = False
        
        # Update note scales based on mode
        if self.mode == self.INFLATION:
            data = self.inflation_calc.get_value(self.time)
            self.note_single.set_scale(data['scale'])
        
        elif self.mode == self.COMPOUND:
            data = self.compound_calc.get_value(self.time)
            self.note_single.set_scale(data['scale'])
        
        elif self.mode == self.REAL_RETURN:
            data = self.real_calc.get_value(self.time)
            self.note_nominal.set_scale(data['nominal_scale'])
            self.note_real.set_scale(data['real_scale'])
        
        elif self.mode == self.COMPARISON:
            inf_data = self.inflation_calc.get_value(self.time)
            comp_data = self.compound_calc.get_value(self.time)
            self.note_left.set_scale(inf_data['scale'])
            self.note_right.set_scale(comp_data['scale'])
        
        # Smooth update
        self.note_single.update()
        self.note_left.update()
        self.note_right.update()
        self.note_nominal.update()
        self.note_real.update()
    
    def render(self):
        """Render frame"""
        glClear(GL_COLOR_BUFFER_BIT)
        glLoadIdentity()
        
        if self.mode == self.INFLATION:
            self.render_inflation()
        elif self.mode == self.COMPOUND:
            self.render_compound()
        elif self.mode == self.REAL_RETURN:
            self.render_real_return()
        elif self.mode == self.COMPARISON:
            self.render_comparison()
        
        self.draw_timeline()
        self.draw_controls()
        pygame.display.flip()
    
    def render_inflation(self):
        """Render inflation mode"""
        self.draw_text("INFLATION - Purchasing Power Erosion", 
                      50, self.height - 50, color=(200, 50, 50))
        
        self.note_single.render()
        
        data = self.inflation_calc.get_value(self.time)
        info = {
            "Year": f"{self.time:.1f}",
            "Initial": f"NPR {self.initial_amount:,.0f}",
            "Purchasing Power": f"NPR {data['value']:,.0f}",
            "Remaining": f"{data['scale']*100:.1f}%"
        }
        self.draw_info_box(50, 100, 300, 180, "Inflation Impact", info, (0.8, 0.2, 0.2))
    
    def render_compound(self):
        """Render compound interest mode"""
        self.draw_text("COMPOUND INTEREST - Investment Growth", 
                      50, self.height - 50, color=(50, 150, 50))
        
        self.note_single.render()
        
        data = self.compound_calc.get_value(self.time)
        info = {
            "Year": f"{self.time:.1f}",
            "Principal": f"NPR {self.initial_amount:,.0f}",
            "Current Value": f"NPR {data['value']:,.0f}",
            "Gain": f"NPR {data['value'] - self.initial_amount:,.0f}"
        }
        self.draw_info_box(50, 100, 320, 180, "Investment Growth", info, (0.2, 0.6, 0.2))
    
    def render_real_return(self):
        """Render real return mode"""
        self.draw_text("REAL RETURN - Inflation-Adjusted Growth", 
                      50, self.height - 50, color=(50, 100, 200))
        
        self.note_nominal.color = (0.4, 0.7, 0.4)
        self.note_nominal.render()
        
        self.note_real.color = (0.3, 0.5, 0.8)
        self.note_real.render()
        
        self.draw_text("Nominal", self.note_nominal.x - 40, 
                      self.height - (self.note_nominal.y + 90), color=(100, 180, 100))
        self.draw_text("Real", self.note_real.x - 25, 
                      self.height - (self.note_real.y + 90), color=(80, 130, 200))
        
        data = self.real_calc.get_value(self.time)
        info = {
            "Year": f"{self.time:.1f}",
            "Principal": f"NPR {self.initial_amount:,.0f}",
            "Nominal": f"NPR {data['nominal']:,.0f}",
            "Real Value": f"NPR {data['real']:,.0f}",
            "Inflation Cost": f"NPR {data['nominal'] - data['real']:,.0f}"
        }
        self.draw_info_box(50, 80, 340, 230, "Real vs Nominal", info, (0.2, 0.4, 0.7))
    
    def render_comparison(self):
        """Render comparison mode"""
        # Divider
        glColor3f(0.7, 0.7, 0.7)
        glLineWidth(2)
        glBegin(GL_LINES)
        glVertex2f(self.width/2, 0)
        glVertex2f(self.width/2, self.height)
        glEnd()
        
        # Left - Inflation
        self.draw_text("IDLE MONEY", 50, self.height - 50, color=(200, 50, 50))
        self.draw_text("Losing to Inflation", 50, self.height - 80, 
                      self.small_font, color=(150, 50, 50))
        self.note_left.render()
        
        # Right - Investment
        self.draw_text("INVESTED MONEY", self.width/2 + 50, 
                      self.height - 50, color=(50, 150, 50))
        self.draw_text("Growing with Interest", self.width/2 + 50, 
                      self.height - 80, self.small_font, color=(50, 120, 50))
        self.note_right.render()
        
        # Info boxes
        inf_data = self.inflation_calc.get_value(self.time)
        comp_data = self.compound_calc.get_value(self.time)
        
        left_info = {
            "Initial": f"NPR {self.initial_amount:,.0f}",
            "Now Worth": f"NPR {inf_data['value']:,.0f}",
            "Lost": f"NPR {self.initial_amount - inf_data['value']:,.0f}"
        }
        self.draw_info_box(30, 100, 250, 140, f"Year {self.time:.1f}", 
                          left_info, (0.8, 0.2, 0.2))
        
        right_info = {
            "Principal": f"NPR {self.initial_amount:,.0f}",
            "Now Worth": f"NPR {comp_data['value']:,.0f}",
            "Gained": f"NPR {comp_data['value'] - self.initial_amount:,.0f}"
        }
        self.draw_info_box(self.width/2 + 30, 100, 250, 140, 
                          f"Year {self.time:.1f}", right_info, (0.2, 0.6, 0.2))
        
        # Difference
        diff = comp_data['value'] - inf_data['value']
        self.draw_text(f"Difference: NPR {diff:,.0f}", 
                      self.width/2 - 150, 60, color=(50, 50, 200))
    
    def draw_controls(self):
        """Draw control help"""
        controls = [
            "SPACE: Play/Pause",
            "R: Reset",
            "1-4: Change Mode",
            "ESC: Quit"
        ]
        y = self.height - 120
        for i, ctrl in enumerate(controls):
            self.draw_text(ctrl, self.width - 200, y - i*25, 
                          self.small_font, color=(100, 100, 100))
    
    def handle_input(self):
        """Handle events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                elif event.key == K_SPACE:
                    self.playing = not self.playing
                elif event.key == K_r:
                    self.time = 0.0
                    self.playing = False
                elif event.key == K_1:
                    self.mode = self.INFLATION
                elif event.key == K_2:
                    self.mode = self.COMPOUND
                elif event.key == K_3:
                    self.mode = self.REAL_RETURN
                elif event.key == K_4:
                    self.mode = self.COMPARISON
            
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    my = self.height - my
                    if 50 <= mx <= self.width - 50 and 30 <= my <= 60:
                        self.dragging = True
                        self.update_timeline_from_mouse(mx)
            
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            
            elif event.type == MOUSEMOTION:
                if self.dragging:
                    mx, _ = event.pos
                    self.update_timeline_from_mouse(mx)
        
        return True
    
    def update_timeline_from_mouse(self, mx):
        """Update timeline from mouse position"""
        normalized = (mx - 50) / (self.width - 100)
        normalized = max(0, min(1, normalized))
        self.time = normalized * self.years
        self.playing = False
    
    def run(self):
        """Main loop"""
        running = True
        while running:
            running = self.handle_input()
            dt = self.clock.tick(self.fps) / 1000.0
            self.update(dt)
            self.render()
        pygame.quit()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  रुपैयाँको यात्रा - The Journey of Money")
    print("  Interactive Financial Simulator")
    print("=" * 60)
    print("\nControls:")
    print("  SPACE - Play/Pause")
    print("  R - Reset")
    print("  1 - Inflation Mode")
    print("  2 - Compound Interest Mode")
    print("  3 - Real Return Mode")
    print("  4 - Comparison Mode (default)")
    print("  Drag Timeline - Scrub years")
    print("  ESC - Quit")
    print("=" * 60)
    print()
    
    app = RupaiyakoYatra()
    app.run()
