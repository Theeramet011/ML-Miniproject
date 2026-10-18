@echo off
chcp 65001 > nul
echo ============================================================
echo   กำลังเริ่มต้นระบบ Thailand Green Energy & EV Planner...
echo   (Streamlit Web Application)
echo ============================================================
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause
