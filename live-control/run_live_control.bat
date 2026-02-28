@echo off
cd /d C:\Users\nearf\.openclaw\workspace\live-control
python -m pip install -r requirements.txt
python live_control.py
pause
