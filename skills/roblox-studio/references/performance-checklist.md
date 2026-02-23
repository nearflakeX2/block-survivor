# Roblox Performance Checklist

- Replace polling loops with events where possible
- Batch repetitive updates (UI + remotes)
- Avoid cloning heavy models repeatedly; pre-pool if needed
- Use streaming-friendly design for large maps
- Keep physics ownership clear for moving parts
- Avoid expensive per-frame operations in many LocalScripts
- Profile with MicroProfiler/Script Performance in Studio
