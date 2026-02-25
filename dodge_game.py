import random
import tkinter as tk

WIDTH, HEIGHT = 900, 560
PLAYER_SIZE = 30
ENEMY_SIZE = 24
PLAYER_SPEED = 8
ENEMY_BASE_SPEED = 3
SPAWN_INTERVAL_MS = 650
FRAME_MS = 16


class GladiumGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Gladium")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#1f1510", highlightthickness=0)
        self.canvas.pack()

        self.score = 0
        self.high_score = 0
        self.combo = 1
        self.wave = 1
        self.running = True
        self.game_over = False

        self.keys = set()
        self.enemies = []

        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 80

        self.draw_arena_background()

        # Gladiator (gold shield)
        self.player = self.canvas.create_rectangle(
            self.player_x,
            self.player_y,
            self.player_x + PLAYER_SIZE,
            self.player_y + PLAYER_SIZE,
            fill="#d4af37",
            outline="#f5deb3",
            width=2,
        )

        self.hud = self.canvas.create_text(
            14,
            12,
            text="Score: 0   High: 0   Combo: x1   Wave: 1",
            fill="#f4ead5",
            font=("Consolas", 14, "bold"),
            anchor="nw",
        )

        self.info_text = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="GLADIUM\nMove with WASD / Arrow Keys\nDodge enemy spears\nPress R to restart",
            fill="#f8d9a0",
            font=("Consolas", 18, "bold"),
            justify="center",
        )

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        self.root.after(1700, self.hide_intro)
        self.root.after(SPAWN_INTERVAL_MS, self.spawn_enemy)
        self.root.after(FRAME_MS, self.update)

    def draw_arena_background(self):
        # Sand floor
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#4b2f1f", outline="")
        self.canvas.create_rectangle(0, HEIGHT - 120, WIDTH, HEIGHT, fill="#8b5a2b", outline="")

        # Arena stripes
        for y in range(50, HEIGHT - 120, 42):
            self.canvas.create_line(0, y, WIDTH, y, fill="#5a3a28", width=2)

        # Pillars
        for x in range(30, WIDTH, 120):
            self.canvas.create_rectangle(x, 25, x + 22, 95, fill="#6c4a36", outline="#7d5940")

    def hide_intro(self):
        self.canvas.itemconfigure(self.info_text, state="hidden")

    def on_key_press(self, event):
        key = event.keysym.lower()
        self.keys.add(key)

        if key == "r" and self.game_over:
            self.restart()

    def on_key_release(self, event):
        key = event.keysym.lower()
        self.keys.discard(key)

    def restart(self):
        for e in self.enemies:
            self.canvas.delete(e["id"])
        self.enemies.clear()

        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 80
        self.canvas.coords(
            self.player,
            self.player_x,
            self.player_y,
            self.player_x + PLAYER_SIZE,
            self.player_y + PLAYER_SIZE,
        )

        self.score = 0
        self.combo = 1
        self.wave = 1
        self.running = True
        self.game_over = False
        self.canvas.itemconfigure(self.info_text, state="hidden")

    def spawn_enemy(self):
        if self.running:
            # Wave scales every 20 points
            self.wave = 1 + (self.score // 20)

            # Spawn count increases by wave
            spawn_count = min(1 + self.wave // 2, 4)

            for _ in range(spawn_count):
                x = random.randint(0, WIDTH - ENEMY_SIZE)
                speed = ENEMY_BASE_SPEED + min(9, self.wave + self.score // 25)

                # Spears are narrow and dangerous
                spear_width = random.choice([12, 14, 16])
                enemy = self.canvas.create_rectangle(
                    x,
                    -ENEMY_SIZE,
                    x + spear_width,
                    0,
                    fill="#c0392b",
                    outline="#f1948a",
                    width=1,
                )
                self.enemies.append({"id": enemy, "speed": speed})

        self.root.after(SPAWN_INTERVAL_MS, self.spawn_enemy)

    def move_player(self):
        if "left" in self.keys or "a" in self.keys:
            self.player_x -= PLAYER_SPEED
        if "right" in self.keys or "d" in self.keys:
            self.player_x += PLAYER_SPEED
        if "up" in self.keys or "w" in self.keys:
            self.player_y -= PLAYER_SPEED
        if "down" in self.keys or "s" in self.keys:
            self.player_y += PLAYER_SPEED

        self.player_x = max(0, min(WIDTH - PLAYER_SIZE, self.player_x))
        self.player_y = max(0, min(HEIGHT - PLAYER_SIZE, self.player_y))

        self.canvas.coords(
            self.player,
            self.player_x,
            self.player_y,
            self.player_x + PLAYER_SIZE,
            self.player_y + PLAYER_SIZE,
        )

    def update_enemies(self):
        player_coords = self.canvas.coords(self.player)

        remaining = []
        dodged_this_frame = 0

        for enemy in self.enemies:
            eid = enemy["id"]
            speed = enemy["speed"]

            self.canvas.move(eid, 0, speed)
            ex1, ey1, ex2, ey2 = self.canvas.coords(eid)

            # Collision check
            px1, py1, px2, py2 = player_coords
            if not (px2 < ex1 or px1 > ex2 or py2 < ey1 or py1 > ey2):
                self.end_game()
                return

            if ey1 > HEIGHT:
                self.canvas.delete(eid)
                dodged_this_frame += 1
            else:
                remaining.append(enemy)

        if dodged_this_frame:
            self.score += dodged_this_frame * self.combo
            self.combo = min(8, self.combo + 1)
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            # Soft combo decay
            if random.random() < 0.08:
                self.combo = max(1, self.combo - 1)

        self.enemies = remaining

    def end_game(self):
        self.running = False
        self.game_over = True
        self.canvas.itemconfigure(
            self.info_text,
            text=(
                "GLADIUM - Defeat\n"
                f"Score: {self.score}   High: {self.high_score}\n"
                f"Reached Wave: {self.wave}\n"
                "Press R to fight again"
            ),
            fill="#ffd9a0",
            state="normal",
        )

    def update_hud(self):
        self.canvas.itemconfigure(
            self.hud,
            text=f"Score: {self.score}   High: {self.high_score}   Combo: x{self.combo}   Wave: {self.wave}",
        )

    def update(self):
        if self.running:
            self.move_player()
            self.update_enemies()
            self.update_hud()

        self.root.after(FRAME_MS, self.update)


def main():
    root = tk.Tk()
    _game = GladiumGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
