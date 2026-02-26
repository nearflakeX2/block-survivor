# Block Survivor (Python)

Latest updates:
- RPG now has a **big obvious explosion**
- Turrets now **stay until destroyed** (no timeout)
- Upgrading turret **does not delete old turrets**
- Added **Machine Gun** upgrade
- Clone Swarm still included
- Meteor Shower uses shrinking red warning circles then explosion
- Cast powers now have **reload/cooldowns**
- Added a **bottom reload bar HUD** (RPG, Meteor, and other cast powers)
- Each power shows **current level + next upgrade cost** in the panel

## Controls
- Move: `WASD` / Arrow keys
- Dash + spear hit: `Space`
- Pause/Resume: `P` (or click pause button)
- Restart: `R`
- Mouse wheel: scroll power list
- Mouse left click: buy/upgrade power in panel

## Visual Effects
- Screen shake on big explosions (RPG/meteor)
- RPG rockets now have a smoke trail
- Meteor warning now includes a visible falling meteor core/tail

## Run
```bash
python dodge_game.py
```