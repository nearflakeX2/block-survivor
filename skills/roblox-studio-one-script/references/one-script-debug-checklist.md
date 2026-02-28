# One-Script Debug Checklist

Use before sending final code.

## Functional checks

- Abilities trigger exactly once per input.
- Cooldowns block spam and recover correctly.
- Effects still work after player death/respawn.
- UI text/buttons do not disappear unexpectedly.

## Safety checks

- Server validates all remote actions.
- No client-provided damage or target trust.
- Nil guards for all character/body part references.

## Performance checks

- No unbounded loops without waits.
- Avoid creating Instances every frame.
- Clean event connections/state when player leaves.

## Regression checks

- Existing features still function.
- New feature does not break spawn flow.
- Script runs from correct location (usually ServerScriptService).
