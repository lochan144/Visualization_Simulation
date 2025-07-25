@echo off
echo ================================
echo NavIC + LoRa Monitoring System
echo ================================
echo.
echo Starting the real-time monitoring system...
echo Web interface will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the system
echo.

cd /d "%~dp0"
python app.py

pause
