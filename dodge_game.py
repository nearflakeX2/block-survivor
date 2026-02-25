import math
import random
import tkinter as tk

# --- Window / world ---
WIDTH, HEIGHT = 960, 640
FPS_MS = 16

# --- Player ---
PLAYER_SIZE = 28
PLAYER_SPEED = 4.4
PLAYER_MAX_HP = 100

# --- Gun ---
SHOOT_COOLDOWN_FRAMES = 10
BULLET_SPEED = 9.0
BULLET_DAMAGE = 24
BULLET_RADIUS = 4

# --- Enemies ---
ENEMY_SIZE = 24
ENEMY_BASE_SPEED = 1.6
ENEMY_BASE_HP = 30
SPAWN_BASE_INTERVAL = 900  # ms


class SurvivorGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Block Survivor")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111111", highlightthickness=0)
        self.canvas.pack()

        # Input
        self.keys = set()
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.kills = 0
        self.wave = 1
        self.frame_count = 0

        # Player position centered
        self.px = WIDTH // 2
        self.py = HEIGHT // 2
        self.hp = PLAYER_MAX_HP

        # Entities
        self.enemies = []
        self.bullets = []

        # Combat timing
        self.shoot_cd = 0

        # UI message
        self.banner = "Move with WASD / Arrows | Auto-shoot nearest enemy | Press R to restart"

        # Spawn loop
        self.spawn_interval = SPAWN_BASE_INTERVAL
        self.root.after(self.spawn_interval, self.spawn_enemy)

        self.update()

    # ---------- Input ----------
    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)
        if key == "r" and self.game_over:
            self.restart()

    def on_key_release(self, event):
        self.keys.discard(event.keysym.lower())

    # ---------- Core mechanics ----------
    def restart(self):
        self.running = True
        self.game_over = False
        self.score = 0
        self.kills = 0
        self.wave = 1
        self.frame_count = 0
        self.hp = PLAYER_MAX_HP
        self.px = WIDTH // 2
        self.py = HEIGHT // 2
        self.enemies.clear()
        self.bullets.clear()
        self.shoot_cd = 0
        self.spawn_interval = SPAWN_BASE_INTERVAL
        self.banner = "Move with WASD / Arrows | Auto-shoot nearest enemy | Press R to restart"

    def move_player(self):
        dx = dy = 0.0
        if "a" in self.keys or "left" in self.keys:
            dx -= PLAYER_SPEED
        if "d" in self.keys or "right" in self.keys:
            dx += PLAYER_SPEED
        if "w" in self.keys or "up" in self.keys:
            dy -= PLAYER_SPEED
        if "s" in self.keys or "down" in self.keys:
            dy += PLAYER_SPEED

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        half = PLAYER_SIZE / 2
        self.px = max(half, min(WIDTH - half, self.px + dx))
        self.py = max(half, min(HEIGHT - half, self.py + dy))

    def spawn_enemy(self):
        if self.running:
            side = random.choice(["top", "bottom", "left", "right"])
            m = 30
            if side == "top":
                x, y = random.randint(m, WIDTH - m), -20
            elif side == "bottom":
                x, y = random.randint(m, WIDTH - m), HEIGHT + 20
            elif side == "left":
                x, y = -20, random.randint(m, HEIGHT - m)
            else:
                x, y = WIDTH + 20, random.randint(m, HEIGHT - m)

            hp = ENEMY_BASE_HP + self.wave * 6
            speed = ENEMY_BASE_SPEED + min(2.5, self.wave * 0.11) + random.random() * 0.6
            size = ENEMY_SIZE + random.randint(-4, 5)

            self.enemies.append({
                "x": x,
                "y": y,
                "hp": hp,
                "speed": speed,
                "size": size,
                "color": random.choice(["#d94f4f", "#bf3d3d", "#f06666"]),
            })

            # speed up over time
            self.spawn_interval = max(220, int(SPAWN_BASE_INTERVAL - self.wave * 35))

        self.root.after(self.spawn_interval, self.spawn_enemy)

    def nearest_enemy(self):
        if not self.enemies:
            return None
        return min(self.enemies, key=lambda e: (e["x"] - self.px) ** 2 + (e["y"] - self.py) ** 2)

    def auto_shoot(self):
        if self.shoot_cd > 0 or not self.running:
            return

        target = self.nearest_enemy()
        if not target:
            return

        dx = target["x"] - self.px
        dy = target["y"] - self.py
        dist = math.hypot(dx, dy) + 1e-6
        vx = (dx / dist) * BULLET_SPEED
        vy = (dy / dist) * BULLET_SPEED

        self.bullets.append({"x": self.px, "y": self.py, "vx": vx, "vy": vy, "r": BULLET_RADIUS})
        self.shoot_cd = SHOOT_COOLDOWN_FRAMES

    def update_bullets(self):
        alive_bullets = []

        for b in self.bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]

            # out of bounds
            if b["x"] < -10 or b["x"] > WIDTH + 10 or b["y"] < -10 or b["y"] > HEIGHT + 10:
                continue

            hit = False
            for e in self.enemies:
                dist = math.hypot(e["x"] - b["x"], e["y"] - b["y"])
                if dist <= (e["size"] / 2 + b["r"]):
                    e["hp"] -= BULLET_DAMAGE
                    hit = True
                    break

            if not hit:
                alive_bullets.append(b)

        self.bullets = alive_bullets

    def update_enemies(self):
        if not self.running:
            return

        player_half = PLAYER_SIZE / 2
        for e in self.enemies:
            dx = self.px - e["x"]
            dy = self.py - e["y"]
            dist = math.hypot(dx, dy) + 1e-6
            e["x"] += (dx / dist) * e["speed"]
            e["y"] += (dy / dist) * e["speed"]

            # contact damage
            if dist <= (e["size"] / 2 + player_half):
                self.hp -= 0.45

        survivors = []
        for e in self.enemies:
            if e["hp"] <= 0:
                self.kills += 1
                self.score += 10
            else:
                survivors.append(e)
        self.enemies = survivors

        if self.hp <= 0:
            self.hp = 0
            self.running = False
            self.game_over = True
            self.banner = "Game Over! Press R to restart"

    def update_progression(self):
        # increase wave every ~15 kills
        self.wave = 1 + self.kills // 15

    # ---------- Rendering ----------
    def draw(self):
        self.canvas.delete("all")

        # subtle grid
        for x in range(0, WIDTH, 40):
            self.canvas.create_line(x, 0, x, HEIGHT, fill="#191919")
        for y in range(0, HEIGHT, 40):
            self.canvas.create_line(0, y, WIDTH, y, fill="#191919")

        # bullets
        for b in self.bullets:
            r = b["r"]
            self.canvas.create_oval(b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r, fill="#ffd84d", outline="")

        # enemies (blocks)
        for e in self.enemies:
            s = e["size"]
            x1, y1 = e["x"] - s / 2, e["y"] - s / 2
            x2, y2 = e["x"] + s / 2, e["y"] + s / 2
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=e["color"], outline="#ffb3b3")

        # player (block)
        half = PLAYER_SIZE / 2
        self.canvas.create_rectangle(
            self.px - half, self.py - half, self.px + half, self.py + half,
            fill="#4aa8ff", outline="#cfe8ff", width=2
        )

        # gun line toward nearest enemy
        t = self.nearest_enemy()
        if t:
            dx, dy = t["x"] - self.px, t["y"] - self.py
            d = math.hypot(dx, dy) + 1e-6
            gx = self.px + (dx / d) * 24
            gy = self.py + (dy / d) * 24
            self.canvas.create_line(self.px, self.py, gx, gy, fill="#e6f3ff", width=4)

        # HUD
        hud = f"HP: {int(self.hp)}   Score: {self.score}   Kills: {self.kills}   Wave: {self.wave}"
        self.canvas.create_text(12, 10, text=hud, fill="#f0f0f0", font=("Consolas", 14, "bold"), anchor="nw")
        self.canvas.create_text(WIDTH // 2, HEIGHT - 12, text=self.banner, fill="#cfcfcf", font=("Consolas", 11), anchor="s")

    # ---------- Main loop ----------
    def update(self):
        self.frame_count += 1

        if self.running:
            self.move_player()
            self.auto_shoot()
            self.update_bullets()
            self.update_enemies()
            self.update_progression()

        if self.shoot_cd > 0:
            self.shoot_cd -= 1

        self.draw()
        self.root.after(FPS_MS, self.update)


def main():
    root = tk.Tk()
    _game = SurvivorGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
