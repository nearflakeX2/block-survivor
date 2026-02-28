import base64
import ctypes
import io
import threading
import time
from dataclasses import dataclass, asdict

from flask import Flask, jsonify, request
from mss import mss
from PIL import Image
import pyautogui

try:
    import win32gui
except Exception:
    win32gui = None


app = Flask(__name__)
pyautogui.FAILSAFE = True  # slam mouse to top-left corner to trigger fail-safe


@dataclass
class ControlConfig:
    enabled: bool = True
    allowed_window_substring: str = "RobloxStudioBeta"
    emergency_stop: bool = False
    last_action: str = "idle"


cfg = ControlConfig()
lock = threading.Lock()


def _foreground_title() -> str:
    if win32gui is None:
        return ""
    try:
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd) or ""
    except Exception:
        return ""


def _is_allowed_window() -> bool:
    if not cfg.allowed_window_substring:
        return True
    title = _foreground_title().lower()
    return cfg.allowed_window_substring.lower() in title


def _guard(action_name: str):
    if not cfg.enabled or cfg.emergency_stop:
        raise RuntimeError("Control disabled (enabled=false or emergency_stop=true)")
    if not _is_allowed_window():
        raise RuntimeError(
            f"Blocked: active window does not match '{cfg.allowed_window_substring}'"
        )
    cfg.last_action = action_name


def _esc_kill_switch_loop():
    # ESC virtual-key code = 0x1B
    # If pressed, immediately disable controls.
    while True:
        pressed = ctypes.windll.user32.GetAsyncKeyState(0x1B) & 0x8000
        if pressed:
            with lock:
                cfg.emergency_stop = True
                cfg.enabled = False
                cfg.last_action = "EMERGENCY_STOP"
            time.sleep(0.4)  # debounce
        time.sleep(0.03)


@app.get("/status")
def status():
    with lock:
        data = asdict(cfg)
    data["active_window"] = _foreground_title()
    data["screen_size"] = pyautogui.size()._asdict()
    return jsonify(data)


@app.post("/config")
def update_config():
    body = request.get_json(force=True, silent=True) or {}
    with lock:
        if "enabled" in body:
            cfg.enabled = bool(body["enabled"])
        if "allowed_window_substring" in body:
            cfg.allowed_window_substring = str(body["allowed_window_substring"])
        if "clear_emergency_stop" in body and body["clear_emergency_stop"]:
            cfg.emergency_stop = False
        cfg.last_action = "config_update"
        data = asdict(cfg)
    return jsonify(data)


@app.post("/stop")
def stop_now():
    with lock:
        cfg.emergency_stop = True
        cfg.enabled = False
        cfg.last_action = "STOP_ENDPOINT"
    return jsonify({"ok": True, "message": "Emergency stop engaged"})


@app.get("/screenshot")
def screenshot():
    max_width = int(request.args.get("max_width", 1280))
    quality = int(request.args.get("quality", 80))

    with mss() as sct:
        monitor = sct.monitors[1]  # primary
        shot = sct.grab(monitor)
        img = Image.frombytes("RGB", shot.size, shot.rgb)

    if img.width > max_width:
        ratio = max_width / float(img.width)
        img = img.resize((max_width, int(img.height * ratio)))

    buff = io.BytesIO()
    img.save(buff, format="JPEG", quality=quality)
    b64 = base64.b64encode(buff.getvalue()).decode("utf-8")

    return jsonify(
        {
            "ok": True,
            "width": img.width,
            "height": img.height,
            "image_base64_jpeg": b64,
        }
    )


@app.post("/move")
def move_mouse():
    body = request.get_json(force=True)
    x = int(body["x"])
    y = int(body["y"])
    duration = float(body.get("duration", 0.08))

    with lock:
        _guard("move")
        pyautogui.moveTo(x, y, duration=duration)

    return jsonify({"ok": True, "x": x, "y": y})


@app.post("/click")
def click_mouse():
    body = request.get_json(force=True)
    x = body.get("x")
    y = body.get("y")
    button = str(body.get("button", "left"))
    double = bool(body.get("double", False))

    with lock:
        _guard("click")
        if x is not None and y is not None:
            pyautogui.moveTo(int(x), int(y), duration=float(body.get("duration", 0.05)))
        if double:
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)

    return jsonify({"ok": True})


@app.post("/type")
def type_text():
    body = request.get_json(force=True)
    text = str(body.get("text", ""))
    interval = float(body.get("interval", 0.01))

    with lock:
        _guard("type")
        pyautogui.write(text, interval=interval)

    return jsonify({"ok": True, "chars": len(text)})


@app.post("/press")
def press_key():
    body = request.get_json(force=True)
    key = str(body["key"])

    with lock:
        _guard("press")
        pyautogui.press(key)

    return jsonify({"ok": True, "key": key})


@app.post("/hotkey")
def hotkey():
    body = request.get_json(force=True)
    keys = body.get("keys") or []
    if not isinstance(keys, list) or not keys:
        return jsonify({"ok": False, "error": "keys must be a non-empty list"}), 400

    with lock:
        _guard("hotkey")
        pyautogui.hotkey(*[str(k) for k in keys])

    return jsonify({"ok": True, "keys": keys})


@app.post("/scroll")
def scroll():
    body = request.get_json(force=True)
    clicks = int(body.get("clicks", -300))

    with lock:
        _guard("scroll")
        pyautogui.scroll(clicks)

    return jsonify({"ok": True, "clicks": clicks})


if __name__ == "__main__":
    threading.Thread(target=_esc_kill_switch_loop, daemon=True).start()
    app.run(host="127.0.0.1", port=8765, debug=False)
