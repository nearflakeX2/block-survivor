---
name: roblox-studio
description: Build, refactor, and debug Roblox Studio experiences using Luau. Use when creating Roblox game systems (leaderstats, round systems, tools, combat, UI, inventory, datastores, remotes), organizing Studio architecture, improving client/server security, or optimizing performance/network ownership.
---

# Roblox Studio Skill

Use this workflow for Roblox Studio requests.

## 1) Set project mode first

Start by identifying the request type:
- **System build**: New gameplay system (inventory, combat, round loop, economy, quests)
- **Bug fix**: Existing scripts fail or behave incorrectly
- **Optimization**: Reduce lag, memory, network traffic, script cost
- **Architecture cleanup**: Reorganize folders, remotes, modules, naming

Then state assumptions briefly and implement.

## 2) Use secure client/server boundaries

Always enforce:
- Keep authoritative game logic on the server
- Treat client input as untrusted
- Validate all RemoteEvent/RemoteFunction payloads (type, range, ownership)
- Rate-limit spammy remotes
- Never trust client-side currency, damage, inventory, or progression values

If a request conflicts with this, propose a secure variant.

## 3) Prefer this folder structure for new systems

Use this baseline unless project structure is explicitly provided:

- `ReplicatedStorage/Remotes/<SystemName>/...`
- `ReplicatedStorage/Shared/<SystemName>/*.lua` (pure shared modules)
- `ServerScriptService/Systems/<SystemName>/*.server.lua`
- `StarterPlayer/StarterPlayerScripts/<SystemName>/*.client.lua`

Keep modules small and single-purpose.

## 4) Implementation standards

- Use Luau type annotations where useful
- Return structured tables from modules
- Avoid global state; inject dependencies via `require`
- Guard nil paths with clear errors/warns
- Use `task.wait`, `task.spawn`, and signals responsibly
- Keep constants/config in dedicated module files

## 5) Datastore and persistence pattern

When persistence is requested:
- Separate profile schema from runtime state
- Add versioned schema defaults
- Use retry wrappers with backoff
- Save on `PlayerRemoving` and periodic autosave
- Handle `BindToClose` for shutdown
- Prevent duping via server-side transaction/order checks

## 6) Performance checklist

Before final output, check:
- Expensive loops throttled or event-driven
- No unbounded `while true do` without wait control
- Avoid repeated `GetDescendants` scans in hot paths
- Cache frequently used instances/services
- Minimize remote chatter and large payloads
- Use CollectionService tags for scalable lookups

## 7) Output format for code requests

When generating systems, deliver:
1. Short architecture summary
2. File tree
3. Full code per file (copy-paste ready)
4. Setup steps in Studio
5. Quick test checklist

## 8) Debug workflow

For bug reports:
1. Ask for exact error text + stack trace (if missing)
2. Identify whether fault is client/server/shared
3. Provide minimal patch diff first
4. Provide hardened final version after fix

## References

- Read `references/common-patterns.md` for reusable system patterns.
- Read `references/security-checklist.md` when remotes/economy/combat are involved.
- Read `references/performance-checklist.md` for optimization requests.
