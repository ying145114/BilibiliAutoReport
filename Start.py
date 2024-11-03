from datetime import datetime
import subprocess
import os


print('启动Getuid.py')
base_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(base_dir, '附加文件','运行记录','错误记录.txt')
python_executable = os.path.join(base_dir, 'venv', 'Scripts', 'python.exe')
getuid_script = os.path.join(base_dir, 'Getuid.py')
report_script = os.path.join(base_dir, 'Report.py')
filteruid_script = os.path.join(base_dir, 'UidFilter.py')



def log_error(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        log.write(f"\n\n{timestamp} {message}")


while True:
    while True:  # 死循环以重启 Getuid.py
        getuid_process = subprocess.Popen([python_executable, getuid_script], shell=True)
        getuid_process.wait()  # 等待 Getuid.py 结束


        if getuid_process.returncode == 0:# 检查 Getuid.py 的退出状态
            print("Getuid.py 正常退出，正在启动 Report.py...")
            break  # 退出此循环，开始启动 Report.py
        else:
            error_message = f"Getuid.py 出现错误，返回码: {getuid_process.returncode}，正在重新运行 Getuid.py..."
            print(error_message)
            log_error(error_message)  # 记录错误信息

#    print('对UID进行过滤处理')
    filteruid_process = subprocess.Popen([python_executable, filteruid_script], shell=True)
#    filteruid_process.wait()



    while True:  # 死循环以重启 Report.py
        report_process = subprocess.Popen([python_executable, report_script], shell=True)
        report_process.wait()  # 等待 Report.py 结束


        if report_process.returncode == 0: # 检查 Report.py 的退出状态
            print("Report.py 正常退出，正在重新启动 Getuid.py...")
            break  # 退出此循环，重新开始下一轮
        else:
            error_message = f"Report.py 出现错误，返回码: {report_process.returncode}，正在重新运行 Report.py..."
            print(error_message)
            log_error(error_message)  # 记录错误信息
