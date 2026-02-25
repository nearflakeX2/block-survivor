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
BASE_SHOOT_COOLDOWN = 10
BULLET_SPEED = 9.0
BULLET_DAMAGE = 24
BULLET_RADIUS = 4

# --- Dash + spear ---
DASH_SPEED = 13.0
DASH_DURATION = 8           # frames
DASH_COOLDOWN = 42          # frames
DASH_HIT_DAMAGE = 56

# --- Enemies ---
ENEMY_SIZE = 24
ENEMY_BASE_SPEED = 1.6
ENEMY_BASE_HP = 30
SPAWN_BASE_INTERVAL = 900  # ms

# --- Powerups ---
POWERUP_SIZE = 16
POWERUP_DROP_CHANCE = 0.18
POWERUP_LIFETIME = 560  # frames (~9 sec)


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
        self.powerups = []

        # Timed buffs (frames)
        self.rapid_fire_timer = 0
        self.speed_timer = 0
        self.shield_timer = 0
        self.multishot_timer = 0

        # Combat timing
        self.shoot_cd = 0
        self.dash_cd = 0
        self.dash_timer = 0
        self.dash_vx = 0.0
        self.dash_vy = 0.0

        # facing direction (for spear + dash aim)
        self.face_x = 1.0
        self.face_y = 0.0

        # UI message
        self.banner = "Move with WASD / Arrows | Auto-shoot nearest enemy | SPACE dash+spear hit | Press R to restart"

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
        if key == "space" and self.running:
            self.start_dash()

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
        self.powerups.clear()
        self.shoot_cd = 0
        self.dash_cd = 0
        self.dash_timer = 0
        self.dash_vx = 0.0
        self.dash_vy = 0.0
        self.face_x = 1.0
        self.face_y = 0.0
        self.spawn_interval = SPAWN_BASE_INTERVAL
        self.rapid_fire_timer = 0
        self.speed_timer = 0
        self.shield_timer = 0
        self.multishot_timer = 0
        self.banner = "Move with WASD / Arrows | Auto-shoot nearest enemy | SPACE dash+spear hit | Press R to restart"

    def current_player_speed(self):
        if self.speed_timer > 0:
            return PLAYER_SPEED * 1.5
        return PLAYER_SPEED

    def current_shoot_cooldown(self):
        if self.rapid_fire_timer > 0:
            return max(3, BASE_SHOOT_COOLDOWN // 2)
        return BASE_SHOOT_COOLDOWN

    def move_player(self):
        if self.dash_timer > 0:
            return

        speed = self.current_player_speed()
        dx = dy = 0.0
        if "a" in self.keys or "left" in self.keys:
            dx -= speed
        if "d" in self.keys or "right" in self.keys:
            dx += speed
        if "w" in self.keys or "up" in self.keys:
            dy -= speed
        if "s" in self.keys or "down" in self.keys:
            dy += speed

        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        # update facing while moving
        if dx or dy:
            mag = math.hypot(dx, dy)
            self.face_x = dx / mag
            self.face_y = dy / mag

        half = PLAYER_SIZE / 2
        self.px = max(half, min(WIDTH - half, self.px + dx))
        self.py = max(half, min(HEIGHT - half, self.py + dy))

    def start_dash(self):
        if self.dash_cd > 0 or self.dash_timer > 0:
            return

        # dash direction from movement keys, else toward nearest enemy, else facing dir
        dx = dy = 0.0
        if "a" in self.keys or "left" in self.keys:
            dx -= 1
        if "d" in self.keys or "right" in self.keys:
            dx += 1
        if "w" in self.keys or "up" in self.keys:
            dy -= 1
        if "s" in self.keys or "down" in self.keys:
            dy += 1

        if dx == 0 and dy == 0:
            t = self.nearest_enemy()
            if t:
                dx = t["x"] - self.px
                dy = t["y"] - self.py
            else:
                dx, dy = self.face_x, self.face_y

        mag = math.hypot(dx, dy) + 1e-6
        self.dash_vx = (dx / mag) * DASH_SPEED
        self.dash_vy = (dy / mag) * DASH_SPEED
        self.face_x = dx / mag
        self.face_y = dy / mag
        self.dash_timer = DASH_DURATION
        self.dash_cd = DASH_COOLDOWN

    def update_dash(self):
        if self.dash_timer <= 0:
            return

        half = PLAYER_SIZE / 2
        self.px = max(half, min(WIDTH - half, self.px + self.dash_vx))
        self.py = max(half, min(HEIGHT - half, self.py + self.dash_vy))

        # spear-dash collision damage
        spear_len = 30
        tip_x = self.px + self.face_x * spear_len
        tip_y = self.py + self.face_y * spear_len
        for e in self.enemies:
            # hit if close to player or spear tip while dashing
            d_body = math.hypot(e["x"] - self.px, e["y"] - self.py)
            d_tip = math.hypot(e["x"] - tip_x, e["y"] - tip_y)
            if d_body <= (e["size"] / 2 + PLAYER_SIZE / 2) or d_tip <= (e["size"] / 2 + 8):
                e["hp"] -= DASH_HIT_DAMAGE

        self.dash_timer -= 1

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

            # Enemy design tiers get meaner as waves increase
            if self.wave < 4:
                etype = "grunt"
                color, outline = "#d94f4f", "#ffb3b3"
                shape = "square"
            elif self.wave < 8:
                etype = "brute"
                hp += 18
                size += 6
                speed *= 0.86
                color, outline = "#b73a7c", "#f4b3db"
                shape = "diamond"
            elif self.wave < 12:
                etype = "runner"
                hp -= 8
                size -= 3
                speed *= 1.42
                color, outline = "#f08a24", "#ffd4a3"
                shape = "triangle"
            else:
                etype = "elite"
                hp += 32
                size += 3
                speed *= 1.2
                color, outline = "#7a2be2", "#d7b4ff"
                shape = "hex"

            self.enemies.append({
                "x": x,
                "y": y,
                "hp": hp,
                "max_hp": hp,
                "speed": speed,
                "size": max(12, size),
                "color": color,
                "outline": outline,
                "type": etype,
                "shape": shape,
            })

            # speed up over time
            self.spawn_interval = max(220, int(SPAWN_BASE_INTERVAL - self.wave * 35))

        self.root.after(self.spawn_interval, self.spawn_enemy)

    def nearest_enemy(self):
        if not self.enemies:
            return None
        return min(self.enemies, key=lambda e: (e["x"] - self.px) ** 2 + (e["y"] - self.py) ** 2)

    def spawn_bullet(self, angle):
        vx = math.cos(angle) * BULLET_SPEED
        vy = math.sin(angle) * BULLET_SPEED
        self.bullets.append({"x": self.px, "y": self.py, "vx": vx, "vy": vy, "r": BULLET_RADIUS})

    def auto_shoot(self):
        if self.shoot_cd > 0 or not self.running:
            return

        target = self.nearest_enemy()
        if not target:
            return

        dx = target["x"] - self.px
        dy = target["y"] - self.py
        base_angle = math.atan2(dy, dx)

        # multishot powerup
        if self.multishot_timer > 0:
            spread = 0.18
            for a in (base_angle - spread, base_angle, base_angle + spread):
                self.spawn_bullet(a)
        else:
            self.spawn_bullet(base_angle)

        self.shoot_cd = self.current_shoot_cooldown()

    def maybe_drop_powerup(self, x, y):
        if random.random() > POWERUP_DROP_CHANCE:
            return

        ptype = random.choices(
            ["heal", "rapid", "speed", "shield", "multi"],
            weights=[22, 20, 20, 18, 20],
            k=1,
        )[0]

        color = {
            "heal": "#4de284",   # green
            "rapid": "#ffe066",  # yellow
            "speed": "#66d9ff",  # cyan
            "shield": "#b388ff", # purple
            "multi": "#ff9ecf",  # pink
        }[ptype]

        self.powerups.append({
            "x": x,
            "y": y,
            "type": ptype,
            "ttl": POWERUP_LIFETIME,
            "color": color,
        })

    def collect_powerups(self):
        remaining = []
        player_r = PLAYER_SIZE / 2

        for p in self.powerups:
            p["ttl"] -= 1
            if p["ttl"] <= 0:
                continue

            if math.hypot(p["x"] - self.px, p["y"] - self.py) <= (player_r + POWERUP_SIZE / 2):
                self.apply_powerup(p["type"])
                continue

            remaining.append(p)

        self.powerups = remaining

    def apply_powerup(self, ptype):
        if ptype == "heal":
            self.hp = min(PLAYER_MAX_HP, self.hp + 28)
            self.banner = "+HEAL"
        elif ptype == "rapid":
            self.rapid_fire_timer = min(1800, self.rapid_fire_timer + 420)
            self.banner = "RAPID FIRE STACKED!"
        elif ptype == "speed":
            self.speed_timer = min(1800, self.speed_timer + 420)
            self.banner = "SPEED BOOST STACKED!"
        elif ptype == "shield":
            self.shield_timer = min(1800, self.shield_timer + 420)
            self.banner = "SHIELD STACKED!"
        elif ptype == "multi":
            self.multishot_timer = min(1800, self.multishot_timer + 420)
            self.banner = "TRIPLE SHOT STACKED!"

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

            # contact damage (reduced with shield)
            if dist <= (e["size"] / 2 + player_half):
                dmg = 0.45
                if self.shield_timer > 0:
                    dmg *= 0.35
                self.hp -= dmg

        survivors = []
        for e in self.enemies:
            if e["hp"] <= 0:
                self.kills += 1
                self.score += 10
                self.maybe_drop_powerup(e["x"], e["y"])
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

    def tick_buffs(self):
        self.rapid_fire_timer = max(0, self.rapid_fire_timer - 1)
        self.speed_timer = max(0, self.speed_timer - 1)
        self.shield_timer = max(0, self.shield_timer - 1)
        self.multishot_timer = max(0, self.multishot_timer - 1)

    # ---------- Rendering ----------
    def draw(self):
        self.canvas.delete("all")

        # subtle grid
        for x in range(0, WIDTH, 40):
            self.canvas.create_line(x, 0, x, HEIGHT, fill="#191919")
        for y in range(0, HEIGHT, 40):
            self.canvas.create_line(0, y, WIDTH, y, fill="#191919")

        # powerups
        for p in self.powerups:
            s = POWERUP_SIZE
            x1, y1 = p["x"] - s / 2, p["y"] - s / 2
            x2, y2 = p["x"] + s / 2, p["y"] + s / 2
            self.canvas.create_oval(x1, y1, x2, y2, fill=p["color"], outline="#ffffff")

        # bullets
        for b in self.bullets:
            r = b["r"]
            self.canvas.create_oval(b["x"] - r, b["y"] - r, b["x"] + r, b["y"] + r, fill="#ffd84d", outline="")

        # enemies (design changes with difficulty tiers)
        for e in self.enemies:
            s = e["size"]
            x, y = e["x"], e["y"]
            x1, y1 = x - s / 2, y - s / 2
            x2, y2 = x + s / 2, y + s / 2

            if e["shape"] == "square":
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=e["color"], outline=e["outline"], width=2)
            elif e["shape"] == "diamond":
                self.canvas.create_polygon(
                    x, y1, x2, y, x, y2, x1, y,
                    fill=e["color"], outline=e["outline"], width=2
                )
            elif e["shape"] == "triangle":
                self.canvas.create_polygon(
                    x, y1, x2, y2, x1, y2,
                    fill=e["color"], outline=e["outline"], width=2
                )
            else:  # hex
                h = s * 0.5
                self.canvas.create_polygon(
                    x - h * 0.9, y - h,
                    x + h * 0.9, y - h,
                    x + h * 1.4, y,
                    x + h * 0.9, y + h,
                    x - h * 0.9, y + h,
                    x - h * 1.4, y,
                    fill=e["color"], outline=e["outline"], width=2
                )

            # mini HP bar
            hp_ratio = max(0, e["hp"]) / max(1, e.get("max_hp", e["hp"]))
            bar_w = max(14, s)
            self.canvas.create_rectangle(x - bar_w / 2, y - s / 2 - 8, x + bar_w / 2, y - s / 2 - 4, fill="#2a2a2a", outline="")
            self.canvas.create_rectangle(
                x - bar_w / 2,
                y - s / 2 - 8,
                x - bar_w / 2 + bar_w * hp_ratio,
                y - s / 2 - 4,
                fill="#67d67a",
                outline="",
            )

        # player (block)
        half = PLAYER_SIZE / 2
        player_fill = "#4aa8ff" if self.shield_timer == 0 else "#7b8cff"
        self.canvas.create_rectangle(
            self.px - half, self.py - half, self.px + half, self.py + half,
            fill=player_fill, outline="#cfe8ff", width=2
        )

        # gun line toward nearest enemy (auto-shoot aim)
        t = self.nearest_enemy()
        if t:
            dx, dy = t["x"] - self.px, t["y"] - self.py
            d = math.hypot(dx, dy) + 1e-6
            gx = self.px + (dx / d) * 20
            gy = self.py + (dy / d) * 20
            self.canvas.create_line(self.px, self.py, gx, gy, fill="#e6f3ff", width=3)

        # spear (points where you face / dash)
        spear_len = 30 if self.dash_timer == 0 else 42
        sx = self.px + self.face_x * spear_len
        sy = self.py + self.face_y * spear_len
        spear_color = "#f4f7ff" if self.dash_timer == 0 else "#fff07a"
        self.canvas.create_line(self.px, self.py, sx, sy, fill=spear_color, width=5)

        # HUD
        hud = f"HP: {int(self.hp)}   Score: {self.score}   Kills: {self.kills}   Wave: {self.wave}"
        buffs = (
            f"Buffs: RF {self.rapid_fire_timer//60}s | SPD {self.speed_timer//60}s | "
            f"SHD {self.shield_timer//60}s | TRI {self.multishot_timer//60}s | "
            f"DASH {self.dash_cd//60 if self.dash_cd>0 else 'READY'}"
        )
        self.canvas.create_text(12, 10, text=hud, fill="#f0f0f0", font=("Consolas", 14, "bold"), anchor="nw")
        self.canvas.create_text(12, 34, text=buffs, fill="#d8d8d8", font=("Consolas", 11), anchor="nw")
        self.canvas.create_text(
            12,
            52,
            text="Enemy tiers: Grunt(1-3) Brute(4-7) Runner(8-11) Elite(12+)",
            fill="#bcbcbc",
            font=("Consolas", 10),
            anchor="nw",
        )
        self.canvas.create_text(WIDTH // 2, HEIGHT - 12, text=self.banner, fill="#cfcfcf", font=("Consolas", 11), anchor="s")

    # ---------- Main loop ----------
    def update(self):
        self.frame_count += 1

        if self.running:
            self.move_player()
            self.update_dash()
            self.auto_shoot()
            self.update_bullets()
            self.update_enemies()
            self.collect_powerups()
            self.update_progression()
            self.tick_buffs()

        if self.shoot_cd > 0:
            self.shoot_cd -= 1
        if self.dash_cd > 0:
            self.dash_cd -= 1

        self.draw()
        self.root.after(FPS_MS, self.update)


def main():
    root = tk.Tk()
    _game = SurvivorGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
