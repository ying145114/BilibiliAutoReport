import json
import re
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from urllib.parse import urlencode, quote
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import shutil
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
########################################################################################################################
blacklist_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/blacklist.txt'
whitelist_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/whitelist.txt'
keywords_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/keyword.txt'
whitelist_filename = os.path.join(base_dir, '附加文件','whitelist.txt')
blacklist_filename = os.path.join(base_dir, '附加文件','blacklist.txt')
keywords_filename = os.path.join(base_dir, '附加文件', 'keyword.txt')
cloud_whitelist_filename = os.path.join(base_dir, '云端文件', 'whitelist.txt')


########################################################################################################################
clearscript_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/附加文件/页面脚本/清空列表.js'
reportscript_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/附加文件/页面脚本/总脚本.js'
chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
clear_script = os.path.join(base_dir, '附加文件','页面脚本', '清空列表.js')
report_script = os.path.join(base_dir, '附加文件', '页面脚本', '总脚本.js')
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
########################################################################################################################
output_file = os.path.join(base_dir, '附加文件', 'uid.txt')
log_file = os.path.join(base_dir,'运行记录','错误记录.txt')
log_directory = os.path.join(base_dir, '运行记录')
os.makedirs(log_directory, exist_ok=True)
proxies = {'http': None, 'https': None}
exclude_uids = set()
numbers = set()
keywords = []
uid_list = []
uids = set()
watchlaters = set()
########################################################################################################################

def fetch_file (cloud_link,local_path,autoupdate):
    if autoupdate == True:
        download = requests.get(cloud_link, proxies=proxies, timeout=(3, 3))
        if download.status_code == 200:
            with open(local_path, 'wb') as out:
                out.write(download.content)
            print(f"成功下载文件并保存为 {local_path}")
        else:
            print(f"无法访问URL{cloud_link}，状态码：{download.status_code}")
    else:
        print('不进行自动更新')

def log_error(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        print(f"\n{timestamp} {message}")
        log.write(f"\n\n{timestamp} {message}")





if os.path.exists(output_file):
    with open(output_file, 'r', encoding='utf-8') as f:  # 以读取模式打开文件
        for line in f:
            line = line.strip()  # 去掉行首尾的空白字符
            if line:  # 如果不是空行，则认为是UID
                uids.add(line)
    os.remove(output_file)


else:
    print(f"文件 {output_file} 不存在，无需删除。")

try:
    fetch_file(blacklist_url,blacklist_filename,True)
    fetch_file(whitelist_url,whitelist_filename,True)
    fetch_file(keywords_url,keywords_filename,True)
    fetch_file(clearscript_url,clear_script,False)
    fetch_file(reportscript_url,report_script,False)
except Exception as e:
    print(f"删除UID时发生错误: {e}")


with open(keywords_filename, 'r', encoding='utf-8') as f:
    for line in f:
        stripped_line = line.strip()
        if stripped_line and not stripped_line.startswith('#'):  # 排除空行和以“#”开头的行
            keywords.append(stripped_line)

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  # 禁用缓存
options.add_argument("--headless")
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
# driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
# driver.set_window_position(-850, 775)  # 设置浏览器窗口位置（x, y）
# driver.set_window_position(-850, 1355)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


for keyword in keywords:  # 遍历关键词列表，进行搜索和处理
    default = f'https://search.bilibili.com/video?keyword={quote(keyword)}&from_source=video_tag'
    driver.get(default)
    elements = driver.find_elements(By.XPATH,"//*[@id='i_cecream']/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/div/a")
    uid_list.clear()
    count = 0
    for element in elements:
        href = element.get_attribute("href")
        match = re.search(r"space.bilibili.com/(\d+)", href)  # 在 href 中搜索匹配的内容
        if not match:
            continue
        uid = match.group(1)  # 获取匹配到的UID部分
        uids.add(uid)
        uid_list.append(uid)  # 添加 UID 到集合中
        count += 1
        if count >= 5:
            break
    print(f'\n关键词：{keyword}  默认排序结果：\n{uid_list}')
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f'\n关键词：{keyword}  默认排序结果：\n{uid_list}')
    print(default)


    pubdate = f'https://search.bilibili.com/video?keyword={quote(keyword)}&from_source=video_tag&order=pubdate'
    driver.get(pubdate)
    elements = driver.find_elements(By.XPATH,"//*[@id='i_cecream']/div/div[2]/div[2]/div/div/div[1]/div/div/div[2]/div/div/div/a")
    uid_list.clear()
    count = 0
    for element in elements:
        href = element.get_attribute("href")
        match = re.search(r"space.bilibili.com/(\d+)", href)  # 在 href 中搜索匹配的内容
        if not match:
            continue
        uid = match.group(1)  # 获取匹配到的UID部分
        uids.add(uid)
        uid_list.append(uid)  # 添加 UID 到集合中
        count += 1
        if count >= 5:
            break
    print(f'\n关键词：{keyword}  时间排序结果：\n{uid_list}')
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f'\n关键词：{keyword}  时间排序结果：\n{uid_list}')
    print(pubdate)

try:
    # 获取当前时间并格式化
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(log_directory, f'{timestamp}.txt')

    shutil.copy(output_file, backup_filename)
    print(f"成功保存备份：{backup_filename}")
except IOError as e:
    print(f"保存备份时发生错误：{e}")









url = f"https://api.bilibili.com/x/v2/history/toview"
driver.get(url)
json_data = driver.find_element("tag name", "pre").text  # 假设 API 返回的 JSON 数据在 <pre> 标签内
data = json.loads(json_data)
for item in data['data']['list']:
    mid = item['owner']['mid']
    with open(cloud_whitelist_filename, 'a') as file:  # 以追加方式打开文件
        file.write(f"\n{mid}")
    watchlaters.add(mid)
    uids.add(mid)
    print(mid)











with open(whitelist_filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()
    for line in lines:
        uid = line.strip()
        if uid.isdigit():  # 假设 UID 是数字格式
            uids.add(uid)

with open(cloud_whitelist_filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()
for line in lines:
    stripped_line = line.strip()
    if stripped_line:  # 确保不是空行
        try:
            number = int(stripped_line)
            numbers.add(number)
        except ValueError:
            print(f"警告: '{stripped_line}' 不是有效的UID，已跳过。")
numbers -= exclude_uids
sorted_numbers = sorted(numbers)
with open(cloud_whitelist_filename, 'w', encoding='utf-8') as file:
    for number in sorted_numbers:
        file.write(f"{number}\n")





with open(blacklist_filename, 'r', encoding='utf-8') as exclude_file:
    exclude_lines = exclude_file.readlines()
    for line in exclude_lines:
        exclude_uid = line.strip()
        if exclude_uid.isdigit():  # 假设 UID 是数字格式
            exclude_uids.add(exclude_uid)
uids -= exclude_uids



with open(output_file, 'w', encoding='utf-8') as f:
    for uid in uids:
        f.write(f'{uid}\n')
print('关键词搜索和UID全部处理完成')