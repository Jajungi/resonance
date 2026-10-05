@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo.
echo  공명 소개 + 스테이션
echo  http://127.0.0.1:8765/intro/
echo  http://127.0.0.1:8765/station.html
echo.
python "%~dp0serve.py" --port 8765
pause