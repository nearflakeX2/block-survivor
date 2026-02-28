# Live Local Control (Mouse/Keyboard + Screenshot)

This runs a local API on `http://127.0.0.1:8765` for:
- screenshot capture
- mouse move/click
- keyboard type/press/hotkey

## Safety
- **ESC = emergency stop** (disables control immediately)
- PyAutoGUI fail-safe enabled (slam mouse to top-left corner)
- Actions are blocked unless active window title contains `RobloxStudioBeta` (configurable)

## Start
Double-click:
- `run_live_control.bat`

## Endpoints
- `GET /status`
- `POST /config`
- `GET /screenshot?max_width=1280&quality=80`
- `POST /move` `{ "x": 400, "y": 300, "duration": 0.08 }`
- `POST /click` `{ "x": 400, "y": 300, "button": "left", "double": false }`
- `POST /type` `{ "text": "hello" }`
- `POST /press` `{ "key": "enter" }`
- `POST /hotkey` `{ "keys": ["ctrl", "s"] }`
- `POST /scroll` `{ "clicks": -300 }`
- `POST /stop`

## Example (PowerShell)
```powershell
Invoke-RestMethod http://127.0.0.1:8765/status
Invoke-RestMethod -Method Post http://127.0.0.1:8765/move -ContentType 'application/json' -Body '{"x":700,"y":400}'
Invoke-RestMethod -Method Post http://127.0.0.1:8765/click -ContentType 'application/json' -Body '{"button":"left"}'
```
