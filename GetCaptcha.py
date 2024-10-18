from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import os
import re
import sys
from selenium import webdriver
import time
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from sympy.physics.units import planck

from src import captcha
import os

output_directory = os.path.join('附加文件', '验证码')
os.makedirs(output_directory, exist_ok=True)
proxies = {
    'http': None,
    'https': None
}


def set_chrome_options(user_data_dir=None, chrome_binary_path=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    if chrome_binary_path:
        options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
    return options


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print('设置用户数据目录')
    user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')  # 使用相对路径
    print('设置 Chrome 可执行文件路径')
    chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')  # 使用相对路径

    # 确保自定义的 ChromeDriver 路径也是正确的
    chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')  # 使用相对路径

    options = set_chrome_options(user_data_dir, chrome_binary_path)
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    print('启动浏览器')

    # 使用 Service 来指定 ChromeDriver 的路径
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    # 设置浏览器窗口大小（宽度, 高度）
    driver.set_window_size(1000, 700)
    # 设置浏览器窗口位置（x, y）
    driver.set_window_position(0, 0)

    url = f"https://www.bilibili.com/appeal/?avid=1205435530"
    driver.get(url)
    while True:
        print("这是一个死循环")
        element = WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
        )
        element.send_keys(
            '视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频')
        # print('已输入理由')

        element = WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located(
                (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
        )
        element.click()  # 选择分类
        # print('已选择分类')

        element = WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
        )
        element.click()  # 生成验证码
        # print('已点击确认')

        time.sleep(4)
        while True:
            try:
                # 等待并获取元素，增加了对超时的处理
                try:
                    img = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                    )
                except TimeoutException:
                    print("等待验证码超时，程序退出")
                    sys.exit(100)  # 超时退出
                time.sleep(2)
                f = img.get_attribute('style')
                print('验证码已出现')

                url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)

                print(url)
                content = requests.get(url, proxies=proxies, timeout=(5, 10)).content
                file_name = os.path.basename(url)

                # 下载图片并保存

                file_path = os.path.join(output_directory, file_name)

                with open(file_path, 'wb') as f:
                    f.write(content)
                # plan = captcha.TextSelectCaptcha().run(content)
                plan = []
                print(plan)

                def get_location(target):
                    # 获取元素在屏幕上的位置信息
                    location = target.location
                    size = target.size
                    height = size['height']
                    width = size['width']
                    left = location['x']
                    top = location['y']
                    right = left + width
                    bottom = top + height
                    script = f"return {{'left': {left}, 'top': {top}, 'right': {right}, 'bottom': {bottom}}};"
                    rect = driver.execute_script(script)
                    left_x = int(rect['left'])
                    top_y = int(rect['top'])
                    return left_x, top_y

                a, b = get_location(img)
                lan_x = 306 / 334
                lan_y = 343 / 384

                for crop in plan:
                    x1, y1, x2, y2 = crop
                    x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                    # print(x, y, "偏移前坐标")
                    print(a + x * lan_x, b + y * lan_y, "点击坐标")
                    ActionChains(driver).move_by_offset(a + x * lan_x,
                                                        b + y * lan_y).click().perform()
                    ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                        -(b + y * lan_y)).perform()  # 将鼠标位置恢复到移动前
                    time.sleep(0.5)

                # 执行点击确认按钮的操作
                try:
                    refresh_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh')))
                    refresh_element.click()

                    # element = WebDriverWait(driver, 10).until(
                    #     EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
                    # element.click()  # 点击确认按钮
                    # print('已提交验证码')
                except:
                    refresh_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh')))
                    refresh_element.click()  # 点击刷新验证按钮
                    print('已点击刷新按钮')

                # 等待 'geetest_item_wrap' 元素消失，表示验证码验证成功
                try:
                    WebDriverWait(driver, 3).until(
                        EC.invisibility_of_element_located(
                            (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                    )
                    # print('验证码已消失')
                    print("验证码验证成功！")
                    break  # 成功验证后跳出循环
                except Exception as e:
                    print(f"验证码验证失败！")

            except Exception as e:
                print(f"发生异常: {e}")
                time.sleep(1)  # 等待1秒后重新执行整个过程
        url = f"https://www.bilibili.com/appeal/?avid=1205435530"
        driver.get(url)



if __name__ == "__main__":
    main()













