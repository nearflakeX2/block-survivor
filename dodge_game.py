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
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind_all("<MouseWheel>", self.on_wheel)

        self.pause_btn = (WORLD_W - 110, 10, WORLD_W - 20, 40)

        self.setup_powers()

        self.mode = None
        self.in_start_menu = True
        self.mode_buttons = {
            "Classic": (WORLD_W//2 - 220, HEIGHT//2 - 40, WORLD_W//2 - 40, HEIGHT//2 + 20),
            "Hardcore": (WORLD_W//2 + 40, HEIGHT//2 - 40, WORLD_W//2 + 220, HEIGHT//2 + 20),
        }

        self.reset()
        self.root.after(self.spawn_ms, self.spawn_enemy)
        self.tick()

    def setup_powers(self):
        # 20 unique powers
        self.powers = [
            {"id":"dark_aura","name":"Dark Aura","cost":100,"kind":"toggle","rarity":"common"},
            {"id":"orbit_blades","name":"Orbit Blades","cost":140,"kind":"toggle","rarity":"rare"},
            {"id":"blood_nova","name":"Blood Nova","cost":160,"kind":"cast","rarity":"epic"},
            {"id":"time_freeze","name":"Time Freeze","cost":170,"kind":"cast","rarity":"epic"},
            {"id":"auto_turret","name":"Auto Turret","cost":180,"kind":"cast","rarity":"rare"},
            {"id":"chain_lightning","name":"Chain Lightning","cost":190,"kind":"cast","rarity":"epic"},
            {"id":"meteor_drop","name":"Meteor Shower","cost":210,"kind":"cast","rarity":"legendary"},
            {"id":"poison_cloud","name":"Poison Cloud","cost":150,"kind":"toggle","rarity":"common"},
            {"id":"spike_ring","name":"Spike Ring","cost":145,"kind":"toggle","rarity":"common"},
            {"id":"blade_dash_plus","name":"Blade Dash+","cost":120,"kind":"passive","rarity":"common"},
            {"id":"rapid_core","name":"Rapid Core","cost":120,"kind":"passive","rarity":"common"},
            {"id":"damage_core","name":"Damage Core","cost":120,"kind":"passive","rarity":"rare"},
            {"id":"speed_core","name":"Speed Core","cost":110,"kind":"passive","rarity":"common"},
            {"id":"regen_core","name":"Regen Core","cost":130,"kind":"passive","rarity":"rare"},
            {"id":"maxhp_core","name":"MaxHP Core","cost":130,"kind":"passive","rarity":"common"},
            {"id":"magnet_core","name":"Magnet Core","cost":125,"kind":"passive","rarity":"common"},
            {"id":"ricochet_shot","name":"Ricochet Shot","cost":160,"kind":"passive","rarity":"rare"},
            {"id":"split_shot","name":"Shotgun Blast","cost":170,"kind":"passive","rarity":"epic"},
            {"id":"multi_shot","name":"Multi Shot","cost":160,"kind":"passive","rarity":"rare"},
            {"id":"clone_swarm","name":"Clone Swarm","cost":180,"kind":"cast","rarity":"epic"},
            {"id":"rpg_launcher","name":"RPG Launcher","cost":165,"kind":"passive","rarity":"legendary"},
            {"id":"machine_gun","name":"Machine Gun","cost":170,"kind":"passive","rarity":"legendary"},
            {"id":"black_hole_core","name":"Black Hole Core","cost":220,"kind":"cast","rarity":"legendary"},
            {"id":"flamethrower_arc","name":"Flamethrower Arc","cost":150,"kind":"passive","rarity":"rare"},
            {"id":"frost_mine","name":"Frost Mine","cost":160,"kind":"cast","rarity":"rare"},
            {"id":"shield_drone","name":"Shield Drone","cost":170,"kind":"toggle","rarity":"epic"},
            {"id":"vampiric_rounds","name":"Vampiric Rounds","cost":165,"kind":"passive","rarity":"epic"},
            {"id":"shockwave_stomp","name":"Shockwave Stomp","cost":175,"kind":"passive","rarity":"epic"},
            {"id":"orbital_laser","name":"Orbital Laser","cost":210,"kind":"passive","rarity":"legendary"},
            {"id":"decoy_hologram","name":"Decoy Hologram","cost":155,"kind":"cast","rarity":"rare"},
            {"id":"execution_protocol","name":"Execution Protocol","cost":165,"kind":"passive","rarity":"epic"},
            {"id":"bounty_scanner","name":"Bounty Scanner","cost":145,"kind":"passive","rarity":"rare"},
            {"id":"cluster_rpg","name":"Cluster RPG","cost":200,"kind":"passive","rarity":"legendary"},
            {"id":"phoenix_revive","name":"Phoenix Revive","cost":240,"kind":"passive","rarity":"legendary"},
            {"id":"chain_hook","name":"Chain Hook","cost":165,"kind":"passive","rarity":"epic"},
            {"id":"thunder_totem","name":"Thunder Totem","cost":185,"kind":"cast","rarity":"epic"},
            {"id":"overclock_mode","name":"Overclock Mode","cost":195,"kind":"passive","rarity":"legendary"},
            {"id":"nuke_mine","name":"Nuke Mine","cost":260,"kind":"passive","rarity":"legendary"},
        ]

        self.descriptions = {
            "dark_aura":"Aura gets bigger/stronger per level.",
            "orbit_blades":"Rings go farther and hit harder per level.",
            "blood_nova":"Bigger nova radius and damage per level.",
            "time_freeze":"Longer and stronger freeze each level.",
            "auto_turret":"Deploy stronger turret and visible bullets.",
            "chain_lightning":"More targets and damage per level.",
            "meteor_drop":"Red warning circles then explosion, random map.",
            "poison_cloud":"Bigger cloud and damage per level.",
            "spike_ring":"Ring radius and damage increase per level.",
            "blade_dash_plus":"Dash gets longer and stronger.",
            "rapid_core":"Permanent faster fire rate.",
            "damage_core":"Permanent bullet damage up.",
            "speed_core":"Permanent movement speed up.",
            "regen_core":"Permanent HP regeneration.",
            "maxhp_core":"Permanent max HP up.",
            "magnet_core":"Pulls drops toward you.",
            "ricochet_shot":"Bullets pierce more with levels.",
            "split_shot":"Shotgun pellets blast in a wide cone.",
            "multi_shot":"Fires tighter parallel shots.",
            "clone_swarm":"Spawns attacking clones.",
            "rpg_launcher":"Also fires rockets while shooting bullets.",
            "machine_gun":"Huge fire-rate boost and extra bullet stream.",
        }

    def reset(self):
        self.running = True
        self.game_over = False
        self.paused = False

        self.power_choice_open = False
        self.power_choices = []
        self.next_choice_coin = 120

        self.px, self.py = WORLD_W // 2, HEIGHT // 2
        self.face_x, self.face_y = 1.0, 0.0

        mode_hp_mul = 0.8 if self.mode == "Hardcore" else 1.0
        self.hp = float(BASE_HP * mode_hp_mul)
        self.max_hp = int(BASE_HP * mode_hp_mul)
        self.coins = 0
        self.kills = 0
        self.wave = 1

        self.enemies = []
        self.bullets = []
        self.drops = []
        self.turrets = []
        self.turret_bullets = []
        self.meteors = []
        self.explosions = []
        self.clones = []
        self.rockets = []
        self.smoke = []
        self.float_texts = []
        self.boss_active = False
        self.black_holes = []
        self.frost_mines = []
        self.decoys = []
        self.totems = []
        self.enemy_bullets = []
        self.fx = {"flame": [], "shock": [], "laser": [], "hook": [], "throw": [], "zap": []}

        self.shake_t = 0
        self.shake_mag = 0

        self.spawn_ms = int(SPAWN_MS * (0.78 if self.mode == "Hardcore" else 1.0))
        self.frame = 0

        self.shoot_cd = 0
        self.dash_cd = 0
        self.dash_t = 0
        self.dash_vx = 0
        self.dash_vy = 0

        self.freeze_t = 0
        self.cast_cd = 0

        # reload/cooldown timers (in frames)
        self.cooldowns = {
            "meteor_drop": 0,
            "blood_nova": 0,
            "chain_lightning": 0,
            "time_freeze": 0,
            "clone_swarm": 0,
            "auto_turret": 0,
            "rpg_launcher": 0,
            "black_hole_core": 0,
            "frost_mine": 0,
            "decoy_hologram": 0,
            "thunder_totem": 0,
            "flamethrower_arc": 0,
            "shockwave_stomp": 0,
            "orbital_laser": 0,
            "chain_hook": 0,
            "shield_drone": 0,
            "nuke_mine": 0,
            "split_shot": 0,
        }

        # base cooldown lengths (reduced by higher levels for cast powers)
        self.cooldown_base = {
            "meteor_drop": 240,
            "blood_nova": 170,
            "chain_lightning": 120,
            "time_freeze": 280,
            "clone_swarm": 220,
            "auto_turret": 170,
            "black_hole_core": 300,
            "frost_mine": 140,
            "decoy_hologram": 170,
            "thunder_totem": 200,
            "flamethrower_arc": 14,
            "shockwave_stomp": 150,
            "orbital_laser": 170,
            "chain_hook": 120,
            "shield_drone": 22,
            "nuke_mine": 1800,
            "split_shot": 40,
        }

        # power ownership and runtime
        self.owned = set()
        self.power_lv = {}
        self.active_toggles = set()

        # stats from passives
        self.stat_damage = 0
        self.stat_speed = 0
        self.stat_regen = 0
        self.stat_rapid = 0
        self.stat_magnet = 0
        self.stat_ricochet = False
        self.stat_split = False
        self.stat_multishot = 0
        self.stat_dash_plus = False
        self.stat_machinegun = 0
        self.stat_vamp = 0
        self.stat_exec = 0
        self.stat_bounty = 0
        self.stat_cluster = 0
        self.stat_flamer = 0
        self.stat_shockwave = 0
        self.stat_orbital = 0
        self.stat_hook = 0
        self.stat_overclock = 0
        self.phoenix_charge = 0
        self.stat_nuke = 0

        self.orbit_angle = 0
        self.panel_scroll = 0.0
        self.panel_scroll_dir = 1
        self.panel_hovering = False
        self.banner = "Mouse: click powers on right panel | Wheel scroll | SPACE dash | R restart"

    # ---------- input ----------
    def on_key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)

        if k == "f11":
            self.root.attributes("-fullscreen", not bool(self.root.attributes("-fullscreen")))
        if k == "escape":
            self.root.attributes("-fullscreen", False)

        if self.in_start_menu:
            return
        if k == "r" and self.game_over:
            self.reset()
        if k == "p" and self.running and not self.game_over:
            self.paused = not self.paused
            self.banner = "Paused" if self.paused else "Resumed"

        # quick test controls while paused
        if self.paused and not self.game_over:
            if k == "1":
                self.coins += 200
                self.banner = "TEST: +200 coins"
            elif k == "2":
                self.hp = self.max_hp
                self.banner = "TEST: full heal"
            elif k == "3":
                self.wave += 1
                self.banner = f"TEST: wave {self.wave}"
            elif k == "4":
                self.enemies.clear()
                self.banner = "TEST: cleared enemies"

        if k == "space" and self.running and not self.paused:
            self.start_dash()

    def on_key_up(self, e):
        self.keys.discard(e.keysym.lower())

    def panel_powers(self):
        if self.mode == "Hardcore":
            return [p for p in self.powers if p["id"] in self.owned]
        return self.powers

    def on_wheel(self, e):
        # scroll power list
        delta = -1 if e.delta > 0 else 1
        visible = max(1, (HEIGHT - 110 - 50) // 34)
        max_scroll = max(0, len(self.panel_powers()) - visible)
        self.panel_scroll = max(0.0, min(float(max_scroll), self.panel_scroll + delta))

    def on_mouse_move(self, e):
        panel_x = WORLD_W + 10
        panel_w = WIDTH - WORLD_W - 20
        row_h = 34
        y0 = 110
        panel_list = self.panel_powers()
        visible = max(1, (HEIGHT - y0 - 50) // row_h)
        idx_in_view = (e.y - y0) // row_h
        in_rows = (panel_x <= e.x <= panel_x + panel_w and idx_in_view >= 0 and idx_in_view < visible)
        idx = int(self.panel_scroll) + idx_in_view if idx_in_view >= 0 else -1
        self.panel_hovering = bool(in_rows and 0 <= idx < len(panel_list))

    def on_click(self, e):
        if self.in_start_menu:
            for name, (x1, y1, x2, y2) in self.mode_buttons.items():
                if x1 <= e.x <= x2 and y1 <= e.y <= y2:
                    self.mode = name
                    self.in_start_menu = False
                    self.reset()
                    self.banner = f"Mode: {name}"
                    return
            return

        if self.power_choice_open:
            cx, cy, cw, ch = WORLD_W//2 - 120, 180, 240, 72
            for i, p in enumerate(self.power_choices):
                yy = cy + i * (ch + 16)
                if cx <= e.x <= cx + cw and yy <= e.y <= yy + ch:
                    self.power_choice_open = False
                    self.buy_or_use_power(p)
                    self.next_choice_coin += 120
                    return
            return

        x1, y1, x2, y2 = self.pause_btn
        if x1 <= e.x <= x2 and y1 <= e.y <= y2 and self.running and not self.game_over:
            self.paused = not self.paused
            self.banner = "Paused" if self.paused else "Resumed"
            return

        if e.x < WORLD_W:
            return

        # identify clicked power row
        panel_x = WORLD_W + 10
        panel_w = WIDTH - WORLD_W - 20
        row_h = 34
        y0 = 110
        panel_list = self.panel_powers()

        if not (panel_x <= e.x <= panel_x + panel_w):
            return

        # always-visible scroll buttons
        if y0 - 34 <= e.y <= y0 - 6:
            self.panel_scroll = max(0.0, self.panel_scroll - 1)
            return
        if HEIGHT - 34 <= e.y <= HEIGHT - 6:
            visible = max(1, (HEIGHT - 110 - 50) // 34)
            max_scroll = max(0, len(panel_list) - visible)
            self.panel_scroll = min(float(max_scroll), self.panel_scroll + 1)
            return

        idx_in_view = (e.y - y0) // row_h
        if idx_in_view < 0:
            return
        idx = int(self.panel_scroll) + idx_in_view
        if idx >= len(panel_list):
            return

        self.buy_or_use_power(panel_list[idx])

    # ---------- power system ----------
    def power_cost(self, p):
        pid = p["id"]
        base = p["cost"]
        lv = self.power_lv.get(pid, 0)
        return base + lv * 45

    def get_cooldown_max(self, pid, lv):
        if pid not in self.cooldown_base:
            return 0
        # each level trims cooldown a bit but keeps minimum floor
        return max(45, self.cooldown_base[pid] - (lv - 1) * 12)

    def roll_power_choices(self, n=3):
        pool = self.powers[:]
        random.shuffle(pool)
        return pool[:min(n, len(pool))]

    def buy_or_use_power(self, p):
        pid = p["id"]
        kind = p["kind"]

        # cast powers have reload timers
        if kind == "cast" and self.cooldowns.get(pid, 0) > 0:
            left = self.cooldowns[pid] // 60 + 1
            self.banner = f"{p['name']} reloading ({left}s)"
            return

        cost = self.power_cost(p)
        if self.coins < cost:
            self.banner = f"Need {cost} coins"
            return

        self.coins -= cost
        new_lv = self.power_lv.get(pid, 0) + 1
        self.power_lv[pid] = new_lv
        self.owned.add(pid)

        if kind in ("toggle", "passive"):
            if kind == "toggle":
                self.active_toggles.add(pid)  # always on after buy
            self.apply_passive(pid, new_lv)
            self.banner = f"{p['name']} upgraded to Lv{new_lv}"
        else:
            self.cast_power(pid, new_lv)
            self.cooldowns[pid] = self.get_cooldown_max(pid, new_lv)
            self.banner = f"{p['name']} cast Lv{new_lv}"

    def apply_passive(self, pid, lv):
        if pid == "rapid_core": self.stat_rapid += 1
        elif pid == "damage_core": self.stat_damage += 8
        elif pid == "speed_core": self.stat_speed += 0.55
        elif pid == "regen_core": self.stat_regen += 0.2
        elif pid == "maxhp_core": self.max_hp += 24; self.hp += 24
        elif pid == "magnet_core": self.stat_magnet += 35
        elif pid == "ricochet_shot": self.stat_ricochet = True
        elif pid == "split_shot": self.stat_split = True
        elif pid == "multi_shot": self.stat_multishot += 1
        elif pid == "blade_dash_plus": self.stat_dash_plus = True
        elif pid == "rpg_launcher":
            pass
        elif pid == "machine_gun":
            self.stat_machinegun += 1
            self.stat_rapid += 1
        elif pid == "vampiric_rounds": self.stat_vamp += 1
        elif pid == "execution_protocol": self.stat_exec += 1
        elif pid == "bounty_scanner": self.stat_bounty += 1
        elif pid == "cluster_rpg": self.stat_cluster += 1
        elif pid == "flamethrower_arc": self.stat_flamer += 1
        elif pid == "shockwave_stomp": self.stat_shockwave += 1
        elif pid == "orbital_laser": self.stat_orbital += 1
        elif pid == "chain_hook": self.stat_hook += 1
        elif pid == "overclock_mode": self.stat_overclock += 1; self.stat_rapid += 1; self.stat_speed += 0.35
        elif pid == "phoenix_revive": self.phoenix_charge = 1
        elif pid == "nuke_mine": self.stat_nuke += 1

    def cast_power(self, pid, lv):
        if pid == "blood_nova":
            r = 130 + lv * 22
            dmg = 55 + lv * 22
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= r:
                    en["hp"] -= dmg
        elif pid == "time_freeze":
            self.freeze_t = max(self.freeze_t, 80 + lv * 30)
        elif pid == "auto_turret":
            # turret now stays until destroyed (no ttl)
            self.turrets.append({"x": self.px, "y": self.py, "cd": 0, "lv": lv, "hp": 70 + lv*30, "max": 70 + lv*30})
        elif pid == "chain_lightning":
            targets = sorted(self.enemies, key=lambda e: (e["x"]-self.px)**2 + (e["y"]-self.py)**2)[:(3 + lv)]
            dmg = 35 + lv * 12
            for t in targets:
                t["hp"] -= dmg
        elif pid == "meteor_drop":
            for _ in range(2 + lv):
                rx = random.randint(40, WORLD_W - 40)
                ry = random.randint(40, HEIGHT - 40)
                self.meteors.append({"x": rx, "y": ry, "t": 40, "max_t": 40, "dmg": 60 + lv * 16, "r": 70 + lv*8})
        elif pid == "clone_swarm":
            for _ in range(1 + lv // 2):
                self.clones.append({"x": self.px, "y": self.py, "ttl": 260 + lv*20, "lv": lv})
        elif pid == "black_hole_core":
            tx, ty = self.px + self.face_x*100, self.py + self.face_y*100
            self.black_holes.append({"x": tx, "y": ty, "t": 120 + lv*12, "r": 90 + lv*10, "lv": lv})
            self.fx["throw"].append({"x1": self.px, "y1": self.py, "x2": tx, "y2": ty, "t": 12, "c": "#9b7bff"})
        elif pid == "frost_mine":
            tx, ty = self.px + self.face_x*35, self.py + self.face_y*35
            self.frost_mines.append({"x": tx, "y": ty, "t": 360, "r": 85 + lv*8, "lv": lv})
            self.fx["throw"].append({"x1": self.px, "y1": self.py, "x2": tx, "y2": ty, "t": 10, "c": "#9fd6ff"})
        elif pid == "decoy_hologram":
            tx, ty = self.px + random.randint(-80,80), self.py + random.randint(-80,80)
            self.decoys.append({"x": tx, "y": ty, "t": 260 + lv*40, "lv": lv})
            self.fx["throw"].append({"x1": self.px, "y1": self.py, "x2": tx, "y2": ty, "t": 10, "c": "#7bf0ff"})
        elif pid == "thunder_totem":
            tx, ty = self.px + self.face_x*25, self.py + self.face_y*25
            self.totems.append({"x": tx, "y": ty, "t": 320 + lv*40, "lv": lv, "cd": 0})
            self.fx["throw"].append({"x1": self.px, "y1": self.py, "x2": tx, "y2": ty, "t": 10, "c": "#ffd28c"})
        elif pid == "rpg_launcher":
            pass
    # ---------- gameplay ----------
    def spawn_enemy(self):
        if self.running and not self.in_start_menu and not self.paused and not self.power_choice_open:
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

            variant = random.choice(["normal", "normal", "normal", "charger", "tank", "shooter"])
            if variant == "charger":
                sp *= 1.5
                hp *= 0.9
                colors[tier] = "#ff6e6e"
            elif variant == "tank":
                hp *= 2.1
                sp *= 0.75
                size += 8
                colors[tier] = "#8a63ff"
            elif variant == "shooter":
                hp *= 1.15
                sp *= 0.95
                colors[tier] = "#ffb347"

            # boss wave every 5 waves
            is_boss = (self.wave % 5 == 0 and not self.boss_active)
            boss_type = None
            if is_boss:
                hp *= 8
                size += 20
                sp *= 0.95
                variant = "boss"
                boss_types = ["brute", "summoner", "artillery", "vampire", "storm"]
                boss_type = boss_types[(self.wave // 5) % len(boss_types)]
                self.boss_active = True
                self.float_texts.append({"x": WORLD_W//2, "y": 90, "t": 90, "txt": f"BOSS WAVE {self.wave}! {boss_type.upper()}", "c": "#ffcc66"})

            self.enemies.append({"x": x, "y": y, "hp": hp, "max": hp, "sp": sp, "s": size, "shape": shapes[tier], "c": colors[tier], "variant": variant, "shoot_cd": random.randint(60,120), "boss": is_boss, "boss_type": boss_type, "skill_cd": random.randint(80,140)})

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
        if not self.enemies:
            return

        targets = sorted(self.enemies, key=lambda e: (e["x"] - self.px) ** 2 + (e["y"] - self.py) ** 2)
        t1 = targets[0]
        t2 = targets[1] if len(targets) > 1 else t1
        t3 = targets[2] if len(targets) > 2 else t2
        t4 = targets[3] if len(targets) > 3 else t1

        # default/multi-shot aims at 4th nearest
        base4 = math.atan2(t4["y"] - self.py, t4["x"] - self.px)
        spread = [0]
        if self.stat_multishot > 0:
            spread = [-0.06, 0, 0.06]

        for s in spread:
            a = base4 + s
            sp = BASE_BULLET_SPEED + self.stat_damage * 0.04
            self.bullets.append({"x": self.px, "y": self.py, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp, "r": 4, "pierce": self.power_lv.get("ricochet_shot",0)})

        # shotgun aims at nearest enemy
        if self.stat_split and self.cooldowns["split_shot"] <= 0:
            base1 = math.atan2(t1["y"] - self.py, t1["x"] - self.px)
            pellets = 6 + self.power_lv.get("split_shot", 0)
            for _ in range(pellets):
                j = random.uniform(-0.28, 0.28)
                a = base1 + j
                sp = BASE_BULLET_SPEED - 0.8 + random.uniform(-0.2, 0.2)
                self.bullets.append({"x": self.px, "y": self.py, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp, "r": 3, "pierce": 0})
            self.cooldowns["split_shot"] = self.get_cooldown_max("split_shot", max(1, self.power_lv.get("split_shot", 1)))

        # machine gun aims at 2nd and 3rd nearest
        if self.stat_machinegun > 0:
            mg_targets = [t2, t3]
            for i in range(self.stat_machinegun):
                tm = mg_targets[i % len(mg_targets)]
                basem = math.atan2(tm["y"] - self.py, tm["x"] - self.px)
                j = random.uniform(-0.025, 0.025)
                a = basem + j
                sp = BASE_BULLET_SPEED + 1.6 + self.stat_machinegun * 0.3
                self.bullets.append({"x": self.px, "y": self.py, "vx": math.cos(a) * sp, "vy": math.sin(a) * sp, "r": 3, "pierce": 0})

        # RPG launcher keeps using nearest
        rpg_lv = self.power_lv.get("rpg_launcher", 0)
        if rpg_lv > 0 and self.cooldowns["rpg_launcher"] <= 0:
            base1 = math.atan2(t1["y"] - self.py, t1["x"] - self.px)
            rv = 5.8 + rpg_lv * 0.7
            self.rockets.append({"x": self.px, "y": self.py, "vx": math.cos(base1)*rv, "vy": math.sin(base1)*rv, "dmg": 80 + rpg_lv*26, "r": 56 + rpg_lv*6})
            self.cooldowns["rpg_launcher"] = max(20, 80 - rpg_lv * 8)

        cd = int(BASE_FIRE_CD * (1 - 0.12 * self.stat_rapid))
        self.shoot_cd = max(3, cd)

    def update_logic(self):
        if not self.running:
            return
        if self.paused or self.power_choice_open or self.in_start_menu:
            return

        self.frame += 1

        # auto-scroll power panel smoothly (single-direction loop)
        panel_len = len(self.panel_powers())
        visible = max(1, (HEIGHT - 110 - 50) // 34)
        max_scroll = max(0, panel_len - visible)
        if max_scroll > 0:
            self.panel_scroll = max(0.0, min(float(max_scroll), self.panel_scroll))
            if not self.panel_hovering:
                self.panel_scroll += 0.035
                if self.panel_scroll > max_scroll:
                    self.panel_scroll = 0.0
        else:
            self.panel_scroll = 0.0

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
            lv = self.power_lv.get("dark_aura", 1)
            dark_r = 88 + lv * 12
            dark_dmg = 1.6 + lv * 0.45
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= dark_r + en["s"] / 2:
                    en["hp"] -= dark_dmg

        if "poison_cloud" in self.active_toggles:
            lv = self.power_lv.get("poison_cloud", 1)
            pr = 125 + lv * 10
            for en in self.enemies:
                if math.hypot(en["x"] - self.px, en["y"] - self.py) <= pr + en["s"] / 2:
                    en["hp"] -= 1.0 + lv*0.28

        if "spike_ring" in self.active_toggles:
            lv = self.power_lv.get("spike_ring", 1)
            r1 = 105 + lv * 8
            r2 = 130 + lv * 10
            for en in self.enemies:
                d = math.hypot(en["x"] - self.px, en["y"] - self.py)
                if r1 <= d <= r2:
                    en["hp"] -= 2.0 + lv * 0.5

        if "orbit_blades" in self.active_toggles:
            lv = self.power_lv.get("orbit_blades", 1)
            self.orbit_angle += 0.18 + lv*0.01
            orbit_r = 46 + lv * 7
            for i in range(3):
                a = self.orbit_angle + i * (2 * math.pi / 3)
                bx, by = self.px + math.cos(a) * orbit_r, self.py + math.sin(a) * orbit_r
                for en in self.enemies:
                    if math.hypot(en["x"] - bx, en["y"] - by) <= en["s"] / 2 + 11 + lv:
                        en["hp"] -= 5 + lv*1.2

        if "shield_drone" in self.active_toggles and self.cooldowns["shield_drone"] <= 0:
            lv = self.power_lv.get("shield_drone", 1)
            sr = 34 + lv * 5
            for en in self.enemies:
                if math.hypot(en["x"]-self.px, en["y"]-self.py) <= sr + en["s"]/2:
                    en["hp"] -= 3 + lv
            self.cooldowns["shield_drone"] = self.get_cooldown_max("shield_drone", lv)

        # laser gun upgrade from damage core levels
        if self.power_lv.get("damage_core", 0) >= 2 and self.enemies:
            t = self.nearest_enemy()
            t["hp"] -= 1.0 + self.power_lv.get("damage_core",0)*0.5

        # flamethrower arc
        if self.stat_flamer > 0 and self.cooldowns["flamethrower_arc"] <= 0:
            for en in self.enemies:
                dx, dy = en["x"] - self.px, en["y"] - self.py
                d = math.hypot(dx, dy) + 1e-6
                if d < 115 + self.stat_flamer * 18:
                    ndx, ndy = dx / d, dy / d
                    dot = ndx * self.face_x + ndy * self.face_y
                    if dot > 0.58:
                        en["hp"] -= 0.7 + self.stat_flamer * 0.35
            self.fx["flame"].append({"x": self.px, "y": self.py, "fx": self.face_x, "fy": self.face_y, "t": 14})
            self.cooldowns["flamethrower_arc"] = self.get_cooldown_max("flamethrower_arc", self.stat_flamer)

        # shockwave stomp pulse
        if self.stat_shockwave > 0 and self.cooldowns["shockwave_stomp"] <= 0:
            rr = 90 + self.stat_shockwave * 16
            for en in self.enemies:
                if math.hypot(en["x"]-self.px, en["y"]-self.py) <= rr:
                    en["hp"] -= 22 + self.stat_shockwave * 8
            self.fx["shock"].append({"x": self.px, "y": self.py, "r": rr, "t": 16, "max": 16})
            self.cooldowns["shockwave_stomp"] = self.get_cooldown_max("shockwave_stomp", self.stat_shockwave)

        # chain hook
        if self.stat_hook > 0 and self.enemies and self.cooldowns["chain_hook"] <= 0:
            t = self.nearest_enemy()
            if t:
                self.fx["hook"].append({"x1": self.px, "y1": self.py, "x2": t["x"], "y2": t["y"], "t": 10})
                t["x"] += (self.px - t["x"]) * 0.35
                t["y"] += (self.py - t["y"]) * 0.35
                t["hp"] -= 8 + self.stat_hook * 4
                self.cooldowns["chain_hook"] = self.get_cooldown_max("chain_hook", self.stat_hook)

        # orbital laser sweep
        if self.stat_orbital > 0 and self.cooldowns["orbital_laser"] <= 0:
            yline = random.randint(30, HEIGHT-30)
            for en in self.enemies:
                if abs(en["y"] - yline) < 16:
                    en["hp"] -= 40 + self.stat_orbital * 11
            self.fx["laser"].append({"y": yline, "t": 14})
            self.float_texts.append({"x": WORLD_W//2, "y": yline, "t": 18, "txt": "LASER", "c": "#ff6666"})
            self.cooldowns["orbital_laser"] = self.get_cooldown_max("orbital_laser", self.stat_orbital)

        # nuke mine: every 30s, huge blast that wipes roughly half the map
        if self.stat_nuke > 0 and self.cooldowns["nuke_mine"] <= 0:
            nx = random.randint(120, WORLD_W - 120)
            ny = random.randint(120, HEIGHT - 120)
            nr = int(min(WORLD_W, HEIGHT) * 0.5)
            self.explosions.append({"x": nx, "y": ny, "t": 28, "max": 28, "r": nr})
            for en in self.enemies:
                if math.hypot(en["x"] - nx, en["y"] - ny) <= nr:
                    en["hp"] -= 9999
            self.shake_t = max(self.shake_t, 16)
            self.shake_mag = max(self.shake_mag, 12)
            self.float_texts.append({"x": nx, "y": ny - 20, "t": 45, "txt": "NUKE", "c": "#ff5252"})
            self.cooldowns["nuke_mine"] = self.get_cooldown_max("nuke_mine", self.stat_nuke)

        # black holes
        alive_bh = []
        for bh in self.black_holes:
            bh["t"] -= 1
            for en in self.enemies:
                dx, dy = bh["x"] - en["x"], bh["y"] - en["y"]
                d = math.hypot(dx, dy) + 1e-6
                if d < bh["r"]:
                    pull = (bh["r"] - d) * 0.02
                    en["x"] += dx / d * pull
                    en["y"] += dy / d * pull
                    en["hp"] -= 0.9 + bh["lv"] * 0.25
            if bh["t"] > 0:
                alive_bh.append(bh)
        self.black_holes = alive_bh

        # frost mines
        alive_mines = []
        for m in self.frost_mines:
            m["t"] -= 1
            triggered = False
            for en in self.enemies:
                if math.hypot(en["x"]-m["x"], en["y"]-m["y"]) <= 18:
                    for e2 in self.enemies:
                        if math.hypot(e2["x"]-m["x"], e2["y"]-m["y"]) <= m["r"]:
                            e2["hp"] -= 25 + m["lv"] * 9
                            e2["sp"] *= 0.8
                    triggered = True
                    break
            if m["t"] > 0 and not triggered:
                alive_mines.append(m)
        self.frost_mines = alive_mines

        # thunder totems
        alive_totems = []
        for t in self.totems:
            t["t"] -= 1
            t["cd"] = max(0, t["cd"] - 1)
            if t["cd"] == 0 and self.enemies:
                targets = sorted(self.enemies, key=lambda e: (e["x"]-t["x"])**2 + (e["y"]-t["y"])**2)[:(1 + t["lv"]//2)]
                for z in targets:
                    if math.hypot(z["x"]-t["x"], z["y"]-t["y"]) < 240:
                        z["hp"] -= 20 + t["lv"] * 8
                        self.fx["zap"].append({"x1": t["x"], "y1": t["y"], "x2": z["x"], "y2": z["y"], "t": 8})
                t["cd"] = max(15, 55 - t["lv"]*4)
            if t["t"] > 0:
                alive_totems.append(t)
        self.totems = alive_totems

        # decoys
        self.decoys = [d for d in self.decoys if (d.update({"t": d["t"]-1}) or d["t"] > 0)]

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
                    dmg = BASE_BULLET_DMG + self.stat_damage
                    if self.stat_exec > 0 and en["hp"] < en["max"] * 0.3:
                        dmg += 10 + self.stat_exec * 5
                    en["hp"] -= dmg
                    if self.stat_vamp > 0:
                        self.hp = min(self.max_hp, self.hp + 0.15 * self.stat_vamp)
                    if b["pierce"] > 0:
                        b["pierce"] -= 1
                    else:
                        hit = True
                    break
            if not hit:
                alive_b.append(b)
        self.bullets = alive_b

        # turrets (visible bullets)
        alive_t = []
        for t in self.turrets:
            t["cd"] = max(0, t["cd"] - 1)
            if t["hp"] <= 0:
                continue
            if self.enemies and t["cd"] == 0:
                target = min(self.enemies, key=lambda e: (e["x"] - t["x"])**2 + (e["y"] - t["y"])**2)
                dx, dy = target["x"]-t["x"], target["y"]-t["y"]
                d = math.hypot(dx, dy) + 1e-6
                if d < 300:
                    sp = 9 + t["lv"]*0.6
                    self.turret_bullets.append({"x": t["x"], "y": t["y"], "vx": dx/d*sp, "vy": dy/d*sp, "dmg": 20+t["lv"]*8, "ttl": 80})
                    t["cd"] = max(6, 14 - t["lv"])
            alive_t.append(t)
        self.turrets = alive_t

        # turret bullets update
        alive_tb = []
        for b in self.turret_bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["ttl"] -= 1
            if b["ttl"] <= 0:
                continue
            hit = False
            for en in self.enemies:
                if math.hypot(en["x"]-b["x"], en["y"]-b["y"]) <= en["s"]/2 + 4:
                    en["hp"] -= b["dmg"]
                    hit = True
                    break
            if not hit:
                alive_tb.append(b)
        self.turret_bullets = alive_tb

        # meteors (red circles shrink then explode)
        alive_m = []
        for m in self.meteors:
            m["t"] -= 1
            if m["t"] <= 0:
                self.explosions.append({"x": m["x"], "y": m["y"], "t": 16, "max": 16, "r": m["r"]})
                self.shake_t = max(self.shake_t, 8)
                self.shake_mag = max(self.shake_mag, 7)
                for en in self.enemies:
                    if math.hypot(en["x"] - m["x"], en["y"] - m["y"]) < m["r"]:
                        en["hp"] -= m["dmg"]
            else:
                alive_m.append(m)
        self.meteors = alive_m

        # clones
        alive_c = []
        for c in self.clones:
            c["ttl"] -= 1
            if c["ttl"] <= 0:
                continue
            if self.enemies:
                t = min(self.enemies, key=lambda e: (e["x"]-c["x"])**2 + (e["y"]-c["y"])**2)
                dx, dy = t["x"]-c["x"], t["y"]-c["y"]
                d = math.hypot(dx,dy) + 1e-6
                c["x"] += dx/d * (4.5 + c["lv"]*0.25)
                c["y"] += dy/d * (4.5 + c["lv"]*0.25)
                if d < t["s"]/2 + 10:
                    t["hp"] -= 14 + c["lv"]*4
            alive_c.append(c)
        self.clones = alive_c

        # rockets
        alive_r = []
        for r in self.rockets:
            # trailing smoke
            self.smoke.append({"x": r["x"], "y": r["y"], "t": 22, "max": 22, "r": random.uniform(4.0, 7.5)})

            r["x"] += r["vx"]
            r["y"] += r["vy"]
            if r["x"] < -20 or r["x"] > WORLD_W+20 or r["y"] < -20 or r["y"] > HEIGHT+20:
                continue
            hit = False
            for en in self.enemies:
                if math.hypot(en["x"]-r["x"], en["y"]-r["y"]) <= en["s"]/2 + 7:
                    self.explosions.append({"x": r["x"], "y": r["y"], "t": 18, "max": 18, "r": r["r"] + 24})
                    self.shake_t = max(self.shake_t, 10)
                    self.shake_mag = max(self.shake_mag, 9)
                    for aoe in self.enemies:
                        if math.hypot(aoe["x"]-r["x"], aoe["y"]-r["y"]) < r["r"]:
                            aoe["hp"] -= r["dmg"]

                    if self.stat_cluster > 0:
                        for _ in range(2 + self.stat_cluster):
                            ang = random.random() * math.pi * 2
                            bx = r["x"] + math.cos(ang) * random.randint(20, 55)
                            by = r["y"] + math.sin(ang) * random.randint(20, 55)
                            self.explosions.append({"x": bx, "y": by, "t": 10, "max": 10, "r": 26})
                            for aoe2 in self.enemies:
                                if math.hypot(aoe2["x"]-bx, aoe2["y"]-by) < 30:
                                    aoe2["hp"] -= 20 + self.stat_cluster * 8
                    hit = True
                    break
            if not hit:
                alive_r.append(r)
        self.rockets = alive_r

        # smoke timer
        alive_s = []
        for s in self.smoke:
            s["t"] -= 1
            if s["t"] > 0:
                alive_s.append(s)
        self.smoke = alive_s

        # floating combat text
        alive_ft = []
        for f in self.float_texts:
            f["t"] -= 1
            f["y"] -= 0.5
            if f["t"] > 0:
                alive_ft.append(f)
        self.float_texts = alive_ft

        # explosion visuals timer
        alive_x = []
        for ex in self.explosions:
            ex["t"] -= 1
            if ex["t"] > 0:
                alive_x.append(ex)
        self.explosions = alive_x

        for key in self.fx:
            self.fx[key] = [f for f in self.fx[key] if (f.update({"t": f["t"] - 1}) or f["t"] > 0)]

        # enemies
        alive_e = []
        for en in self.enemies:
            tx, ty = self.px, self.py
            if self.decoys:
                d0 = min(self.decoys, key=lambda q: (q["x"]-en["x"])**2 + (q["y"]-en["y"])**2)
                if random.random() < 0.65:
                    tx, ty = d0["x"], d0["y"]

            dx, dy = tx - en["x"], ty - en["y"]
            d = math.hypot(dx, dy) + 1e-6
            mul = 0.25 if self.freeze_t > 0 else 1.0

            if en.get("variant") == "charger" and d < 170:
                mul *= 1.35
            if en.get("variant") == "tank":
                mul *= 0.82

            en["x"] += (dx / d) * en["sp"] * mul
            en["y"] += (dy / d) * en["sp"] * mul

            # shooter variant: chips player at range
            if en.get("variant") == "shooter":
                en["shoot_cd"] = max(0, en.get("shoot_cd", 0) - 1)
                if d < 260 and en["shoot_cd"] == 0:
                    self.hp -= 0.9
                    en["shoot_cd"] = random.randint(65, 105)
                    self.float_texts.append({"x": self.px, "y": self.py-18, "t": 26, "txt": "-1", "c": "#ff8f8f"})

            # boss skills
            if en.get("boss"):
                en["skill_cd"] = max(0, en.get("skill_cd", 0) - 1)
                if en["skill_cd"] == 0:
                    bt = en.get("boss_type")
                    if bt == "brute":
                        if d < 200:
                            self.hp -= 8
                            self.shake_t = max(self.shake_t, 10)
                            self.shake_mag = max(self.shake_mag, 10)
                    elif bt == "summoner":
                        for _ in range(3):
                            sx = en["x"] + random.randint(-80, 80)
                            sy = en["y"] + random.randint(-80, 80)
                            self.enemies.append({"x": sx, "y": sy, "hp": 28 + self.wave*2, "max": 28 + self.wave*2, "sp": 1.8, "s": 18, "shape": "diamond", "c": "#d45cff", "variant": "normal", "shoot_cd": 80, "boss": False, "boss_type": None, "skill_cd": 90})
                    elif bt == "artillery":
                        self.meteors.append({"x": self.px, "y": self.py, "t": 28, "max_t": 28, "dmg": 26 + self.wave*2, "r": 60})
                    elif bt == "vampire":
                        en["hp"] = min(en["max"], en["hp"] + 45)
                    elif bt == "storm":
                        for _ in range(3):
                            if self.enemies:
                                z = random.choice(self.enemies)
                                z["hp"] += 0  # visual chain lightning through existing system style
                        self.hp -= 4
                    en["skill_cd"] = random.randint(90, 150)

            if d <= en["s"] / 2 + PLAYER_SIZE / 2:
                self.hp -= 0.45

            for t in self.turrets:
                if math.hypot(en["x"]-t["x"], en["y"]-t["y"]) <= en["s"]/2 + 10:
                    t["hp"] -= 0.55

            if en["hp"] <= 0:
                self.kills += 1
                base_coin = 14 if en.get("boss") else 8
                if self.stat_bounty > 0 and (en.get("boss") or en.get("variant") in ["tank", "shooter"]):
                    base_coin += 3 + self.stat_bounty
                self.coins += base_coin
                self.float_texts.append({"x": en["x"], "y": en["y"]-10, "t": 34, "txt": "+" + str(base_coin), "c": "#ffe066"})
                if en.get("boss"):
                    self.boss_active = False
                    self.shake_t = max(self.shake_t, 14)
                    self.shake_mag = max(self.shake_mag, 11)
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

        # auto-cast owned cast powers when ready (no click needed)
        for pid in ["meteor_drop", "blood_nova", "chain_lightning", "time_freeze", "clone_swarm", "black_hole_core", "frost_mine", "decoy_hologram", "thunder_totem"]:
            lv = self.power_lv.get(pid, 0)
            if lv > 0 and self.cooldowns.get(pid, 0) <= 0:
                self.cast_power(pid, lv)
                self.cooldowns[pid] = self.get_cooldown_max(pid, lv)

        # timers/stats
        self.shoot_cd = max(0, self.shoot_cd - 1)
        self.dash_cd = max(0, self.dash_cd - 1)
        self.freeze_t = max(0, self.freeze_t - 1)
        for pid in self.cooldowns:
            self.cooldowns[pid] = max(0, self.cooldowns[pid] - 1)
        self.shake_t = max(0, self.shake_t - 1)
        if self.shake_t == 0:
            self.shake_mag = 0

        self.hp = min(self.max_hp, self.hp + self.stat_regen / 60)
        self.wave = 1 + self.kills // 15

        # power choice popup is Hardcore-only
        if self.mode == "Hardcore" and self.coins >= self.next_choice_coin and not self.power_choice_open:
            self.power_choice_open = True
            self.power_choices = self.roll_power_choices(3)
            self.banner = "Pick 1 of 3 powers"

        if self.hp <= 0:
            if self.phoenix_charge > 0:
                self.phoenix_charge = 0
                self.hp = self.max_hp * 0.55
                self.shake_t = max(self.shake_t, 14)
                self.shake_mag = max(self.shake_mag, 10)
                self.float_texts.append({"x": self.px, "y": self.py-20, "t": 60, "txt": "PHOENIX!", "c": "#ffb347"})
            else:
                self.hp = 0
                self.running = False
                self.game_over = True

    # ---------- draw ----------
    def draw_enemy(self, en):
        tx = getattr(self, "_tx", lambda v: v)
        ty = getattr(self, "_ty", lambda v: v)
        ts = getattr(self, "_ts", lambda v: v)
        x, y, s = tx(en["x"]), ty(en["y"]), ts(en["s"])
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

        row_h = 34
        y0 = 110
        visible = (HEIGHT - y0 - 50) // row_h
        panel_list = self.panel_powers()

        # info
        c.create_text(WORLD_W + 10, 44, anchor="nw", fill="#d7d7ff", font=("Consolas", 10),
                      text="Mouse wheel to scroll\nClick to buy/use power")

        for i in range(visible):
            idx = int(self.panel_scroll) + i
            if idx >= len(panel_list):
                break
            p = panel_list[idx]
            y = y0 + i * row_h

            owned = p["id"] in self.owned
            active = p["id"] in self.active_toggles
            lv = self.power_lv.get(p["id"], 0)
            cost = self.power_cost(p)

            bg = "#20203a" if owned else "#171729"
            if active:
                bg = "#263f2a"

            rarity = p.get("rarity", "common")
            rarity_color = {
                "common": "#7f8a9a",
                "rare": "#4aa7ff",
                "epic": "#b56bff",
                "legendary": "#ffb347",
            }.get(rarity, "#7f8a9a")

            c.create_rectangle(WORLD_W + 10, y, WIDTH - 10, y + row_h - 2, fill=bg, outline="#3d3d60")
            c.create_rectangle(WORLD_W + 10, y, WORLD_W + 14, y + row_h - 2, fill=rarity_color, outline="")

            status = f"Lv{lv} | {cost}c"
            if p["kind"] == "toggle" and active:
                status = f"ON Lv{lv} | {cost}c"

            c.create_text(WORLD_W + 16, y + 14, anchor="w", fill="#f0f0ff", font=("Consolas", 10, "bold"), text=p["name"])
            c.create_text(WIDTH - 18, y + 14, anchor="e", fill="#b8ffd0" if active else "#f8d9a8", font=("Consolas", 9, "bold"), text=status)

        # scroll controls + tiny scrollbar
        c.create_rectangle(WORLD_W + 10, y0 - 34, WIDTH - 10, y0 - 6, fill="#1a1a2f", outline="#3d3d60")
        c.create_text(WORLD_W + 130, y0 - 20, text="▲ Scroll Up", fill="#d6dbff", font=("Consolas", 10, "bold"))
        c.create_rectangle(WORLD_W + 10, HEIGHT - 34, WIDTH - 10, HEIGHT - 6, fill="#1a1a2f", outline="#3d3d60")
        c.create_text(WORLD_W + 130, HEIGHT - 20, text="▼ Scroll Down", fill="#d6dbff", font=("Consolas", 10, "bold"))

        if len(panel_list) > visible:
            track_y1, track_y2 = y0, HEIGHT - 40
            c.create_rectangle(WIDTH - 16, track_y1, WIDTH - 12, track_y2, fill="#222", outline="")
            thumb_h = max(20, (visible / len(panel_list)) * (track_y2 - track_y1))
            max_scroll = len(panel_list) - visible
            ratio = 0 if max_scroll <= 0 else self.panel_scroll / max_scroll
            ty = track_y1 + ratio * ((track_y2 - track_y1) - thumb_h)
            c.create_rectangle(WIDTH - 17, ty, WIDTH - 11, ty + thumb_h, fill="#6c7cff", outline="")

        # hovered/selected description not tracked; show tip
        c.create_text(WORLD_W + 10, HEIGHT - 50, anchor="nw", fill="#bfc3ff", font=("Consolas", 9),
                      text="Every power can be leveled.\nRight value shows next upgrade cost.")

    def draw_reload_bars(self):
        c = self.canvas

        tracked = []

        # always show RPG if owned
        if self.power_lv.get("rpg_launcher", 0) > 0:
            max_cd = max(20, 80 - self.power_lv.get("rpg_launcher", 0) * 8)
            tracked.append(("RPG", self.cooldowns["rpg_launcher"], max_cd, "#ff9858"))

        # show cast powers once purchased
        for pid, label, color in [
            ("meteor_drop", "Meteor", "#ff4b4b"),
            ("blood_nova", "Nova", "#d063ff"),
            ("chain_lightning", "Lightning", "#79d8ff"),
            ("time_freeze", "Freeze", "#9fd6ff"),
            ("clone_swarm", "Clones", "#7fffd7"),
            ("auto_turret", "Turret", "#f8d29b"),
            ("black_hole_core", "BlackHole", "#8f6bff"),
            ("frost_mine", "Mine", "#9fd6ff"),
            ("decoy_hologram", "Decoy", "#7bf0ff"),
            ("thunder_totem", "Totem", "#ffd28c"),
            ("flamethrower_arc", "Flame", "#ff944d"),
            ("shockwave_stomp", "Shock", "#ffc87a"),
            ("orbital_laser", "Laser", "#ff6666"),
            ("chain_hook", "Hook", "#d6d6d6"),
            ("shield_drone", "Shield", "#8fe6ff"),
            ("split_shot", "Shotgun", "#ffd27a"),
            ("nuke_mine", "Nuke", "#ff5252"),
        ]:
            if self.power_lv.get(pid, 0) > 0:
                max_cd = self.get_cooldown_max(pid, self.power_lv.get(pid, 1))
                tracked.append((label, self.cooldowns[pid], max_cd, color))

        if not tracked:
            return

        x = 10
        y = HEIGHT - 20
        h = 10
        for name, cd, max_cd, color in tracked:
            w = 95
            ready = max_cd == 0 or cd <= 0
            ratio = 1.0 if ready else max(0.0, min(1.0, 1 - cd / max_cd))

            c.create_rectangle(x, y, x + w, y + h, fill="#2b2b2b", outline="#666")
            c.create_rectangle(x, y, x + w * ratio, y + h, fill=color if not ready else "#67d67a", outline="")
            c.create_text(x + w / 2, y - 6, text=f"{name} {'READY' if ready else ''}".strip(), fill="#d9d9d9", font=("Consolas", 8, "bold"))
            x += w + 8
            if x + w > WORLD_W - 10:
                x = 10
                y -= 22

    def draw(self):
        c = self.canvas
        c.delete("all")

        if self.in_start_menu:
            c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#0e0e16", outline="")
            c.create_text(WORLD_W//2, 120, text="BLOCK SURVIVOR", fill="#efe8ff", font=("Consolas", 38, "bold"))
            c.create_text(WORLD_W//2, 170, text="Choose a mode", fill="#cbd3ff", font=("Consolas", 14, "bold"))
            for name, (x1, y1, x2, y2) in self.mode_buttons.items():
                color = "#2a3f2a" if name == "Classic" else "#4a2525"
                c.create_rectangle(x1, y1, x2, y2, fill=color, outline="#d6dcff", width=2)
                c.create_text((x1+x2)/2, (y1+y2)/2, text=name, fill="#f3f6ff", font=("Consolas", 14, "bold"))
            c.create_text(WORLD_W//2, HEIGHT-80, text="Classic = normal | Hardcore = faster spawns + lower HP", fill="#aeb8e6", font=("Consolas", 10))
            return

        # world bg/grid
        c.create_rectangle(0, 0, WORLD_W, HEIGHT, fill="#101010", outline="")

        cam_zoom = 1.0
        # zoom-out now works in both modes (Hardcore zooms more aggressively)
        if self.mode == "Hardcore":
            cam_zoom = max(0.55, 1.0 - max(0, self.wave - 1) * 0.012)
        elif self.mode == "Classic":
            cam_zoom = max(0.72, 1.0 - max(0, self.wave - 1) * 0.007)

        cx, cy = self.px, self.py
        def tx(x): return cx + (x - cx) * cam_zoom
        def ty(y): return cy + (y - cy) * cam_zoom
        def ts(v): return max(1.0, v * cam_zoom)
        self._tx, self._ty, self._ts = tx, ty, ts
        for x in range(0, WORLD_W, 40):
            c.create_line(x, 0, x, HEIGHT, fill="#181818")
        for y in range(0, HEIGHT, 40):
            c.create_line(0, y, WORLD_W, y, fill="#181818")

        # world entities
        for d in self.drops:
            x, y = tx(d["x"]), ty(d["y"])
            r = ts(5)
            c.create_oval(x-r, y-r, x+r, y+r, fill="#ffe066", outline="")

        for b in self.bullets:
            x, y = tx(b["x"]), ty(b["y"])
            r = ts(b["r"])
            c.create_oval(x-r, y-r, x+r, y+r, fill="#ffd84d", outline="")

        for s in self.smoke:
            p = s["t"] / s["max"]
            rr = s["r"] * (1.2 - p * 0.3)
            shade = int(70 + 90 * p)
            color = f"#{shade:02x}{shade:02x}{shade:02x}"
            c.create_oval(s["x"]-rr, s["y"]-rr, s["x"]+rr, s["y"]+rr, fill=color, outline="")

        for rb in self.rockets:
            x, y = tx(rb["x"]), ty(rb["y"])
            c.create_oval(x-ts(6), y-ts(6), x+ts(6), y+ts(6), fill="#ff8855", outline="#ffd9c7")
            c.create_oval(x-ts(2), y-ts(2), x+ts(2), y+ts(2), fill="#ffe6b3", outline="")

        for tb in self.turret_bullets:
            x, y = tx(tb["x"]), ty(tb["y"])
            c.create_oval(x-ts(3), y-ts(3), x+ts(3), y+ts(3), fill="#9cf5ff", outline="")

        for t in self.turrets:
            s = ts(16)
            x, y = tx(t["x"]), ty(t["y"])
            c.create_rectangle(x-s/2, y-s/2, x+s/2, y+s/2, fill="#ffdca8", outline="#fff3dd", width=2)
            ratio = max(0, t["hp"]) / max(1, t["max"])
            c.create_rectangle(x-ts(14), y-ts(14), x+ts(14), y-ts(10), fill="#2b2b2b", outline="")
            c.create_rectangle(x-ts(14), y-ts(14), x-ts(14)+ts(28)*ratio, y-ts(10), fill="#67d67a", outline="")

        for cl in self.clones:
            x, y = tx(cl["x"]), ty(cl["y"])
            r = ts(7)
            c.create_rectangle(x-r, y-r, x+r, y+r, fill="#7cefff", outline="#d8fbff")

        for d in self.decoys:
            c.create_rectangle(d["x"]-9, d["y"]-9, d["x"]+9, d["y"]+9, fill="#7bf0ff", outline="#d8ffff", dash=(2,2))

        for bh in self.black_holes:
            c.create_oval(bh["x"]-bh["r"], bh["y"]-bh["r"], bh["x"]+bh["r"], bh["y"]+bh["r"], outline="#8a6bff", width=1)
            c.create_oval(bh["x"]-10, bh["y"]-10, bh["x"]+10, bh["y"]+10, fill="#2c1655", outline="#bda6ff")

        for m0 in self.frost_mines:
            c.create_oval(m0["x"]-8, m0["y"]-8, m0["x"]+8, m0["y"]+8, fill="#9fd6ff", outline="#e7f4ff")

        for tt in self.totems:
            c.create_rectangle(tt["x"]-8, tt["y"]-14, tt["x"]+8, tt["y"]+14, fill="#c7a36b", outline="#ffe6b8")

        for m in self.meteors:
            mx, my0 = tx(m["x"]), ty(m["y"])
            rr = ts(m["r"] * (m["t"]/m["max_t"]))
            c.create_oval(mx-rr, my0-rr, mx+rr, my0+rr, outline="#ff4b4b", width=2)
            prog = 1 - (m["t"] / m["max_t"])
            my = ty(m["y"] - 120 + prog * 100)
            c.create_line(mx-ts(12), my-ts(18), mx+ts(2), my-ts(2), fill="#ffb36b", width=3)
            c.create_oval(mx-ts(7), my-ts(7), mx+ts(7), my+ts(7), fill="#ff8a45", outline="#ffe2ad")

        for ex in self.explosions:
            p = ex["t"] / ex["max"]
            rr = ex["r"] * (1 - p*0.15)
            c.create_oval(ex["x"]-rr, ex["y"]-rr, ex["x"]+rr, ex["y"]+rr, fill="#ff7a44", outline="#ffe2b8", width=3)
            c.create_oval(ex["x"]-rr*0.6, ex["y"]-rr*0.6, ex["x"]+rr*0.6, ex["y"]+rr*0.6, fill="#ffd27a", outline="")

        for f in self.fx["throw"]:
            c.create_line(f["x1"], f["y1"], f["x2"], f["y2"], fill=f.get("c", "#ffffff"), width=2, dash=(3,2))
        for f in self.fx["laser"]:
            c.create_line(0, f["y"], WORLD_W, f["y"], fill="#ff6666", width=5)
        for f in self.fx["hook"]:
            c.create_line(f["x1"], f["y1"], f["x2"], f["y2"], fill="#d6d6d6", width=3)
        for f in self.fx["zap"]:
            c.create_line(f["x1"], f["y1"], f["x2"], f["y2"], fill="#9fe8ff", width=2)
        for f in self.fx["shock"]:
            p = f["t"] / max(1, f["max"])
            rr = f["r"] * (1 - p*0.5)
            c.create_oval(f["x"]-rr, f["y"]-rr, f["x"]+rr, f["y"]+rr, outline="#ffc87a", width=2)
        for f in self.fx["flame"]:
            px, py = -f["fy"], f["fx"]
            front = 135
            spread = 40
            x1 = f["x"] + f["fx"] * 20 + px * 8
            y1 = f["y"] + f["fy"] * 20 + py * 8
            x2 = f["x"] + f["fx"] * front + px * spread
            y2 = f["y"] + f["fy"] * front + py * spread
            x3 = f["x"] + f["fx"] * front - px * spread
            y3 = f["y"] + f["fy"] * front - py * spread
            x4 = f["x"] + f["fx"] * 20 - px * 8
            y4 = f["y"] + f["fy"] * 20 - py * 8
            c.create_polygon(x1, y1, x2, y2, x3, y3, x4, y4, fill="#ff8a3d", outline="#ffd08a", stipple="gray25")

        for en in self.enemies:
            self.draw_enemy(en)
            ex, ey, es = tx(en["x"]), ty(en["y"]), ts(en["s"])
            rw = max(ts(16), es)
            ratio = max(0, en["hp"]) / max(1, en["max"])
            c.create_rectangle(ex-rw/2, ey-es/2-ts(7), ex+rw/2, ey-es/2-ts(3), fill="#2b2b2b", outline="")
            c.create_rectangle(ex-rw/2, ey-es/2-ts(7), ex-rw/2 + rw*ratio, ey-es/2-ts(3), fill="#67d67a", outline="")
            if en.get("boss"):
                c.create_text(ex, ey-es/2-ts(16), text="BOSS", fill="#ffcc66", font=("Consolas", 9, "bold"))

        # edge indicators for nearby offscreen threats
        for en in self.enemies:
            ex = min(max(en["x"], 6), WORLD_W-6)
            ey = min(max(en["y"], 6), HEIGHT-6)
            if en["x"] != ex or en["y"] != ey:
                c.create_oval(ex-4, ey-4, ex+4, ey+4, fill="#ff6363", outline="")

        # player
        px, py = tx(self.px), ty(self.py)
        h = ts(PLAYER_SIZE / 2)
        c.create_rectangle(px-h, py-h, px+h, py+h, fill="#4aa8ff", outline="#cfe8ff", width=2)
        spear_len = ts(40 if self.dash_t > 0 else 28)
        c.create_line(px, py, px + self.face_x*spear_len, py + self.face_y*spear_len,
                      fill="#fff07a" if self.dash_t > 0 else "#f4f7ff", width=5)

        if "dark_aura" in self.active_toggles:
            lv = self.power_lv.get("dark_aura",1)
            rr = ts(88 + lv*12)
            c.create_oval(px-rr, py-rr, px+rr, py+rr, outline="#7d54ff", width=2)

        if "poison_cloud" in self.active_toggles:
            lv = self.power_lv.get("poison_cloud",1)
            rr = ts(125 + lv*10)
            c.create_oval(px-rr, py-rr, px+rr, py+rr, outline="#5dcf73", width=1)

        if "spike_ring" in self.active_toggles:
            lv = self.power_lv.get("spike_ring",1)
            r1, r2 = ts(105+lv*8), ts(130+lv*10)
            c.create_oval(px-r1, py-r1, px+r1, py+r1, outline="#ffcc88", width=1)
            c.create_oval(px-r2, py-r2, px+r2, py+r2, outline="#ffcc88", width=1)

        if "orbit_blades" in self.active_toggles:
            lv = self.power_lv.get("orbit_blades",1)
            orbit_r = ts(46 + lv*7)
            for i in range(3):
                a = self.orbit_angle + i * (2 * math.pi / 3)
                bx, by = px + math.cos(a) * orbit_r, py + math.sin(a) * orbit_r
                r = ts(6)
                c.create_oval(bx-r, by-r, bx+r, by+r, fill="#c9a3ff", outline="#f0e0ff")

        if "shield_drone" in self.active_toggles:
            lv = self.power_lv.get("shield_drone",1)
            rr = ts(34 + lv * 5)
            c.create_oval(px-rr, py-rr, px+rr, py+rr, outline="#8fe6ff", width=2)

        if self.power_lv.get("damage_core",0) >= 2 and self.enemies:
            t = self.nearest_enemy()
            c.create_line(self.px, self.py, t["x"], t["y"], fill="#ff4d4d", width=2)

        # HUD
        c.create_text(10, 10, anchor="nw", fill="#f0f0f0", font=("Consolas", 13, "bold"),
                      text=f"HP {int(self.hp)}/{self.max_hp}  Coins {self.coins}  Wave {self.wave}  Kills {self.kills}")
        c.create_text(10, 32, anchor="nw", fill="#d2d2d2", font=("Consolas", 10), text=self.banner)

        for f in self.float_texts:
            c.create_text(f["x"], f["y"], text=f["txt"], fill=f["c"], font=("Consolas", 10, "bold"))

        # pause button
        x1, y1, x2, y2 = self.pause_btn
        c.create_rectangle(x1, y1, x2, y2, fill="#1d2f4f" if not self.paused else "#4f2a1d", outline="#a9c6ff", width=2)
        c.create_text((x1+x2)/2, (y1+y2)/2, text="PAUSE (P)" if not self.paused else "RESUME (P)", fill="#e9f2ff", font=("Consolas", 9, "bold"))

        if self.paused and not self.game_over:
            c.create_text(WORLD_W//2, HEIGHT//2-20, text="PAUSED", fill="#d7e8ff", font=("Consolas", 34, "bold"))
            c.create_text(WORLD_W//2, HEIGHT//2+20, text="TEST: 1=+Coins  2=Heal  3=Wave+  4=Clear", fill="#c9d8f0", font=("Consolas", 11, "bold"))

        if self.game_over:
            c.create_text(WORLD_W//2, HEIGHT//2, text="GAME OVER\nPress R", fill="#ffd2a6", font=("Consolas", 30, "bold"), justify="center")

        if self.power_choice_open:
            c.create_rectangle(0, 0, WORLD_W, HEIGHT, fill="#000000", stipple="gray25", outline="")
            c.create_text(WORLD_W//2, 130, text="Choose 1 Power", fill="#fff0c7", font=("Consolas", 22, "bold"))
            cx, cy, cw, ch = WORLD_W//2 - 120, 180, 240, 72
            for i, p in enumerate(self.power_choices):
                y = cy + i * (ch + 16)
                c.create_rectangle(cx, y, cx+cw, y+ch, fill="#22263d", outline="#b9c4ff", width=2)
                c.create_text(cx+12, y+24, anchor="w", text=p["name"], fill="#f4f6ff", font=("Consolas", 12, "bold"))
                c.create_text(cx+12, y+48, anchor="w", text=f"Lv {self.power_lv.get(p['id'],0)} -> {self.power_lv.get(p['id'],0)+1}", fill="#bcd0ff", font=("Consolas", 10))

        self.draw_reload_bars()
        self.draw_panel()

        # screen shake on big explosions
        if self.shake_t > 0 and self.shake_mag > 0:
            sx = random.randint(-self.shake_mag, self.shake_mag)
            sy = random.randint(-self.shake_mag, self.shake_mag)
            c.move("all", sx, sy)

    def tick(self):
        self.update_logic()
        self.draw()
        self.root.after(FPS_MS, self.tick)


def main():
    global WIDTH, HEIGHT, WORLD_W

    root = tk.Tk()
    WIDTH = root.winfo_screenwidth()
    HEIGHT = root.winfo_screenheight()
    WORLD_W = int(WIDTH * 0.76)

    root.attributes("-fullscreen", True)
    root.resizable(True, True)
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
