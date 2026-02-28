---
name: roblox-studio-one-script
description: Build, refactor, and debug Roblox Studio game systems using a single Script file workflow. Use when the user asks for Roblox code that must stay in one script (no ModuleScripts), rapid prototype combat/powers systems, simple UI wiring from one server script, or quick fixes for broken one-file Roblox projects.
---

# Roblox Studio One Script

Use this skill when the user wants fast Roblox results in one Script file.

## Workflow

1. Confirm one-script scope
- Keep logic in one Script unless user explicitly allows splitting.
- Ask only if required services/objects are unknown.

2. Build from the template pattern
- Use `references/one-script-template.md` for structure and naming.
- Keep clear sections: services, config, state, remotes, core systems, loops, cleanup.

3. Implement gameplay safely
- Validate remotes and player inputs server-side.
- Avoid expensive per-frame loops when possible.
- Use cooldowns/debounce for abilities and effects.

4. Debug and harden
- Use `references/one-script-debug-checklist.md` before finalizing.
- Check respawn behavior, character references, nil guards, and memory leaks.

5. Deliver copy-paste-ready code
- Return a complete script, not fragments, for one-script requests.
- Include a short “where to put this Script” note (e.g., ServerScriptService).

## Output rules

- Prefer a full working script over partial patches.
- Keep comments short and functional.
- Preserve existing feature behavior unless user asks for redesign.
- If a feature is too large for one script, say so and offer a phased one-script version first.
