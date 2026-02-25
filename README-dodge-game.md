# Block Survivor (Python)

Survivor game in Python + Tkinter:
- You are a blue block with a gun
- Auto-shoots nearest enemy
- Dash + spear attack
- Evolving enemy tiers
- Stackable powerups
- Shop + active powers

## Powerups

Timed stackable drops:
- **Heal** (green): restores HP
- **Rapid Fire** (yellow): shoot faster
- **Speed Boost** (cyan): move faster
- **Shield** (purple): reduced contact damage
- **Triple Shot** (pink): fire 3 bullets

Permanent drops (do not run out):
- **Damage Core**: +bullet damage permanently
- **Max HP Core**: +max HP permanently
- **Regen Core**: passive regen permanently
- **Lifesteal Core**: heal when bullets hit
- **Bullet Speed Core**: faster bullets permanently
- **Magnet Core**: pulls nearby drops to you

## Shop + Powers

- Press **P** to open/close shop
- Buy/equip powers with **1 / 2 / 3**
- Press **Q** in combat for equipped power

Powers:
- **Dark Aura**: toggle ON/OFF, damages nearby enemies continuously (stays on)
- **Orbit Blades**: toggle ON/OFF, spinning damage around you (stays on)
- **Clone Rush**: temporary clone attack (this one expires)

## Run

```bash
python dodge_game.py
```

## Controls

- Move: `WASD` or Arrow keys
- Dash + spear hit: `Spacebar`
- Open shop: `P`
- Use equipped power / toggle power: `Q`
- Restart after death: `R`
