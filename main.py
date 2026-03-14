from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import random

Window.clearcolor = (0.02, 0.0, 0.08, 1)

LANES = [0.2, 0.5, 0.8]
COLORS = {
    'neon_blue': (0.0, 0.8, 1.0, 1),
    'neon_pink': (1.0, 0.0, 0.8, 1),
    'neon_green': (0.0, 1.0, 0.5, 1),
    'neon_red': (1.0, 0.1, 0.2, 1),
    'neon_yellow': (1.0, 0.9, 0.0, 1),
    'dark': (0.05, 0.05, 0.15, 1),
    'road': (0.04, 0.04, 0.14, 1),
}

class GameWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = 'menu'
        self.score = 0
        self.speed = 300
        self.lane = 1
        self.player_x = LANES[self.lane]
        self.target_x = self.player_x
        self.jump_v = 0
        self.is_jumping = False
        self.player_h = 0.0
        self.obstacles = []
        self.coins = []
        self.particles = []
        self.road_lines = [i / 6.0 for i in range(7)]
        self.touch_start = None
        self.invincible = 0
        self.shake = 0
        self.spawn_timer = 0

        self.score_label = Label(
            text='', font_size='36sp',
            color=(0, 1, 1, 1),
            size_hint=(1, None), height=50
        )
        self.add_widget(self.score_label)

        self.info_label = Label(
            text='CYBER RUNNER\n\nSwipe left/right to dodge\nSwipe up to jump\n\nTAP TO START',
            font_size='20sp', color=(0, 1, 1, 1),
            halign='center', valign='middle',
            size_hint=(0.8, 0.4),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.add_widget(self.info_label)

        Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_touch_down(self, touch):
        self.touch_start = (touch.x, touch.y)
        if self.state != 'playing':
            self.start_game()
        return True

    def on_touch_up(self, touch):
        if not self.touch_start or self.state != 'playing':
            return True
        dx = touch.x - self.touch_start[0]
        dy = touch.y - self.touch_start[1]
        if abs(dx) > 30 or abs(dy) > 30:
            if abs(dx) > abs(dy):
                if dx > 0: self.move_right()
                else: self.move_left()
            else:
                if dy > 0: self.jump()
        self.touch_start = None
        return True

    def start_game(self):
        self.state = 'playing'
        self.score = 0
        self.speed = 300
        self.lane = 1
        self.player_x = LANES[self.lane]
        self.target_x = self.player_x
        self.obstacles = []
        self.coins = []
        self.particles = []
        self.jump_v = 0
        self.is_jumping = False
        self.player_h = 0.0
        self.invincible = 0
        self.spawn_timer = 0
        self.info_label.text = ''
        self.score_label.color = (0, 1, 1, 1)

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1
            self.target_x = LANES[self.lane]

    def move_right(self):
        if self.lane < 2:
            self.lane += 1
            self.target_x = LANES[self.lane]

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_v = 0.018

    def add_particles(self, x, y, color):
        for _ in range(8):
            self.particles.append({
                'x': x, 'y': y,
                'vx': random.uniform(-0.02, 0.02),
                'vy': random.uniform(0.005, 0.025),
                'life': 1.0, 'color': color
            })

    def update(self, dt):
        dt = min(dt, 0.05)
        w = self.width or 400
        h = self.height or 700

        for i in range(len(self.road_lines)):
            self.road_lines[i] += self.speed * dt / h
            if self.road_lines[i] > 1.2:
                self.road_lines[i] -= 1.4

        if self.state == 'playing':
            self.score += dt * self.speed * 0.05
            self.speed = min(700, 300 + self.score * 0.3)
            self.score_label.text = str(int(self.score))
            self.player_x += (self.target_x - self.player_x) * 10 * dt

            if self.is_jumping:
                self.player_h += self.jump_v
                self.jump_v -= 0.0012
                if self.player_h <= 0:
                    self.player_h = 0
                    self.is_jumping = False
                    self.jump_v = 0

            if self.invincible > 0:
                self.invincible -= dt
            if self.shake > 0:
                self.shake -= dt

            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = max(0.4, 1.5 - self.score * 0.001)
                lane = random.randint(0, 2)
                if random.random() < 0.65:
                    self.obstacles.append({'x': LANES[lane], 'y': 1.1})
                else:
                    self.coins.append({'x': LANES[lane], 'y': 1.1})

            for obs in self.obstacles[:]:
                obs['y'] -= self.speed * dt / h
                if obs['y'] < -0.1:
                    self.obstacles.remove(obs)
                elif self.invincible <= 0:
                    px = self.player_x * w
                    py = (0.15 + self.player_h) * h
                    ox = obs['x'] * w
                    oy = obs['y'] * h
                    if abs(px - ox) < w * 0.07 and abs(py - oy) < h * 0.08:
                        self.game_over()

            for coin in self.coins[:]:
                coin['y'] -= self.speed * dt / h
                if coin['y'] < -0.1:
                    self.coins.remove(coin)
                else:
                    px = self.player_x * w
                    py = (0.15 + self.player_h) * h
                    cx = coin['x'] * w
                    cy = coin['y'] * h
                    if abs(px - cx) < w * 0.08 and abs(py - cy) < h * 0.08:
                        self.score += 50
                        self.add_particles(coin['x'], coin['y'], COLORS['neon_yellow'])
                        self.coins.remove(coin)

            for p in self.particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= dt * 2
                if p['life'] <= 0:
                    self.particles.remove(p)

        self.canvas.clear()
        with self.canvas:
            Color(*COLORS['dark'])
            Rectangle(pos=(0, 0), size=(w, h))

            road_w = w * 0.7
            road_x = (w - road_w) / 2
            Color(*COLORS['road'])
            Rectangle(pos=(road_x, 0), size=(road_w, h))

            for ly in self.road_lines:
                progress = max(0, min(1, ly))
                line_w = road_w * (0.3 + progress * 0.7)
                line_x = w / 2 - line_w / 2
                Color(0, 0.5, 1, 0.3 + progress * 0.4)
                Line(points=[line_x, ly * h, line_x + line_w, ly * h], width=1.5)

            Color(*COLORS['neon_pink'])
            Line(points=[road_x, 0, road_x, h], width=3)
            Color(*COLORS['neon_blue'])
            Line(points=[road_x + road_w, 0, road_x + road_w, h], width=3)

            for coin in self.coins:
                cx = coin['x'] * w
                cy = coin['y'] * h
                Color(*COLORS['neon_yellow'])
                Ellipse(pos=(cx-14, cy-14), size=(28, 28))
                Color(1, 1, 1, 0.6)
                Ellipse(pos=(cx-7, cy-7), size=(14, 14))

            for obs in self.obstacles:
                ox = obs['x'] * w
                oy = obs['y'] * h
                ow = w * 0.1
                oh = h * 0.09
                Color(1, 0.3, 0.3, 0.3)
                Rectangle(pos=(ox-ow/2-5, oy-oh/2-5), size=(ow+10, oh+10))
                Color(*COLORS['neon_red'])
                Rectangle(pos=(ox-ow/2, oy-oh/2), size=(ow, oh))

            for p in self.particles:
                c = p['color']
                Color(c[0], c[1], c[2], p['life'] * 0.8)
                sz = p['life'] * w * 0.018
                Ellipse(pos=(p['x']*w - sz/2, p['y']*h - sz/2), size=(sz, sz))

            px = self.player_x * w
            py = (0.15 + self.player_h) * h
            pw = w * 0.08
            ph = h * 0.1
            sx = random.uniform(-6, 6) if self.shake > 0 else 0

            blink = not (0 < self.invincible < 99 and int(self.invincible * 10) % 2 == 0)
            if blink:
                Color(0, 1, 0.8, 0.12)
                Ellipse(pos=(px-pw+sx, py-ph*0.2), size=(pw*2, ph*1.5))
                Color(*COLORS['neon_green'])
                Rectangle(pos=(px-pw/2+sx, py-ph/2), size=(pw, ph))
                Color(0, 0.5, 1, 0.9)
                Rectangle(pos=(px-pw/3+sx, py+ph*0.1), size=(pw*0.65, ph*0.25))
                Color(0, 0.8, 0.6, 1)
                Rectangle(pos=(px-pw/2+sx, py-ph*0.7), size=(pw*0.38, ph*0.22))
                Rectangle(pos=(px+pw*0.12+sx, py-ph*0.7), size=(pw*0.38, ph*0.22))

        self.score_label.pos = (0, h - 55)
        self.score_label.size = (w, 50)

    def game_over(self):
        self.state = 'gameover'
        self.invincible = 99
        self.shake = 0.4
        self.info_label.text = f'GAME OVER\n\nSCORE: {int(self.score)}\n\nTAP TO RETRY'
        self.score_label.color = (1, 0.1, 0.2, 1)

class CyberRunnerApp(App):
    def build(self):
        self.title = 'Cyber Runner'
        return GameWidget()

if __name__ == '__main__':
    CyberRunnerApp().run()
