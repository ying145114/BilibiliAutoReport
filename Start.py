import subprocess
import sys
import time
import os

print('所有关键词搜索和处理完成后，通过虚拟机在指定路径运行 Getuid.py')
base_dir = os.path.dirname(os.path.abspath(__file__))

# 使用相对路径设置 Python 可执行文件和脚本路径
report_script = os.path.join(base_dir, 'Report.py')

while True:  # 无限循环以重启 Getuid.py
    # 启动 Getuid.py
    python_executable = os.path.join(base_dir, 'venv', 'Scripts', 'python.exe')
    getuid_script = os.path.join(base_dir, 'Getuid.py')

    # 启动子进程
    report_process = subprocess.Popen([python_executable, getuid_script], shell=True)
    while report_process.poll() is None:  # 等待 report.py 结束
        time.sleep(1)  # 等待1秒钟

    # 检查 report.py 的退出状态
    if report_process.returncode == 0:
        print("Getuid.py 正常退出，正在重新启动 Getuid.py...")
        subprocess.run([sys.executable, __file__])  # 重新启动 getuid.py
        break  # 跳出循环，防止再次进入无限循环
    else:
        print(f"Getuid.py 出现错误，返回码: {report_process.returncode}，正在重新运行 Getuid.py...")