# Roblox Security Checklist

- Never trust client-provided currency or item counts
- Validate all RemoteEvent args
- Enforce server cooldowns independent of client cooldowns
- Validate raycast/hit claims on server where feasible
- Reject impossible movement/action timing
- Sanitize text input before storage/broadcast
- Keep admin actions behind server-only permission checks
- Log suspicious repeated remote abuse per player
