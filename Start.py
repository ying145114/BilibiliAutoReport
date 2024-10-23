import subprocess
import sys
import time
import os
from datetime import datetime

print('启动Getuid.py')

base_dir = os.path.dirname(os.path.abspath(__file__))
log_folder = os.path.join(base_dir)  # 确保目录存在
os.makedirs(log_folder, exist_ok=True)
log_file_path = os.path.join(log_folder, 'log.txt')
# 使用相对路径设置 Python 可执行文件和脚本路径
python_executable = os.path.join(base_dir, 'venv', 'Scripts', 'python.exe')
getuid_script = os.path.join(base_dir, 'Getuid.py')
report_script = os.path.join(base_dir, 'Report.py')

# 日志文件路径


def log_error(message):
    """记录错误信息到日志文件"""
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        log_file.write(f"\n\n{timestamp} {message}")

while True:  # 无限循环
    # 启动 Getuid.py
    while True:  # 死循环以重启 Getuid.py
        getuid_process = subprocess.Popen([python_executable, getuid_script], shell=True)
        getuid_process.wait()  # 等待 Getuid.py 结束

        # 检查 Getuid.py 的退出状态
        if getuid_process.returncode == 0:
            print("Getuid.py 正常退出，正在启动 Report.py...")
            break  # 退出此循环，开始启动 Report.py
        else:
            error_message = f"Getuid.py 出现错误，返回码: {getuid_process.returncode}，正在重新运行 Getuid.py..."
            print(error_message)
            log_error(error_message)  # 记录错误信息

    # 启动 Report.py
    while True:  # 死循环以重启 Report.py
        report_process = subprocess.Popen([python_executable, report_script], shell=True)
        report_process.wait()  # 等待 Report.py 结束

        # 检查 Report.py 的退出状态
        if report_process.returncode == 0:
            print("Report.py 正常退出，正在重新启动 Getuid.py...")
            break  # 退出此循环，重新开始下一轮
        else:
            error_message = f"Report.py 出现错误，返回码: {report_process.returncode}，正在重新运行 Report.py..."
            print(error_message)
            log_error(error_message)  # 记录错误信息
