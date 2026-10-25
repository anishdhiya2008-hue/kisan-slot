@echo off
title Kisan Slot
echo Installing Flask (needed only the first time)...
where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% -m pip install flask
echo.
echo ================================================================
echo  Starting Kisan Slot. Open  http://localhost:5000  in Chrome.
echo  The staff PIN is printed below. Press Ctrl+C to stop.
echo ================================================================
%PY% app.py
pause
