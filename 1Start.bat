=@echo off
chcp 65001
setlocal
call venv\Scripts\activate.bat
python Start.py
pause
endlocal
