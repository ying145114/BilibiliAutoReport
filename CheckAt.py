import time
from datetime import datetime, timedelta
import requests
import json
import re
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os





base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')
log_file = os.path.join(base_dir, '附加文件', 'ATLOG.txt')
output_file = os.path.join(base_dir, '附加文件', 'uid.txt')
proxies = {'http': None, 'https': None}
mids = set()


with open(log_file, 'a', encoding='utf-8') as file:
    file.write(f"{(datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H-%M-%S')}\n")

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')
options.binary_location = chrome_binary_path
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  # 禁用缓存
options.add_argument("--headless")
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
# driver.set_window_position(0, 0)  # 设置浏览器窗口位置（x, y）
url = f"https://space.bilibili.com/"
driver.get(url)

cookies = driver.get_cookies()
COOKIE = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
UA = driver.execute_script("return navigator.userAgent;")


with open(log_file, 'a', encoding='utf-8') as file:
    file.write(f"{(datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H-%M-%S')}\n")
headers = {'cookie': COOKIE, 'user-agent': UA}
params = {'build': '0', 'mobi_app': 'web', }
response = requests.get('https://api.vc.bilibili.com/x/im/web/msgfeed/unread', proxies=proxies, params=params,
                        headers=headers)
# print(response.text)
data = json.loads(response.text)
at = data['data']['at']

print("被提及次数：", at)

headers = {'cookie': COOKIE, 'user-agent': UA}
params = {'build': '0', 'mobi_app': 'web', }
response = requests.get('https://api.bilibili.com/x/msgfeed/at', proxies=proxies, params=params, headers=headers)
# print(response.text)
data = json.loads(response.text)
subject_ids = []
source_ids = []
source_contents = []

for i, item in enumerate(data['data']['items']):
    if i >= at:  # 达到 n 时停止
        break
    subject_ids.append(item['item']['subject_id'])
    source_ids.append(item['item']['source_id'])
    source_contents.append(item['item']['source_content'])
print(subject_ids, source_ids,source_contents)

for subject_id, source_id,source_content in zip(subject_ids, source_ids,source_contents):
    headers = {'cookie': COOKIE, 'user-agent': UA}
    data = {
        'oid': subject_id,
        'type': 1,
        'rpid': source_id,
        'action': 1,
        'csrf': re.search(r'bili_jct=([^;]*)', COOKIE).group(1),
        'statistics': '{"appId":100,"platform":5}'
    }
    response = requests.post('https://api.bilibili.com/x/v2/reply/action', proxies=proxies, headers=headers, data=data)
    print('点赞评论：', response.text)

    headers = {'cookie': COOKIE, 'user-agent': UA}
    params = {'aid': subject_id}
    response = requests.get('https://api.bilibili.com/x/web-interface/view', proxies=proxies, params=params,headers=headers)
    data = json.loads(response.text)
    try:
        mid = data['data']['owner']['mid']
        print('解析的UID:',mid)
        mids.add(mid)
    except Exception as e:
        print('出错')
    uids = re.findall(r'\d+', source_content)
    print('提取的UID: ',uids)
    mids.update(uids)
    time.sleep(1)



for mid in mids:
    with open(output_file, 'a', encoding='utf-8') as file:
        file.write(f"{mid}\n")
    with open(log_file, 'a', encoding='utf-8') as file:
        file.write(f"{mid}\n")