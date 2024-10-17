import json
import os
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def set_chrome_options(user_data_dir=None, chrome_binary_path=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)  # 启用浏览器保留
    options.add_argument('--enable-logging')  # 启用控制台日志
    options.add_argument("--disable-blink-features=AutomationControlled")
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    if chrome_binary_path:
        options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
    return options


def check_uid_banned(driver, uid):
    url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=1&keyword=&order=pubdate"
    #print(f"UID {uid} 正在检测.")

    driver.get(url)
    #time.sleep(2)  # 等待页面加载

    try:
        xpath = '//*[@id="app"]/div[1]/div[1]/div[1]/div/span'  # 根据实际情况更改XPath

        # 使用WebDriverWait等待元素可见
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        # 如果元素可见且可用，返回True（表示被封禁）
        if element.is_displayed() and element.is_enabled():
            return True

    except Exception as e:
        print(f"发生错误: {e}")

    return False  # 如果出现异常或条件不满足，默认认为未被封禁


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    user_data_dir = os.path.join(base_dir,  'User Data')
    chrome_binary_path = os.path.join(base_dir,  'chrome-win', 'chrome.exe')
    chrome_driver_path = os.path.join(base_dir, 'chromedriver.exe')

    options = set_chrome_options(user_data_dir, chrome_binary_path)

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    # 设置浏览器窗口大小（宽度, 高度）
    driver.set_window_size(1000, 700)
    # 设置浏览器窗口位置（x, y）
    driver.set_window_position(-850, 775)

    input_file = os.path.join(base_dir,  'uid.txt')  # uid.txt在附加文件文件夹下
    output_file = os.path.join(base_dir,  'banned.txt')  # banned.txt也在附加文件夹下
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(input_file, 'r') as f:
        uids = f.read().splitlines()

    with open(input_file, 'r') as f:
        uids = f.read().splitlines()

    banned_uids = []

    for uid in uids:
        if check_uid_banned(driver, uid):
            banned_uids.append(uid)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }

            search_url1 = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"

            # 发起HTTP GET请求获取搜索结果页面内容
            response = requests.get(search_url1, headers=headers, timeout=(5, 10))
            response.raise_for_status()  # 检查请求是否成功

            # 加载JSON响应数据
            data = json.loads(response.text)

            # 提取并显示"name"、"fans"和"current_level"字段
            name = data["data"]["card"]["name"]
            fans = data["data"]["card"]["fans"]
            current_level = data["data"]["card"]["level_info"]["current_level"]
            print(f"UID {uid} 被封禁. 昵称: {name}, 粉丝数: {fans}, 账号等级: {current_level}")

            # 动态写入被封禁的UID到文件
            with open(output_file, 'a') as f:
                f.write(uid + '\n')

        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }

            search_url1 = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"

            # 发起HTTP GET请求获取搜索结果页面内容
            response = requests.get(search_url1, headers=headers, timeout=(5, 10))
            response.raise_for_status()  # 检查请求是否成功

            # 加载JSON响应数据
            data = json.loads(response.text)

            # 提取并显示"name"、"fans"和"current_level"字段
            name = data["data"]["card"]["name"]
            fans = data["data"]["card"]["fans"]
            current_level = data["data"]["card"]["level_info"]["current_level"]
            print(f"UID {uid} 未被封禁. 昵称: {name}, 粉丝数: {fans}, 账号等级: {current_level}")

    print(f"被封禁的UID已写入 {output_file}.")

    # 根据需要选择关闭浏览器
    driver.quit()


if __name__ == "__main__":
    main()
