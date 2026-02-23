# Common Roblox Patterns

## Leaderstats bootstrap
- Create Folder `leaderstats` under Player on join
- Add IntValue/Currency values server-side only
- Never let client write leaderstats directly

## Round system skeleton
- Intermission -> prepare -> round -> cleanup loop
- Keep state machine on server
- Broadcast read-only round state to clients

## Remote validation
- Validate payload types
- Validate entity ownership
- Validate cooldown and distance
- Early return on invalid data

## Tool/combat pattern
- Client: input + cosmetic feedback
- Server: hit validation, damage, cooldown, anti-exploit

## Inventory pattern
- Shared item definitions in ReplicatedStorage/Shared
- Server inventory source of truth
- Client receives filtered snapshot + updates

## UI state pattern
- Keep local UI state in one controller module
- Subscribe/unsubscribe cleanly to remotes/signals
- Debounce button handlers
