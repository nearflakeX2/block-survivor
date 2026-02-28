# One-Script Roblox Template Pattern

Use this section order for maintainability.

1. `-- Services`
2. `-- Config`
3. `-- Runtime State`
4. `-- Remote setup`
5. `-- Utility functions`
6. `-- Core systems (combat, powers, round logic)`
7. `-- Player lifecycle hooks`
8. `-- Main loops / timers`

## Skeleton

```lua
-- Services
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

-- Config
local COOLDOWN = 2

-- Runtime State
local playerState = {}

-- Remote setup
local remotesFolder = ReplicatedStorage:FindFirstChild("Remotes") or Instance.new("Folder")
remotesFolder.Name = "Remotes"
remotesFolder.Parent = ReplicatedStorage

local actionRemote = remotesFolder:FindFirstChild("Action") or Instance.new("RemoteEvent")
actionRemote.Name = "Action"
actionRemote.Parent = remotesFolder

-- Utility
local function getState(player)
    local s = playerState[player]
    if not s then
        s = {lastCast = 0}
        playerState[player] = s
    end
    return s
end

-- Core
local function canCast(player)
    local s = getState(player)
    local now = os.clock()
    if now - s.lastCast < COOLDOWN then return false end
    s.lastCast = now
    return true
end

actionRemote.OnServerEvent:Connect(function(player, action, payload)
    if action ~= "Cast" then return end
    if not canCast(player) then return end
    -- do effect safely
end)

-- Lifecycle
Players.PlayerRemoving:Connect(function(player)
    playerState[player] = nil
end)
```

## Rules

- Never trust client damage values.
- Guard every character access (`player.Character`, `HumanoidRootPart`, `Humanoid`).
- Clean up per-player state on leave.
- Keep constants in one config block at top.
