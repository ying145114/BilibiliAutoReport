=@echo off
chcp 65001

setlocal

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 运行 Start.py
python Report.py

:: 可选：停留在命令行窗口，查看输出
pause

endlocal
