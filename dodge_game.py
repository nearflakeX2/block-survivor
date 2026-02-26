import math
import random
import tkinter as tk

WIDTH, HEIGHT = 1100, 680
WORLD_W = 840  # right side is power panel
FPS_MS = 16

PLAYER_SIZE = 28
BASE_HP = 120
BASE_SPEED = 4.1
BASE_BULLET_DMG = 22
BASE_BULLET_SPEED = 8.8
BASE_FIRE_CD = 10

ENEMY_BASE_HP = 26
ENEMY_BASE_SPEED = 1.45
SPAWN_MS = 850


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Survivor")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#101010", highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        root.bind("<KeyPress>", self.on_key_down)
        root.bind("<KeyRelease>", self.on_key_up)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind_all("<MouseWheel>", self.on_wheel)

        self.setup_powers()
        self.reset()
        self.root.after(self.spawn_ms, self.spawn_enemy)
        self.tick()

    def setup_powers(self):
        # 20 unique powers
        self.powers = [
            {"id":"dark_aura","name":"Dark Aura","cost":100,"kind":"toggle"},
            {"id":"orbit_blades","name":"Orbit Blades","cost":140,"kind":"toggle"},
            {"id":"blood_nova","name":"Blood Nova","cost":160,"kind":"cast"},
            {"id":"time_freeze","name":"Time Freeze","cost":170,"kind":"cast"},
            {"id":"auto_turret","name":"Auto Turret","cost":180,"kind":"cast"},
            {"id":"chain_lightning","name":"Chain Lightning","cost":190,"kind":"cast"},
            {"id":"meteor_drop","name":"Meteor Drop","cost":210,"kind":"cast"},
            {"id":"poison_cloud","name":"Poison Cloud","cost":150,"kind":"toggle"},
            {"id":"spike_ring","name":"Spike Ring","cost":145,"kind":"toggle"},
            {"id":"blade_dash_plus","name":"Blade Dash+","cost":120,"kind":"passive"},
            {"id":"rapid_core","name":"Rapid Core","cost":120,"kind":"passive"},
            {"id":"damage_core","name":"Damage Core","cost":120,"kind":"passive"},
            {"id":"speed_core","name":"Speed Core","cost":110,"kind":"passive"},
            {"id":"regen_core","name":"Regen Core","cost":130,"kind":"passive"},
            {"id":"maxhp_core","name":"MaxHP Core","cost":130,"kind":"passive"},
            {"id":"magnet_core","name":"Magnet Core","cost":125,"kind":"passive"},
            {"id":"ricochet_shot","name":"Ricochet Shot","cost":160,"kind":"passive"},
            {"id":"split_shot","name":"Split Shot","cost":170,"kind":"passive"},
            {"id":"vamp_pulse","name":"Vamp Pulse","cost":180,"kind":"cast"},
            {"id":"shockwave_step","name":"Shockwave Step","cost":165,"kind":"cast"},
        ]

        self.descriptions = {
            "dark_aura":"Toggle aura that damages nearby enemies.",
            "orbit_blades":"Toggle 3 spinning blades around you.",
            "blood_nova":"Instant big AoE burst around player.",
            "time_freeze":"Slows all enemies for a short time.",
            "auto_turret":"Deploys a temporary auto-firing turret.",
            "chain_lightning":"Zaps nearest enemies in a chain.",
            "meteor_drop":"Drops meteors randomly on enemies.",
            "poison_cloud":"Toggle poison cloud around player.",
            "spike_ring":"Toggle outer ring damage zone.",
            "blade_dash_plus":"Dash hits much harder and longer.",
            "rapid_core":"Permanent faster fire rate.",
            "damage_core":"Permanent bullet damage up.",
            "speed_core":"Permanent movement speed up.",
            "regen_core":"Permanent HP regeneration.",
            "maxhp_core":"Permanent max HP up.",
            "magnet_core":"Pulls drops toward you.",
            "ricochet_shot":"Bullets pierce one extra enemy.",
            "split_shot":"Shoots 3 bullets each attack.",
            "vamp_pulse":"Steals life from nearby enemies.",
            "shockwave_step":"Launches directional shockwave.",
        }

    def reset(self):
        self.running = True
        self.game_over = False

        self.px, self.py = WORLD_W // 2, HEIGHT // 2
        self.face_x, self.face_y = 1.0, 0.0

        self.hp = float(BASE_HP)
        self.max_hp = BASE_HP
        self.coins = 0
        self.kills = 0
        self.wave = 1

        self.enemies = []
        self.bullets = []
        self.drops = []
        self.turrets = []
        self.meteors = []

        self.spawn_ms = SPAWN_MS
        self.frame = 0

        self.shoot_cd = 0
        self.dash_cd = 0
        self.dash_t = 0
        self.dash_vx = 0
        self.dash_vy = 0

        self.freeze_t = 0
        self.cast_cd = 0

        # power ownership and runtime
        self.owned = set()
        self.active_toggles = set()

        # stats from passives
        self.stat_damage = 0
        self.stat_speed = 0
        self.stat_regen = 0
        self.stat_rapid = 0
        self.stat_magnet = 0
        self.stat_ricochet = False
        self.stat_split = False
        self.stat_dash_plus = False

        self.orbit_angle = 0
        self.panel_scroll = 0
        self.banner = "Mouse: click powers on right panel | Wheel scroll | SPACE dash | R restart"

    # ---------- input ----------
    def on_key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)
        if k == "r" and self.game_over:
            self.reset()
        if k == "space" and self.running:
            self.start_dash()

    def on_key_up(self, e):
        self.keys.discard(e.keysym.lower())

    def on_wheel(self, e):
        # scroll power list
        delta = -1 if e.delta > 0 else 1
        self.panel_scroll = max(0, min(len(self.powers) - 1, self.panel_scroll + delta))

    def on_click(self, e):
        if e.x < WORLD_W:
            return

        # identify clicked power row
        panel_x = WORLD_W + 10
        panel_w = WIDTH - WORLD_W - 20
        row_h = 28
        y0 = 110

        if not (panel_x <= e.x <= panel_x + panel_w):
            return

        idx_in_view = (e.y - y0) // row_h
        if idx_in_view < 0:
            return
        idx = self.panel_scroll + idx_in_view
        if idx >= len(self.powers):
            return

        self.buy_or_use_power(self.powers[idx])

    # ---------- power system ----------
    def power_cost(self, p):
        # repeat buys increase cost only for cast powers
        pid = p["id"]
        base = p["cost"]
        levels = getattr(self, f"lvl_{pid}", 0)
        return base + levels * 40 if p["kind"] == "cast" else base

    def buy_or_use_power(self, p):
        pid = p["id"]
        kind = p["kind"]

        if kind in ("toggle", "passive") and pid in self.owned:
            # toggles can be turned on/off by clicking again
            if kind == "toggle":
                if pid in self.active_toggles:
                    self.active_toggles.remove(pid)
                    self.banner = f"{p['name']} OFF"
                else:
                    self.active_toggles.add(pid)
                    self.banner = f"{p['name']} ON"
            else:
                self.banner = f"{p['name']} already owned"
            return

        cost = self.power_cost(p)
        if self.coins < cost:
            self.banner = f"Need {cost} coins"
            return

        self.coins -= cost

        if kind in ("toggle", "passive"):
            self.owned.add(pid)
            if kind == "toggle":
                self.active_toggles.add(pid)  # instantly active as requested
            self.apply_passive(pid)
            self.banner = f"Bought {p['name']}"
        else:
            # cast power: buy level + instant cast once
            lv = getattr(self, f"lvl_{pid}", 0) + 1
            setattr(self, f"lvl_{pid}", lv)
            self.cast_power(pid)
            self.banner = f"{p['name']} Lv{lv}"

    def apply_passive(self, pid):
        if pid == "rapid_core": self.stat_rapid += 1
        elif pid == "damage_core": self.stat_damage += 8
        elif pid == "speed_core": self.stat_speed += 0.6
        elif pid == "regen_core": self.stat_regen += 0.22
        elif pid == "maxhp_core": self.max_hp += 30; self.hp += 30
        elif pid == "magnet_core": self.stat_magnet += 45
        elif pid == "ricochet_shot": self.stat_ricochet = True
        elif pid == "split_shot": self.stat_split = True
        elif pid == "blade_dash_plus": self.stat_dash_plus = True

    def cast_power(self, pid):
        # cast powers triggered on purchase and can be re-bought for more levels
        lv = getattr(self, f"lvl_{pid}", 1)
        if pid == "blood_nova":
            r = 130 + lv * 18
            dmg = 55 + lv * 20
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= r:
                    en["hp"] -= dmg
        elif pid == "time_freeze":
            self.freeze_t = max(self.freeze_t, 80 + lv * 25)
        elif pid == "auto_turret":
            self.turrets.append({"x": self.px, "y": self.py, "ttl": 280 + lv * 70, "cd": 0, "lv": lv})
        elif pid == "chain_lightning":
            targets = sorted(self.enemies, key=lambda e: (e["x"]-self.px)**2 + (e["y"]-self.py)**2)[:(3 + lv)]
            dmg = 35 + lv * 10
            for t in targets:
                t["hp"] -= dmg
        elif pid == "meteor_drop":
            for _ in range(2 + lv):
                if self.enemies:
                    t = random.choice(self.enemies)
                    self.meteors.append({"x": t["x"], "y": t["y"], "t": 30, "dmg": 50 + lv * 14})
        elif pid == "vamp_pulse":
            total = 0
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= 120 + lv * 8:
                    en["hp"] -= 30 + lv * 10
                    total += 6 + lv * 2
            self.hp = min(self.max_hp, self.hp + total)
        elif pid == "shockwave_step":
            # directional line damage
            for en in self.enemies:
                vx, vy = en["x"] - self.px, en["y"] - self.py
                forward = vx * self.face_x + vy * self.face_y
                side = abs(vx * (-self.face_y) + vy * self.face_x)
                if 0 < forward < 220 + lv * 30 and side < 25 + lv * 5:
                    en["hp"] -= 45 + lv * 14

    # ---------- gameplay ----------
    def spawn_enemy(self):
        if self.running:
            side = random.randint(0, 3)
            if side == 0:
                x, y = random.randint(20, WORLD_W - 20), -20
            elif side == 1:
                x, y = random.randint(20, WORLD_W - 20), HEIGHT + 20
            elif side == 2:
                x, y = -20, random.randint(20, HEIGHT - 20)
            else:
                x, y = WORLD_W + 20, random.randint(20, HEIGHT - 20)

            hp = ENEMY_BASE_HP + self.wave * 5
            sp = ENEMY_BASE_SPEED + min(2.8, self.wave * 0.1) + random.random() * 0.5
            size = 22 + random.randint(-4, 5)
            tier = min(3, self.wave // 4)
            shapes = ["square", "diamond", "triangle", "hex"]
            colors = ["#d94f4f", "#b04fda", "#f08a24", "#7a2be2"]
            self.enemies.append({"x": x, "y": y, "hp": hp, "max": hp, "sp": sp, "s": size, "shape": shapes[tier], "c": colors[tier]})

            self.spawn_ms = max(180, SPAWN_MS - self.wave * 25)

        self.root.after(self.spawn_ms, self.spawn_enemy)

    def nearest_enemy(self):
        if not self.enemies:
            return None
        return min(self.enemies, key=lambda e: (e["x"] - self.px) ** 2 + (e["y"] - self.py) ** 2)

    def start_dash(self):
        if self.dash_cd > 0 or self.dash_t > 0:
            return
        dx = (-1 if "a" in self.keys or "left" in self.keys else 0) + (1 if "d" in self.keys or "right" in self.keys else 0)
        dy = (-1 if "w" in self.keys or "up" in self.keys else 0) + (1 if "s" in self.keys or "down" in self.keys else 0)
        if dx == 0 and dy == 0:
            t = self.nearest_enemy()
            if t:
                dx, dy = t["x"] - self.px, t["y"] - self.py
            else:
                dx, dy = self.face_x, self.face_y
        d = math.hypot(dx, dy) + 1e-6
        self.face_x, self.face_y = dx / d, dy / d
        dash_speed = 13 + (3 if self.stat_dash_plus else 0)
        self.dash_vx, self.dash_vy = self.face_x * dash_speed, self.face_y * dash_speed
        self.dash_t = 10 if self.stat_dash_plus else 8
        self.dash_cd = 40

    def fire(self):
        if self.shoot_cd > 0:
            return
        t = self.nearest_enemy()
        if not t:
            return

        base = math.atan2(t["y"] - self.py, t["x"] - self.px)
        spread = [0]
        if self.stat_split:
            spread = [-0.16, 0, 0.16]

        for s in spread:
            a = base + s
            sp = BASE_BULLET_SPEED + self.stat_damage * 0.04
            self.bullets.append({"x": self.px, "y": self.py, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp, "r": 4, "pierce": 1 if self.stat_ricochet else 0})

        cd = int(BASE_FIRE_CD * (1 - 0.12 * self.stat_rapid))
        self.shoot_cd = max(3, cd)

    def update_logic(self):
        if not self.running:
            return

        self.frame += 1

        # movement
        if self.dash_t > 0:
            self.px += self.dash_vx
            self.py += self.dash_vy
            self.dash_t -= 1
            hit_dmg = 58 + (24 if self.stat_dash_plus else 0)
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) < en["s"] / 2 + PLAYER_SIZE / 2:
                    en["hp"] -= hit_dmg
        else:
            sp = BASE_SPEED + self.stat_speed
            dx = (-sp if "a" in self.keys or "left" in self.keys else 0) + (sp if "d" in self.keys or "right" in self.keys else 0)
            dy = (-sp if "w" in self.keys or "up" in self.keys else 0) + (sp if "s" in self.keys or "down" in self.keys else 0)
            if dx and dy:
                dx *= 0.7071
                dy *= 0.7071
            if dx or dy:
                d = math.hypot(dx, dy)
                self.face_x, self.face_y = dx / d, dy / d
            self.px += dx
            self.py += dy

        h = PLAYER_SIZE / 2
        self.px = max(h, min(WORLD_W - h, self.px))
        self.py = max(h, min(HEIGHT - h, self.py))

        # toggles always active when bought
        if "dark_aura" in self.active_toggles:
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= 88 + en["s"] / 2:
                    en["hp"] -= 1.8

        if "poison_cloud" in self.active_toggles:
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= 125 + en["s"] / 2:
                    en["hp"] -= 1.1

        if "spike_ring" in self.active_toggles:
            for en in self.enemies:
                d = math.hypot(en["x"] - self.px, en["y"] - self.py)
                if 105 <= d <= 130:
                    en["hp"] -= 2.3

        if "orbit_blades" in self.active_toggles:
            self.orbit_angle += 0.2
            for i in range(3):
                a = self.orbit_angle + i * (2 * math.pi / 3)
                bx, by = self.px + math.cos(a) * 46, self.py + math.sin(a) * 46
                for en in self.enemies:
                    if math.hypot(en["x"] - bx, en["y"] - by) <= en["s"] / 2 + 11:
                        en["hp"] -= 6

        # auto-fire
        self.fire()

        # bullets
        alive_b = []
        for b in self.bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            if b["x"] < -10 or b["x"] > WORLD_W + 10 or b["y"] < -10 or b["y"] > HEIGHT + 10:
                continue
            hit = False
            for en in self.enemies:
                if math.hypot(en["x"] - b["x"], en["y"] - b["y"]) <= en["s"] / 2 + b["r"]:
                    en["hp"] -= BASE_BULLET_DMG + self.stat_damage
                    if b["pierce"] > 0:
                        b["pierce"] -= 1
                    else:
                        hit = True
                    break
            if not hit:
                alive_b.append(b)
        self.bullets = alive_b

        # turrets
        alive_t = []
        for t in self.turrets:
            t["ttl"] -= 1
            t["cd"] = max(0, t["cd"] - 1)
            if t["ttl"] <= 0:
                continue
            if self.enemies and t["cd"] == 0:
                target = min(self.enemies, key=lambda e: (e["x"] - t["x"])**2 + (e["y"] - t["y"])**2)
                if math.hypot(target["x"] - t["x"], target["y"] - t["y"]) < 270:
                    target["hp"] -= 24 + t["lv"] * 8
                    t["cd"] = 12
            alive_t.append(t)
        self.turrets = alive_t

        # meteors
        alive_m = []
        for m in self.meteors:
            m["t"] -= 1
            if m["t"] <= 0:
                for en in self.enemies:
                    if math.hypot(en["x"] - m["x"], en["y"] - m["y"]) < 70:
                        en["hp"] -= m["dmg"]
            else:
                alive_m.append(m)
        self.meteors = alive_m

        # enemies
        alive_e = []
        for en in self.enemies:
            dx, dy = self.px - en["x"], self.py - en["y"]
            d = math.hypot(dx, dy) + 1e-6
            mul = 0.25 if self.freeze_t > 0 else 1.0
            en["x"] += (dx / d) * en["sp"] * mul
            en["y"] += (dy / d) * en["sp"] * mul
            if d <= en["s"] / 2 + PLAYER_SIZE / 2:
                self.hp -= 0.45

            if en["hp"] <= 0:
                self.kills += 1
                self.coins += 8
            else:
                alive_e.append(en)
        self.enemies = alive_e

        # drops
        if random.random() < 0.04 and self.enemies:
            en = random.choice(self.enemies)
            self.drops.append({"x": en["x"], "y": en["y"], "ttl": 420, "k":"coin"})

        keep = []
        for d in self.drops:
            d["ttl"] -= 1
            if d["ttl"] <= 0:
                continue
            if self.stat_magnet > 0:
                dx, dy = self.px - d["x"], self.py - d["y"]
                dist = math.hypot(dx, dy) + 1e-6
                if dist < 220 + self.stat_magnet:
                    pull = 1.0 + self.stat_magnet * 0.02
                    d["x"] += (dx / dist) * pull
                    d["y"] += (dy / dist) * pull
            if math.hypot(d["x"] - self.px, d["y"] - self.py) <= 18:
                self.coins += 5
            else:
                keep.append(d)
        self.drops = keep

        # timers/stats
        self.shoot_cd = max(0, self.shoot_cd - 1)
        self.dash_cd = max(0, self.dash_cd - 1)
        self.freeze_t = max(0, self.freeze_t - 1)

        self.hp = min(self.max_hp, self.hp + self.stat_regen / 60)
        self.wave = 1 + self.kills // 15

        if self.hp <= 0:
            self.hp = 0
            self.running = False
            self.game_over = True

    # ---------- draw ----------
    def draw_enemy(self, en):
        x, y, s = en["x"], en["y"], en["s"]
        x1, y1, x2, y2 = x - s/2, y - s/2, x + s/2, y + s/2
        shape = en["shape"]
        c = en["c"]
        if shape == "square":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline="#ffb3b3", width=2)
        elif shape == "diamond":
            self.canvas.create_polygon(x, y1, x2, y, x, y2, x1, y, fill=c, outline="#ffd8ff", width=2)
        elif shape == "triangle":
            self.canvas.create_polygon(x, y1, x2, y2, x1, y2, fill=c, outline="#ffe0c2", width=2)
        else:
            h = s * 0.5
            self.canvas.create_polygon(
                x-h*.9, y-h, x+h*.9, y-h, x+h*1.4, y, x+h*.9, y+h, x-h*.9, y+h, x-h*1.4, y,
                fill=c, outline="#e9ccff", width=2
            )

    def draw_panel(self):
        c = self.canvas
        c.create_rectangle(WORLD_W, 0, WIDTH, HEIGHT, fill="#0a0a12", outline="#2b2b46", width=2)
        c.create_text(WORLD_W + 130, 18, text="POWERS (click)", fill="#efe8ff", font=("Consolas", 14, "bold"))

        row_h = 28
        y0 = 110
        visible = (HEIGHT - y0 - 20) // row_h

        # info
        c.create_text(WORLD_W + 10, 44, anchor="nw", fill="#d7d7ff", font=("Consolas", 10),
                      text="Mouse wheel to scroll\nClick to buy/use power")

        for i in range(visible):
            idx = self.panel_scroll + i
            if idx >= len(self.powers):
                break
            p = self.powers[idx]
            y = y0 + i * row_h

            owned = p["id"] in self.owned
            active = p["id"] in self.active_toggles
            lv = getattr(self, f"lvl_{p['id']}", 0)
            cost = self.power_cost(p)

            bg = "#20203a" if owned else "#171729"
            if active:
                bg = "#263f2a"

            c.create_rectangle(WORLD_W + 10, y, WIDTH - 10, y + row_h - 2, fill=bg, outline="#3d3d60")

            status = ""
            if p["kind"] == "cast":
                status = f"Lv{lv}" if lv > 0 else f"{cost}c"
            elif owned:
                status = "ON" if active else "OWNED"
            else:
                status = f"{cost}c"

            c.create_text(WORLD_W + 16, y + 14, anchor="w", fill="#f0f0ff", font=("Consolas", 10, "bold"), text=p["name"])
            c.create_text(WIDTH - 18, y + 14, anchor="e", fill="#b8ffd0" if active else "#f8d9a8", font=("Consolas", 9, "bold"), text=status)

        # hovered/selected description not tracked; show tip
        c.create_text(WORLD_W + 10, HEIGHT - 50, anchor="nw", fill="#bfc3ff", font=("Consolas", 9),
                      text="Tip: buy toggle/passive once.\nCast powers can be bought repeatedly for levels.")

    def draw(self):
        c = self.canvas
        c.delete("all")

        # world bg/grid
        c.create_rectangle(0, 0, WORLD_W, HEIGHT, fill="#101010", outline="")
        for x in range(0, WORLD_W, 40):
            c.create_line(x, 0, x, HEIGHT, fill="#181818")
        for y in range(0, HEIGHT, 40):
            c.create_line(0, y, WORLD_W, y, fill="#181818")

        # world entities
        for d in self.drops:
            c.create_oval(d["x"]-5, d["y"]-5, d["x"]+5, d["y"]+5, fill="#ffe066", outline="")

        for b in self.bullets:
            r = b["r"]
            c.create_oval(b["x"]-r, b["y"]-r, b["x"]+r, b["y"]+r, fill="#ffd84d", outline="")

        for t in self.turrets:
            s = 16
            c.create_rectangle(t["x"]-s/2, t["y"]-s/2, t["x"]+s/2, t["y"]+s/2, fill="#ffdca8", outline="#fff3dd", width=2)

        for m in self.meteors:
            c.create_oval(m["x"]-8, m["y"]-8, m["x"]+8, m["y"]+8, fill="#ff7a44", outline="#ffd2b0")

        for en in self.enemies:
            self.draw_enemy(en)

        # player
        h = PLAYER_SIZE / 2
        c.create_rectangle(self.px-h, self.py-h, self.px+h, self.py+h, fill="#4aa8ff", outline="#cfe8ff", width=2)
        spear_len = 40 if self.dash_t > 0 else 28
        c.create_line(self.px, self.py, self.px + self.face_x*spear_len, self.py + self.face_y*spear_len,
                      fill="#fff07a" if self.dash_t > 0 else "#f4f7ff", width=5)

        if "dark_aura" in self.active_toggles:
            rr = 88
            c.create_oval(self.px-rr, self.py-rr, self.px+rr, self.py+rr, outline="#7d54ff", width=2)

        if "poison_cloud" in self.active_toggles:
            rr = 125
            c.create_oval(self.px-rr, self.py-rr, self.px+rr, self.py+rr, outline="#5dcf73", width=1)

        if "spike_ring" in self.active_toggles:
            c.create_oval(self.px-105, self.py-105, self.px+105, self.py+105, outline="#ffcc88", width=1)
            c.create_oval(self.px-130, self.py-130, self.px+130, self.py+130, outline="#ffcc88", width=1)

        if "orbit_blades" in self.active_toggles:
            for i in range(3):
                a = self.orbit_angle + i * (2 * math.pi / 3)
                bx, by = self.px + math.cos(a) * 46, self.py + math.sin(a) * 46
                c.create_oval(bx-6, by-6, bx+6, by+6, fill="#c9a3ff", outline="#f0e0ff")

        # HUD
        c.create_text(10, 10, anchor="nw", fill="#f0f0f0", font=("Consolas", 13, "bold"),
                      text=f"HP {int(self.hp)}/{self.max_hp}  Coins {self.coins}  Wave {self.wave}  Kills {self.kills}")
        c.create_text(10, 32, anchor="nw", fill="#d2d2d2", font=("Consolas", 10), text=self.banner)

        if self.game_over:
            c.create_text(WORLD_W//2, HEIGHT//2, text="GAME OVER\nPress R", fill="#ffd2a6", font=("Consolas", 30, "bold"), justify="center")

        self.draw_panel()

    def tick(self):
        self.update_logic()
        self.draw()
        self.root.after(FPS_MS, self.tick)


def main():
    root = tk.Tk()
    root.resizable(False, False)
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
