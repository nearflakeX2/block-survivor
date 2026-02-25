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
- **Damage Core**
- **Max HP Core**
- **Regen Core**
- **Lifesteal Core**
- **Bullet Speed Core**
- **Magnet Core**

## Shop + Powers

- Press **P** to open/close shop
- Buy/equip powers with **1..6**
- Press **Q** in combat for equipped power

Powers:
- **Dark Aura** (toggle)
- **Orbit Blades** (toggle)
- **Clone Rush** (temporary)
- **Blood Nova** (big AoE burst)
- **Auto Turret** (deploy turret)
- **Time Freeze** (slow enemies hard)

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
