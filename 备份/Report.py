import subprocess

from selenium import webdriver
import time
import subprocess
import os
import requests
def read_uid_list(filename):
    uids = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("关键词"):
                continue  # 如果是关键词行，则跳过
            elif line:  # 如果不是空行，则认为是UID
                uids.append(line)
    return uids


# 设置 ChromeOptions
def set_chrome_options(user_data_dir=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    return options


def main():
    uids = read_uid_list('uid.txt')  # 从 uid.txt 中读取 uid 列表

    # 设置用户数据目录，如果不需要可以设为 None
    user_data_dir = r'C:\Users\Joshua\Desktop\User Data'  # 修改为你自己的目录
    options = set_chrome_options(user_data_dir)
    driver = webdriver.Chrome(options=options)

    try:
        for uid in uids:
            url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=2&keyword=&order=pubdate"
            driver.get(url)
            print(f"UID: {uid} 页面已打开")

            while True:
                # 监测控制台日志
                logs = driver.get_log('browser')
                for log in logs:
                    if "Refused to load the stylesheet" in log['message']:
                        driver.switch_to.new_window('tab')
                        driver.get("https://www.bilibili.com/appeal/?avid=14692212")
                        

                # 检查页面URL是否包含"pn=1"
                current_url = driver.current_url
                if "pn=1" in current_url:
                    print("地址栏中包含 'pn=1'，切换到下一个UID")
                    break

                time.sleep(80)  # 每隔80秒检查一次

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
