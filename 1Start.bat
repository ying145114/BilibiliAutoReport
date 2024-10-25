=@echo off
setlocal
chcp 65001s

:: �������⻷��
call venv\Scripts\activate.bat

:: ���� Start.py
python Start.py

:: ��ѡ��ͣ���������д��ڣ��鿴���
pause

endlocal
