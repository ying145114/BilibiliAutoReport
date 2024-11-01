from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import os


base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '附加文件', '运行数据', 'chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')
options.binary_location = chrome_binary_path
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  #禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome( service = service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
#driver.set_window_position(0, 0)  # 设置浏览器窗口位置（x, y）
url = f"https://space.bilibili.com/"
driver.get(url)
input("按 Enter 键关闭浏览器...")  # 通过输入来控制浏览器关闭
driver.quit()  # 关闭浏览器
