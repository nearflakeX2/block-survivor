# Block Survivor (Python)

Latest updates:
- PASS 1: Added named world zones with live zone HUD label.
- PASS 1: Added biome events (Heatwave, Toxic Rain, Storm Front) that periodically alter combat/movement.
- PASS 1: Added hazard regions (Lava Pools + Toxic Bogs) in addition to rivers.
- PASS 2: Added capturable outposts with periodic defend rewards.
- PASS 2: Added build shortcuts (`B` wall, `N` trap) with coin costs.
- PASS 2: Added companion drone helper + `U` upgrade at captured outposts.
- PASS 3: Added vehicle mount (`X`) with speed/fuel management.
- PASS 3: Added portal challenge arenas (`J` near portal) with survival rewards.
- PASS 3: Added roaming world bosses that spawn independently of wave flow.
- PASS 4: Added weapon evolutions (Railgun Rounds + Apocalypse RPG) based on upgrade milestones.
- PASS 4: Added Rift Zone high-danger area with extra damage/spawns.
- PASS 4: Added extraction event (`K`) to call evac and survive for payout cashout.
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
- Floating combat text (+coins / damage ticks)

## New Gameplay Additions
- Boss wave every 5 waves + rotating boss archetypes (brute/summoner/artillery/vampire/storm)
- Enemy variants: charger, tank, shooter
- Rarity strip colors in the power panel (common/rare/epic/legendary)
- Edge threat indicators for offscreen enemies
- Cast powers auto-fire when reloaded (including Meteor)
- Added all suggested powers: Black Hole, Flamethrower, Frost Mine, Shield Drone, Vampiric, Shockwave, Orbital Laser, Decoy, Execution, Bounty, Cluster RPG, Phoenix, Chain Hook, Thunder Totem, Overclock
- Added throw/ability animations for new powers + reload bars/timers for active and proc-based powers
- New Start Page mode select: Classic / Hardcore
- When you reach coin milestones, game pauses and lets you choose 1 of 3 powers
- Pause mode now includes quick testing keys (1/2/3/4)
- Added Nuke Mine power (auto triggers every 30 seconds, massive wipe zone)
- Power panel now has bigger rows + always-visible up/down scroll buttons

## Run
```bash
python dodge_game.py
```