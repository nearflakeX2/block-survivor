import random
import tkinter as tk

WIDTH, HEIGHT = 800, 500
PLAYER_SIZE = 28
ENEMY_SIZE = 24
PLAYER_SPEED = 8
ENEMY_BASE_SPEED = 3
SPAWN_INTERVAL_MS = 700
FRAME_MS = 16


class DodgeGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Neon Dodge")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111")
        self.canvas.pack()

        self.score = 0
        self.high_score = 0
        self.running = True
        self.game_over = False

        self.keys = set()
        self.enemies = []

        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 60

        self.player = self.canvas.create_rectangle(
            self.player_x,
            self.player_y,
            self.player_x + PLAYER_SIZE,
            self.player_y + PLAYER_SIZE,
            fill="#39ff14",
            outline="",
        )

        self.score_text = self.canvas.create_text(
            12,
            12,
            text="Score: 0   High: 0",
            fill="#f5f5f5",
            font=("Consolas", 14, "bold"),
            anchor="nw",
        )

        self.info_text = self.canvas.create_text(
            WIDTH // 2,
            HEIGHT // 2,
            text="Move with WASD / Arrow Keys\nAvoid red blocks\nPress R to restart",
            fill="#cccccc",
            font=("Consolas", 16, "bold"),
            justify="center",
        )

        root.bind("<KeyPress>", self.on_key_press)
        root.bind("<KeyRelease>", self.on_key_release)

        self.root.after(1400, self.hide_intro)
        self.root.after(SPAWN_INTERVAL_MS, self.spawn_enemy)
        self.root.after(FRAME_MS, self.update)

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
        self.player_y = HEIGHT - 60
        self.canvas.coords(
            self.player,
            self.player_x,
            self.player_y,
            self.player_x + PLAYER_SIZE,
            self.player_y + PLAYER_SIZE,
        )

        self.score = 0
        self.running = True
        self.game_over = False
        self.canvas.itemconfigure(self.info_text, state="hidden")

    def spawn_enemy(self):
        if self.running:
            x = random.randint(0, WIDTH - ENEMY_SIZE)
            speed = ENEMY_BASE_SPEED + min(7, self.score // 12)
            enemy = self.canvas.create_rectangle(
                x,
                -ENEMY_SIZE,
                x + ENEMY_SIZE,
                0,
                fill="#ff3b3b",
                outline="",
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
        for enemy in self.enemies:
            eid = enemy["id"]
            speed = enemy["speed"]

            self.canvas.move(eid, 0, speed)
            ex1, ey1, ex2, ey2 = self.canvas.coords(eid)

            # collision
            px1, py1, px2, py2 = player_coords
            if not (px2 < ex1 or px1 > ex2 or py2 < ey1 or py1 > ey2):
                self.end_game()
                return

            if ey1 > HEIGHT:
                self.canvas.delete(eid)
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                remaining.append(enemy)

        self.enemies = remaining

    def end_game(self):
        self.running = False
        self.game_over = True
        self.canvas.itemconfigure(
            self.info_text,
            text=f"Game Over!\nScore: {self.score}   High: {self.high_score}\nPress R to restart",
            fill="#ffe08a",
            state="normal",
        )

    def update_hud(self):
        self.canvas.itemconfigure(
            self.score_text,
            text=f"Score: {self.score}   High: {self.high_score}",
        )

    def update(self):
        if self.running:
            self.move_player()
            self.update_enemies()
            self.update_hud()

        self.root.after(FRAME_MS, self.update)


def main():
    root = tk.Tk()
    game = DodgeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
