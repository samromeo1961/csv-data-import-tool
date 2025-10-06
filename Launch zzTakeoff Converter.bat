@echo off
REM zzTakeoff Import Converter Launcher
REM Double-click this file to start the application

cd /d "%~dp0"
python takeoff_converter.py

REM Keep window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Application exited with error code: %ERRORLEVEL%
    echo.
    pause
)
