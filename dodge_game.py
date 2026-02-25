import math
import random
import tkinter as tk

# ---------- Config ----------
WIDTH, HEIGHT = 960, 640
FPS_MS = 16
PLAYER_SPEED = 4.2
ENEMY_BASE_SPEED = 2.2
PLAYER_RADIUS = 16
ENEMY_RADIUS = 15
ATTACK_RANGE = 42
ENEMY_ATTACK_RANGE = 36


class GladiumGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gladium - Arena Prototype")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2a1a12", highlightthickness=0)
        self.canvas.pack()

        # Input
        self.keys = set()
        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        # Economy / progression
        self.gold = 0
        self.blood = 0
        self.wave = 1
        self.kills = 0
        self.state = "fighting"  # fighting, shop, game_over

        # Upgrades
        self.weapon_lvl = 1
        self.shield_lvl = 1
        self.ability_lvl = 1

        # Cooldowns
        self.attack_cd = 0
        self.ability_cd = 0
        self.player_stun = 0

        # Player stats
        self.max_hp = 110
        self.hp = self.max_hp
        self.base_damage = 16

        # Player position
        self.px = WIDTH // 2
        self.py = HEIGHT // 2 + 160

        # Enemies
        self.enemies = []

        # UI text ids
        self.hud_id = None
        self.msg_id = None
        self.controls_id = None

        # Visual ids
        self.player_id = None
        self.player_sword_id = None

        self.setup_wave(self.wave)
        self.update()

    # ---------- Core setup ----------
    def setup_wave(self, wave):
        self.state = "fighting"
        self.enemies.clear()

        # wave-based + 1v1 style starts
        enemy_count = min(2 + wave, 10)
        base_hp = 38 + wave * 6
        base_dmg = 7 + wave

        for _ in range(enemy_count):
            x, y = self.random_spawn_near_edge()
            self.enemies.append({
                "x": x,
                "y": y,
                "hp": base_hp + random.randint(-6, 8),
                "max_hp": base_hp,
                "damage": base_dmg + random.randint(0, 2),
                "speed": ENEMY_BASE_SPEED + min(2.6, wave * 0.08) + random.random() * 0.6,
                "attack_cd": random.randint(10, 40),
                "color": random.choice(["#b13b2e", "#8f2b22", "#c14635"]),
            })

    def random_spawn_near_edge(self):
        side = random.choice(["top", "bottom", "left", "right"])
        margin = 40
        if side == "top":
            return random.randint(margin, WIDTH - margin), random.randint(margin, 120)
        if side == "bottom":
            return random.randint(margin, WIDTH - margin), random.randint(HEIGHT - 120, HEIGHT - margin)
        if side == "left":
            return random.randint(margin, 120), random.randint(margin, HEIGHT - margin)
        return random.randint(WIDTH - 120, WIDTH - margin), random.randint(margin, HEIGHT - margin)

    # ---------- Input ----------
    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)

        if key == "r" and self.state == "game_over":
            self.reset_run()

        if key == "return" and self.state == "shop":
            self.wave += 1
            self.setup_wave(self.wave)

        if self.state == "shop":
            if key == "1":
                self.buy_weapon()
            elif key == "2":
                self.buy_shield()
            elif key == "3":
                self.buy_ability()

    def on_key_release(self, event):
        key = event.keysym.lower()
        self.keys.discard(key)

    # ---------- Upgrades ----------
    def weapon_cost(self):
        return 30 + self.weapon_lvl * 35

    def shield_cost(self):
        return 24 + self.shield_lvl * 30

    def ability_cost(self):
        return 40 + self.ability_lvl * 45

    def buy_weapon(self):
        c = self.weapon_cost()
        if self.gold >= c:
            self.gold -= c
            self.weapon_lvl += 1

    def buy_shield(self):
        c = self.shield_cost()
        if self.gold >= c:
            self.gold -= c
            self.shield_lvl += 1
            self.max_hp += 14
            self.hp = min(self.max_hp, self.hp + 18)

    def buy_ability(self):
        c = self.ability_cost()
        if self.blood >= c:
            self.blood -= c
            self.ability_lvl += 1

    # ---------- Combat ----------
    def current_damage(self):
        return self.base_damage + (self.weapon_lvl - 1) * 7

    def shield_reduction(self):
        return min(0.5, 0.08 * (self.shield_lvl - 1))

    def ability_damage(self):
        return 28 + self.ability_lvl * 14

    def do_basic_attack(self):
        if self.attack_cd > 0 or self.state != "fighting" or self.player_stun > 0:
            return
        self.attack_cd = 22

        hit_any = False
        dmg = self.current_damage()

        for e in self.enemies:
            dist = math.hypot(e["x"] - self.px, e["y"] - self.py)
            if dist <= ATTACK_RANGE:
                e["hp"] -= dmg
                hit_any = True

        if hit_any:
            # tiny lifesteal fantasy
            self.hp = min(self.max_hp, self.hp + 2)

    def do_special_attack(self):
        # AOE blood ability
        if self.ability_cd > 0 or self.state != "fighting" or self.player_stun > 0:
            return

        self.ability_cd = max(120, 300 - self.ability_lvl * 22)

        radius = 80 + self.ability_lvl * 12
        dmg = self.ability_damage()

        for e in self.enemies:
            dist = math.hypot(e["x"] - self.px, e["y"] - self.py)
            if dist <= radius:
                e["hp"] -= dmg

    # ---------- Update logic ----------
    def move_player(self):
        dx = dy = 0
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

        self.px = max(PLAYER_RADIUS + 8, min(WIDTH - PLAYER_RADIUS - 8, self.px + dx))
        self.py = max(PLAYER_RADIUS + 8, min(HEIGHT - PLAYER_RADIUS - 8, self.py + dy))

    def update_enemies(self):
        if self.state != "fighting":
            return

        for e in self.enemies:
            # move toward player
            vx = self.px - e["x"]
            vy = self.py - e["y"]
            d = math.hypot(vx, vy) + 1e-6

            # simple separation / crowding reduction
            sep_x = sep_y = 0
            for o in self.enemies:
                if o is e:
                    continue
                ox, oy = e["x"] - o["x"], e["y"] - o["y"]
                od = math.hypot(ox, oy)
                if od < 26 and od > 0:
                    sep_x += ox / od
                    sep_y += oy / od

            vx = (vx / d) * 0.9 + sep_x * 0.35
            vy = (vy / d) * 0.9 + sep_y * 0.35

            norm = math.hypot(vx, vy) + 1e-6
            e["x"] += (vx / norm) * e["speed"]
            e["y"] += (vy / norm) * e["speed"]

            # attacks
            e["attack_cd"] = max(0, e["attack_cd"] - 1)
            dist_to_player = math.hypot(e["x"] - self.px, e["y"] - self.py)
            if dist_to_player <= ENEMY_ATTACK_RANGE and e["attack_cd"] == 0:
                incoming = e["damage"]
                blocked = incoming * self.shield_reduction()
                final = max(1, int(incoming - blocked))
                self.hp -= final
                e["attack_cd"] = random.randint(28, 54)
                self.player_stun = min(8, self.player_stun + 2)

        # remove dead + rewards
        alive = []
        for e in self.enemies:
            if e["hp"] <= 0:
                self.kills += 1
                self.gold += 10 + self.wave * 2
                self.blood += 8 + self.wave
            else:
                alive.append(e)
        self.enemies = alive

        if self.hp <= 0:
            self.state = "game_over"

        if self.state == "fighting" and not self.enemies:
            # wave clear bonus
            self.gold += 24 + self.wave * 5
            self.blood += 20 + self.wave * 4
            self.hp = min(self.max_hp, self.hp + 18)
            self.state = "shop"

    # ---------- Rendering ----------
    def draw_arena(self):
        self.canvas.delete("all")

        # Arena floor + rings
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#3a2419", outline="")
        self.canvas.create_oval(90, 70, WIDTH - 90, HEIGHT - 70, fill="#6c4429", outline="#8f6b45", width=4)
        self.canvas.create_oval(160, 125, WIDTH - 160, HEIGHT - 125, fill="#7b502f", outline="#8f6b45", width=3)

        # Decorative blood splats
        random.seed(42)  # deterministic splats, no flicker pattern changes
        for _ in range(24):
            x = random.randint(150, WIDTH - 150)
            y = random.randint(110, HEIGHT - 110)
            r = random.randint(2, 6)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#5e0f0f", outline="")

    def draw_player(self):
        # body
        self.player_id = self.canvas.create_oval(
            self.px - PLAYER_RADIUS,
            self.py - PLAYER_RADIUS,
            self.px + PLAYER_RADIUS,
            self.py + PLAYER_RADIUS,
            fill="#d6b25e",
            outline="#f3deb0",
            width=2,
        )

        # sword direction based on last movement key
        sx, sy = self.px + 18, self.py
        if "a" in self.keys or "left" in self.keys:
            sx = self.px - 22
        elif "w" in self.keys or "up" in self.keys:
            sy = self.py - 22
        elif "s" in self.keys or "down" in self.keys:
            sy = self.py + 22

        self.player_sword_id = self.canvas.create_line(
            self.px,
            self.py,
            sx,
            sy,
            fill="#e8e8e8",
            width=4,
        )

        # ability radius preview when ready
        if self.ability_cd == 0 and self.state == "fighting":
            rr = 80 + self.ability_lvl * 12
            self.canvas.create_oval(self.px - rr, self.py - rr, self.px + rr, self.py + rr, outline="#a33939", width=1)

    def draw_enemies(self):
        for e in self.enemies:
            x, y = e["x"], e["y"]
            self.canvas.create_oval(
                x - ENEMY_RADIUS,
                y - ENEMY_RADIUS,
                x + ENEMY_RADIUS,
                y + ENEMY_RADIUS,
                fill=e["color"],
                outline="#f3c7c0",
                width=1,
            )

            # hp bar
            w = 30
            hp_ratio = max(0, e["hp"]) / e["max_hp"]
            self.canvas.create_rectangle(x - w / 2, y - 24, x + w / 2, y - 20, fill="#2b1b1b", outline="")
            self.canvas.create_rectangle(x - w / 2, y - 24, x - w / 2 + w * hp_ratio, y - 20, fill="#38d46a", outline="")

    def draw_hud(self):
        ability_ready = "READY" if self.ability_cd == 0 else f"{self.ability_cd // 60 + 1}s"
        hp_pct = int((self.hp / self.max_hp) * 100)

        hud = (
            f"HP: {self.hp}/{self.max_hp} ({hp_pct}%)   "
            f"Wave: {self.wave}   Kills: {self.kills}\n"
            f"Gold: {self.gold}   Blood: {self.blood}   "
            f"Weapon Lv {self.weapon_lvl} | Shield Lv {self.shield_lvl} | Ability Lv {self.ability_lvl}   "
            f"Special: {ability_ready}"
        )

        self.hud_id = self.canvas.create_text(12, 12, text=hud, fill="#f5e9cf", font=("Consolas", 13, "bold"), anchor="nw")

        controls = "Move: WASD/Arrows | Attack: SPACE | Special: F | Shop: 1/2/3 + ENTER | Restart: R"
        self.controls_id = self.canvas.create_text(WIDTH // 2, HEIGHT - 14, text=controls, fill="#dbcaa0", font=("Consolas", 11), anchor="s")

        if self.state == "shop":
            msg = (
                "WAVE CLEARED!\n"
                f"[1] Weapon +Damage ({self.weapon_cost()} gold)\n"
                f"[2] Shield +HP/Block ({self.shield_cost()} gold)\n"
                f"[3] Blood Art +Special ({self.ability_cost()} blood)\n"
                "Press ENTER to start next wave"
            )
            self.msg_id = self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2,
                text=msg,
                fill="#ffe6b5",
                font=("Consolas", 18, "bold"),
                justify="center",
            )

        elif self.state == "game_over":
            msg = (
                "YOU DIED IN THE ARENA\n"
                f"Waves Survived: {self.wave}  |  Kills: {self.kills}\n"
                f"Final Gold: {self.gold}  |  Final Blood: {self.blood}\n"
                "Press R to fight again"
            )
            self.msg_id = self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2,
                text=msg,
                fill="#ffd2a6",
                font=("Consolas", 20, "bold"),
                justify="center",
            )

    def reset_run(self):
        self.gold = 0
        self.blood = 0
        self.wave = 1
        self.kills = 0
        self.weapon_lvl = 1
        self.shield_lvl = 1
        self.ability_lvl = 1
        self.max_hp = 110
        self.hp = self.max_hp
        self.attack_cd = 0
        self.ability_cd = 0
        self.player_stun = 0
        self.px = WIDTH // 2
        self.py = HEIGHT // 2 + 160
        self.setup_wave(self.wave)

    def tick_cooldowns(self):
        self.attack_cd = max(0, self.attack_cd - 1)
        self.ability_cd = max(0, self.ability_cd - 1)
        self.player_stun = max(0, self.player_stun - 1)

    def update(self):
        # actions
        if "space" in self.keys:
            self.do_basic_attack()
        if "f" in self.keys:
            self.do_special_attack()

        if self.state == "fighting":
            if self.player_stun == 0:
                self.move_player()
            self.update_enemies()

        self.tick_cooldowns()

        # render
        self.draw_arena()
        self.draw_enemies()
        self.draw_player()
        self.draw_hud()

        self.root.after(FPS_MS, self.update)


def main():
    root = tk.Tk()
    _game = GladiumGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
