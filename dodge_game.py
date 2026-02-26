import math
import random
import tkinter as tk

WIDTH, HEIGHT = 960, 640
FPS = 16

PLAYER_SIZE = 28
BASE_HP = 100
BASE_SPEED = 4.2
BASE_BULLET_DMG = 24
BASE_BULLET_SPEED = 9.0
BASE_FIRE_CD = 10

ENEMY_BASE_HP = 28
ENEMY_BASE_SPEED = 1.5
SPAWN_MS = 850

POWERUP_SIZE = 16

# 52 unique relics (bought in shop, instantly active, permanent)
RELICS = [
    "Ash Fang","Void Prism","Storm Nail","Sun Shard","Moon Spine","Iron Vein","Blood Lens","Star Core",
    "Grim Feather","Echo Coil","Dusk Crown","Frost Tooth","Blaze Root","Shock Bloom","Dust Rune","Night Horn",
    "Rift Bone","Gold Thorn","Warp Eye","Gale Ring","Thorn Heart","Stone Pulse","Nova Seed","Pyre Chain",
    "Mist Anchor","Viper Sigil","Razor Shell","Hush Bell","Bramble Mark","Flare Idol","Obsidian Key","Sky Hook",
    "Inferno Knot","Glacier Knot","Volt Knot","Plague Knot","Spirit Knot","Raven Knot","Phantom Knot","Titan Knot",
    "Aether Knot","Pulse Knot","Gloom Knot","Aurora Knot","Sable Knot","Oracle Knot","Warden Knot","Lancer Knot",
    "Reaper Knot","Mirage Knot","Tempest Knot","Ember Knot"
]


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Block Survivor")
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#101010", highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        root.bind("<KeyPress>", self.key_down)
        root.bind("<KeyRelease>", self.key_up)

        self.reset_all()
        self.root.after(self.spawn_ms, self.spawn_enemy)
        self.tick()

    def reset_all(self):
        self.running = True
        self.shop_open = False
        self.game_over = False

        self.px, self.py = WIDTH // 2, HEIGHT // 2
        self.face_x, self.face_y = 1, 0

        self.wave, self.kills, self.score, self.coins = 1, 0, 0, 0
        self.drop_pity = 0

        self.max_hp = BASE_HP
        self.hp = float(self.max_hp)
        self.speed_mul = 1.0
        self.bullet_dmg_add = 0
        self.bullet_speed_add = 0
        self.fire_cd_mul = 1.0
        self.regen = 0.0
        self.magnet = 0.0

        # buyable powers, instantly active when bought
        self.dark_active = False
        self.orbit_active = False
        self.nova_level = 0
        self.turret_level = 0
        self.freeze_level = 0

        self.nova_cd = 0
        self.freeze_cd = 0
        self.freeze_timer = 0

        self.dash_cd = 0
        self.dash_t = 0
        self.dash_vx = 0
        self.dash_vy = 0

        self.orbit_a = 0.0
        self.turrets = []

        self.powerups = []
        self.enemies = []
        self.bullets = []

        self.relic_owned = set()

        self.banner = "WASD move | SPACE dash+spear | P shop | R restart"
        self.spawn_ms = SPAWN_MS
        self.shoot_cd = 0
        self.frame = 0

    def key_down(self, e):
        k = e.keysym.lower()
        self.keys.add(k)

        if k == "r" and self.game_over:
            self.reset_all()
            return

        if k == "p" and self.running:
            self.shop_open = not self.shop_open
            return

        if self.shop_open:
            if k == "1": self.buy_dark()
            elif k == "2": self.buy_orbit()
            elif k == "3": self.buy_nova()
            elif k == "4": self.buy_turret()
            elif k == "5": self.buy_freeze()
            elif k == "6": self.buy_relic()
            return

        if k == "space" and self.running:
            self.start_dash()

    def key_up(self, e):
        self.keys.discard(e.keysym.lower())

    # ---------- shop ----------
    def spend(self, cost):
        if self.coins < cost:
            self.banner = f"Need {cost} coins"
            return False
        self.coins -= cost
        return True

    def buy_dark(self):
        if self.dark_active: self.banner = "Dark Aura already active"; return
        if self.spend(100): self.dark_active = True; self.banner = "Dark Aura activated"

    def buy_orbit(self):
        if self.orbit_active: self.banner = "Orbit already active"; return
        if self.spend(180): self.orbit_active = True; self.banner = "Orbit Blades activated"

    def buy_nova(self):
        c = 140 + self.nova_level * 120
        if self.spend(c): self.nova_level += 1; self.banner = f"Blood Nova Lv{self.nova_level}"

    def buy_turret(self):
        c = 180 + self.turret_level * 140
        if self.spend(c):
            self.turret_level += 1
            self.turrets.append({"x": self.px, "y": self.py, "ttl": 420 + 80*self.turret_level, "cd": 0})
            self.banner = f"Turret Lv{self.turret_level} (deployed)"

    def buy_freeze(self):
        c = 160 + self.freeze_level * 130
        if self.spend(c): self.freeze_level += 1; self.banner = f"Time Freeze Lv{self.freeze_level}"

    def buy_relic(self):
        if len(self.relic_owned) >= len(RELICS):
            self.banner = "All relics owned"
            return
        cost = 90 + 8 * len(self.relic_owned)
        if not self.spend(cost):
            return
        choice = random.choice([r for r in RELICS if r not in self.relic_owned])
        self.relic_owned.add(choice)
        self.apply_relic(choice)
        self.banner = f"Relic acquired: {choice}"

    def apply_relic(self, name):
        i = RELICS.index(name)
        mod = i % 13
        tier = 1 + i // 13
        # all effects are unique by (mod,tier,name)
        if mod == 0: self.bullet_dmg_add += 2 * tier
        elif mod == 1: self.speed_mul += 0.03 * tier
        elif mod == 2: self.regen += 0.15 * tier
        elif mod == 3: self.max_hp += 6 * tier; self.hp += 6 * tier
        elif mod == 4: self.fire_cd_mul *= max(0.95, 1 - 0.02 * tier)
        elif mod == 5: self.bullet_speed_add += 0.5 * tier
        elif mod == 6: self.magnet += 14 * tier
        elif mod == 7: self.nova_level += 1
        elif mod == 8: self.freeze_level += 1
        elif mod == 9: self.turret_level += 1
        elif mod == 10: self.dark_active = True
        elif mod == 11: self.orbit_active = True
        elif mod == 12: self.hp = min(self.max_hp, self.hp + 20 + 8*tier)

    # ---------- gameplay ----------
    def start_dash(self):
        if self.dash_cd > 0 or self.dash_t > 0:
            return
        dx = (-1 if "a" in self.keys or "left" in self.keys else 0) + (1 if "d" in self.keys or "right" in self.keys else 0)
        dy = (-1 if "w" in self.keys or "up" in self.keys else 0) + (1 if "s" in self.keys or "down" in self.keys else 0)
        if dx == 0 and dy == 0:
            t = self.nearest_enemy()
            if t:
                dx, dy = t["x"]-self.px, t["y"]-self.py
            else:
                dx, dy = self.face_x, self.face_y
        d = math.hypot(dx, dy) + 1e-6
        self.face_x, self.face_y = dx/d, dy/d
        self.dash_vx, self.dash_vy = self.face_x * 13, self.face_y * 13
        self.dash_t, self.dash_cd = 8, 42

    def spawn_enemy(self):
        if self.running and not self.shop_open:
            side = random.choice([0,1,2,3])
            if side==0: x,y = random.randint(30,WIDTH-30), -20
            elif side==1: x,y = random.randint(30,WIDTH-30), HEIGHT+20
            elif side==2: x,y = -20, random.randint(30,HEIGHT-30)
            else: x,y = WIDTH+20, random.randint(30,HEIGHT-30)

            hp = ENEMY_BASE_HP + self.wave*6
            sp = ENEMY_BASE_SPEED + min(2.8, self.wave*0.1) + random.random()*0.5
            shape = ["square","diamond","triangle","hex"][min(3,self.wave//4)]
            color = ["#d94f4f","#b04fda","#f08a24","#7a2be2"][min(3,self.wave//4)]
            self.enemies.append({"x":x,"y":y,"hp":hp,"max":hp,"sp":sp,"s":22+random.randint(-4,5),"shape":shape,"c":color})
            self.spawn_ms = max(180, SPAWN_MS - self.wave*28)
        self.root.after(self.spawn_ms, self.spawn_enemy)

    def nearest_enemy(self):
        return min(self.enemies, key=lambda e:(e["x"]-self.px)**2+(e["y"]-self.py)**2) if self.enemies else None

    def fire(self):
        if self.shoot_cd > 0 or not self.enemies:
            return
        t = self.nearest_enemy()
        a = math.atan2(t["y"]-self.py, t["x"]-self.px)
        sp = BASE_BULLET_SPEED + self.bullet_speed_add
        self.bullets.append({"x":self.px,"y":self.py,"vx":math.cos(a)*sp,"vy":math.sin(a)*sp,"r":4})
        cd = int(BASE_FIRE_CD * self.fire_cd_mul)
        self.shoot_cd = max(3, cd)

    def drop_powerup(self, x, y):
        self.drop_pity += 1
        if random.random() > 0.35 and self.drop_pity < 4:
            return
        self.drop_pity = 0
        kinds = ["heal","rapid","speed","shield","multi","damage","maxhp","regen","bspeed","magnet"]
        k = random.choice(kinds)
        cols = {"heal":"#4de284","rapid":"#ffe066","speed":"#66d9ff","shield":"#b388ff","multi":"#ff9ecf",
                "damage":"#ff784f","maxhp":"#7dffb2","regen":"#9cf2ff","bspeed":"#ffd166","magnet":"#a6ff6b"}
        self.powerups.append({"x":x,"y":y,"k":k,"ttl":560,"c":cols[k]})

    def apply_drop(self, k):
        if k == "heal": self.hp = min(self.max_hp, self.hp + 24)
        elif k == "rapid": self.fire_cd_mul *= 0.92
        elif k == "speed": self.speed_mul += 0.08
        elif k == "shield": self.hp = min(self.max_hp, self.hp + 10)
        elif k == "multi": self.bullet_dmg_add += 4
        elif k == "damage": self.bullet_dmg_add += 6
        elif k == "maxhp": self.max_hp += 14; self.hp += 14
        elif k == "regen": self.regen += 0.4
        elif k == "bspeed": self.bullet_speed_add += 1.4
        elif k == "magnet": self.magnet += 25

    def update_logic(self):
        self.frame += 1
        if not self.running or self.shop_open:
            return

        # move
        if self.dash_t > 0:
            self.px += self.dash_vx; self.py += self.dash_vy; self.dash_t -= 1
            for e in self.enemies:
                if math.hypot(e["x"]-self.px, e["y"]-self.py) < e["s"]/2 + 18:
                    e["hp"] -= 56
        else:
            sp = BASE_SPEED * self.speed_mul
            dx = (-sp if "a" in self.keys or "left" in self.keys else 0) + (sp if "d" in self.keys or "right" in self.keys else 0)
            dy = (-sp if "w" in self.keys or "up" in self.keys else 0) + (sp if "s" in self.keys or "down" in self.keys else 0)
            if dx and dy: dx*=0.7071; dy*=0.7071
            if dx or dy:
                d = math.hypot(dx,dy); self.face_x,self.face_y = dx/d, dy/d
            self.px += dx; self.py += dy

        h = PLAYER_SIZE/2
        self.px = max(h, min(WIDTH-h, self.px))
        self.py = max(h, min(HEIGHT-h, self.py))

        # auto skills (instant-active buys)
        if self.dark_active:
            for e in self.enemies:
                if math.hypot(e["x"]-self.px,e["y"]-self.py) < 90 + e["s"]/2:
                    e["hp"] -= 1.7

        if self.orbit_active:
            self.orbit_a += 0.22
            for i in range(3):
                a = self.orbit_a + i*2.094
                bx, by = self.px + math.cos(a)*46, self.py + math.sin(a)*46
                for e in self.enemies:
                    if math.hypot(e["x"]-bx,e["y"]-by) < e["s"]/2 + 12:
                        e["hp"] -= 6

        # auto nova/freeze if bought
        if self.nova_level > 0 and self.nova_cd == 0:
            r = 140 + self.nova_level*12
            d = 40 + self.nova_level*18
            for e in self.enemies:
                if math.hypot(e["x"]-self.px,e["y"]-self.py) < r:
                    e["hp"] -= d
            self.nova_cd = max(120, 320 - self.nova_level*20)

        if self.freeze_level > 0 and self.freeze_cd == 0:
            self.freeze_timer = 70 + self.freeze_level*20
            self.freeze_cd = max(180, 420 - self.freeze_level*25)

        # turret logic
        alive_t = []
        for t in self.turrets:
            t["ttl"] -= 1; t["cd"] = max(0, t["cd"]-1)
            if t["ttl"] <= 0: continue
            if self.enemies and t["cd"]==0:
                target = min(self.enemies, key=lambda e:(e["x"]-t["x"])**2+(e["y"]-t["y"])**2)
                if math.hypot(target["x"]-t["x"], target["y"]-t["y"]) < 280:
                    target["hp"] -= 26 + self.turret_level*6
                    t["cd"] = 14
            alive_t.append(t)
        self.turrets = alive_t

        # shooting
        self.fire()

        # bullets
        live_b = []
        for b in self.bullets:
            b["x"] += b["vx"]; b["y"] += b["vy"]
            if b["x"] < -10 or b["x"] > WIDTH+10 or b["y"] < -10 or b["y"] > HEIGHT+10:
                continue
            hit = False
            for e in self.enemies:
                if math.hypot(e["x"]-b["x"], e["y"]-b["y"]) < e["s"]/2 + b["r"]:
                    e["hp"] -= BASE_BULLET_DMG + self.bullet_dmg_add
                    hit = True
                    break
            if not hit: live_b.append(b)
        self.bullets = live_b

        # enemies move + hurt
        live_e = []
        for e in self.enemies:
            dx,dy = self.px-e["x"], self.py-e["y"]
            d = math.hypot(dx,dy)+1e-6
            mul = 0.22 if self.freeze_timer>0 else 1.0
            e["x"] += (dx/d)*e["sp"]*mul
            e["y"] += (dy/d)*e["sp"]*mul
            if d < e["s"]/2 + PLAYER_SIZE/2:
                self.hp -= 0.45 * (0.55 if self.freeze_timer>0 else 1.0)
            if e["hp"] <= 0:
                self.kills += 1; self.score += 10; self.coins += 7
                self.drop_powerup(e["x"], e["y"])
            else:
                live_e.append(e)
        self.enemies = live_e

        # collect drops
        keep = []
        for p in self.powerups:
            p["ttl"] -= 1
            if p["ttl"] <= 0: continue
            if self.magnet > 0:
                dx,dy = self.px-p["x"], self.py-p["y"]
                d = math.hypot(dx,dy)+1e-6
                if d < 220 + self.magnet:
                    p["x"] += (dx/d)*(0.8 + self.magnet*0.02)
                    p["y"] += (dy/d)*(0.8 + self.magnet*0.02)
            if math.hypot(p["x"]-self.px,p["y"]-self.py) < PLAYER_SIZE/2 + POWERUP_SIZE/2:
                self.apply_drop(p["k"])
            else:
                keep.append(p)
        self.powerups = keep

        # timers
        self.hp = min(self.max_hp, self.hp + self.regen/60)
        self.wave = 1 + self.kills // 15
        if self.hp <= 0:
            self.hp = 0; self.running = False; self.game_over = True
        self.shoot_cd = max(0, self.shoot_cd-1)
        self.nova_cd = max(0, self.nova_cd-1)
        self.freeze_cd = max(0, self.freeze_cd-1)
        self.dash_cd = max(0, self.dash_cd-1)
        self.freeze_timer = max(0, self.freeze_timer-1)

    def draw_enemy(self, e):
        x,y,s = e["x"], e["y"], e["s"]
        x1,y1,x2,y2 = x-s/2,y-s/2,x+s/2,y+s/2
        if e["shape"]=="square":
            self.canvas.create_rectangle(x1,y1,x2,y2,fill=e["c"],outline="#ffb3b3",width=2)
        elif e["shape"]=="diamond":
            self.canvas.create_polygon(x,y1,x2,y,x,y2,x1,y,fill=e["c"],outline="#ffd8ff",width=2)
        elif e["shape"]=="triangle":
            self.canvas.create_polygon(x,y1,x2,y2,x1,y2,fill=e["c"],outline="#ffe0c2",width=2)
        else:
            h=s*0.5
            self.canvas.create_polygon(x-h*.9,y-h,x+h*.9,y-h,x+h*1.4,y,x+h*.9,y+h,x-h*.9,y+h,x-h*1.4,y,fill=e["c"],outline="#e9ccff",width=2)

    def draw(self):
        c = self.canvas
        c.delete("all")
        for x in range(0, WIDTH, 40): c.create_line(x,0,x,HEIGHT,fill="#181818")
        for y in range(0, HEIGHT, 40): c.create_line(0,y,WIDTH,y,fill="#181818")

        # drops
        labels = {"heal":"H","rapid":"R","speed":"S","shield":"D","multi":"T","damage":"+DMG","maxhp":"+HP","regen":"+RG","bspeed":"+BS","magnet":"+MG"}
        for p in self.powerups:
            s=POWERUP_SIZE
            c.create_oval(p["x"]-s/2,p["y"]-s/2,p["x"]+s/2,p["y"]+s/2,fill=p["c"],outline="#fff")
            c.create_text(p["x"],p["y"],text=labels[p["k"]],fill="#111",font=("Consolas",7,"bold"))

        for b in self.bullets:
            r=b["r"]; c.create_oval(b["x"]-r,b["y"]-r,b["x"]+r,b["y"]+r,fill="#ffd84d",outline="")

        for t in self.turrets:
            s=16
            c.create_rectangle(t["x"]-s/2,t["y"]-s/2,t["x"]+s/2,t["y"]+s/2,fill="#ffdca8",outline="#fff3dd",width=2)

        for e in self.enemies: self.draw_enemy(e)

        # player
        h=PLAYER_SIZE/2
        c.create_rectangle(self.px-h,self.py-h,self.px+h,self.py+h,fill="#4aa8ff",outline="#cfe8ff",width=2)
        spear = 42 if self.dash_t>0 else 30
        c.create_line(self.px,self.py,self.px+self.face_x*spear,self.py+self.face_y*spear,fill="#fff07a" if self.dash_t>0 else "#f4f7ff",width=5)

        if self.dark_active:
            rr=88; c.create_oval(self.px-rr,self.py-rr,self.px+rr,self.py+rr,outline="#7d54ff",width=2)
        if self.orbit_active:
            for i in range(3):
                a=self.orbit_a+i*2.094
                bx,by=self.px+math.cos(a)*46,self.py+math.sin(a)*46
                c.create_oval(bx-6,by-6,bx+6,by+6,fill="#c9a3ff",outline="#f0e0ff")

        hud = f"HP {int(self.hp)}/{self.max_hp}  Coins {self.coins}  Wave {self.wave}  Kills {self.kills}  Relics {len(self.relic_owned)}/52"
        c.create_text(10,10,text=hud,anchor="nw",fill="#f0f0f0",font=("Consolas",13,"bold"))
        c.create_text(10,30,text=f"Aura:Dark {'ON' if self.dark_active else 'OFF'} Orbit {'ON' if self.orbit_active else 'OFF'} | NovaLv {self.nova_level} TurretLv {self.turret_level} FreezeLv {self.freeze_level}",anchor="nw",fill="#d0d0d0",font=("Consolas",10))
        c.create_text(WIDTH//2, HEIGHT-12, text=self.banner, fill="#cfcfcf", font=("Consolas", 11), anchor="s")

        if self.shop_open:
            c.create_rectangle(140,100,WIDTH-140,HEIGHT-100,fill="#0f0f15",outline="#9b8cff",width=3)
            txt = (
                "SHOP (P to close)\n\n"
                "[1] Dark Aura (instant always ON) - 100\n"
                "[2] Orbit Blades (instant always ON) - 180\n"
                f"[3] Blood Nova level ({140 + self.nova_level*120})\n"
                f"[4] Auto Turret level ({180 + self.turret_level*140})\n"
                f"[5] Time Freeze level ({160 + self.freeze_level*130})\n"
                f"[6] Buy RANDOM UNIQUE RELIC ({90 + 8*len(self.relic_owned)})\n\n"
                "Relics are 52 unique permanent powerups."
            )
            c.create_text(WIDTH//2, HEIGHT//2, text=txt, fill="#efe8ff", font=("Consolas", 15, "bold"), justify="center")

        if self.game_over:
            c.create_text(WIDTH//2, HEIGHT//2, text="GAME OVER\nPress R", fill="#ffd2a6", font=("Consolas", 28, "bold"), justify="center")

    def tick(self):
        self.update_logic()
        self.draw()
        self.root.after(FPS, self.tick)


def main():
    root = tk.Tk()
    root.resizable(False, False)
    Game(root)
    root.mainloop()

if __name__ == "__main__":
    main()
