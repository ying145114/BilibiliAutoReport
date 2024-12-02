from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
chrome_binary_path = os.path.join(base_dir, '..','附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '..','附加文件',  'chromedriver.exe')
check_path = os.path.join(base_dir,  'whitelist.txt')
uids = set()


options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.binary_location = chrome_binary_path
options.add_argument('--incognito')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  #禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome( service = service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
#driver.set_window_position(0, 0)  # 设置浏览器窗口位置（x, y）




try:
    with open(check_path, 'r', encoding='utf-8') as f:  # 以读取模式打开文件
        for line in f:
            line = line.strip()  # 去掉行首尾的空白字符
            if line:  # 如果不是空行，则认为是UID
                uids.add(line)
except Exception as e:
    print('无法读取UID文件')
    exit(0)




for uid in uids:
    userurl = f"https://space.bilibili.com/{uid}/video"
    driver.get(userurl)
    input("按 Enter 键关闭浏览器...")  # 通过输入来控制浏览器关闭



driver.quit()  # 关闭浏览器








