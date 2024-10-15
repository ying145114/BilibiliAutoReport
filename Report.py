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
from src import captcha
import os
import json


def remove_completed_uid(uid):
    try:
        with open('附加文件/uid.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open('附加文件/uid.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip() != uid:
                    f.write(line)

        print(f"已删除已完成的UID: {uid}")
    except Exception as e:
        print(f"删除已完成的UID时发生错误: {e}")


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
def set_chrome_options(user_data_dir=None, chrome_binary_path=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    options.add_argument("--disable-blink-features=AutomationControlled")
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    if chrome_binary_path:
        options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
    return options


def main():
    uids = read_uid_list('附加文件/uid.txt')  # 从 uid.txt 中读取 uid 列表

    base_dir = os.path.dirname(os.path.abspath(__file__))

    print('设置用户数据目录')
    user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')  # 使用相对路径
    print('设置 Chrome 可执行文件路径')
    chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')  # 使用相对路径
    blacklist_file = os.path.join(base_dir, '云端文件', 'blacklist.txt')  # black_list在云端文件文件夹下

    # 确保自定义的 ChromeDriver 路径也是正确的
    chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')  # 使用相对路径

    options = set_chrome_options(user_data_dir, chrome_binary_path)
    print('启动浏览器')

    # 使用 Service 来指定 ChromeDriver 的路径
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # 设置浏览器窗口大小（宽度, 高度）
    driver.set_window_size(1000, 700)
    # 设置浏览器窗口位置（x, y）
    driver.set_window_position(-850, 775)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    firstrun = 1

    try:
        if not uids:
            print("uid.txt 文件中没有可处理的UID，程序退出")
            exit(0)
        for uid in uids:

            # 判断代码
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            }
            search_url = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"

            try:
                response = requests.get(search_url, headers=headers, timeout=(5, 10))
                response.raise_for_status()

                data = json.loads(response.text)
                name = data["data"]["card"]["name"]
                print(f"检查完成，UID:{uid} ,名称: {name}")

                if name == "账号已注销":
                    with open(blacklist_file, 'a', encoding='utf-8') as bf:
                        bf.write(f"\n{uid}")  # 在写入 UID 前添加换行符
                        remove_completed_uid(uid)
                    continue  # 账号已注销，跳过后续操作

            except Exception as e:
                print(f"获取UID {uid} 的名称时发生错误: {e}")
                continue  # 如果出现错误，也跳过此UID
            url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=1&keyword=&order=pubdate"
            driver.get(url)

            time.sleep(2)
            screenshot_path = os.path.join('附加文件', '记录', f'{uid}.png')
            driver.save_screenshot(screenshot_path)
            print(f"截图已保存为 {screenshot_path}")

            print(f"UID: {uid} 页面已打开")
            remove_completed_uid(uid)
            current_window = driver.current_window_handle

            while True:
                # 等待60秒
                if firstrun == 1:
                    print('首次运行，等待1秒')
                    time.sleep(1)
                    firstrun = 0

                else:
                    print('非首次运行，等待58秒')
                    time.sleep(58)

                # 在当前标签页A中打开新标签页B执行其他任务
                driver.switch_to.new_window('tab')
                driver.get("https://www.bilibili.com/appeal/?avid=1205435530")

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
                )
                element.send_keys('视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频')
                print('已输入理由')

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
                )
                element.click()  #选择分类
                print('已选择分类')

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                )
                element.click()  # 生成验证码
                print('已点击确认')

                time.sleep(4)
                while True:
                    try:
                        # 等待并获取元素，增加了对超时的处理
                        try:
                            img = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                            )
                        except TimeoutException:
                            print("等待验证码超时，程序退出")
                            sys.exit(100)  # 超时退出
                        time.sleep(2)
                        f = img.get_attribute('style')
                        print('验证码已出现')

                        url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)

                        print(url)
                        content = requests.get(url).content
                        plan = captcha.TextSelectCaptcha().run(content)
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
                            print(x, y, "偏移前坐标")
                            print(a + x * lan_x, b + y * lan_y, "点击坐标")
                            ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
                            print(a + x * lan_x, b + y * lan_y)
                            ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                                -(b + y * lan_y)).perform()  # 将鼠标位置恢复到移动前
                            time.sleep(0.5)

                        # 执行点击确认按钮的操作
                        try:
                            element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
                            element.click()  # 点击确认按钮
                            print('已提交验证码')
                        except:
                            refresh_element = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh')))
                            refresh_element.click()  # 点击刷新验证按钮
                            print('已点击刷新按钮')

                        # 等待 'geetest_item_wrap' 元素消失，表示验证码验证成功
                        try:
                            WebDriverWait(driver, 3).until(
                                EC.invisibility_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                            )
                            print('验证码已消失')
                            print("验证码验证成功！")
                            break  # 成功验证后跳出循环
                        except Exception as e:
                            print(f"发生异常: {e}")

                    except Exception as e:
                        print(f"发生异常: {e}")
                        time.sleep(1)  # 等待1秒后重新执行整个过程
                        sys.exit(100)  # 如果发生异常也退出程序
                time.sleep(2)
                driver.close()

                # 切回到之前的窗口或标签页
                driver.switch_to.window(current_window)

                # 检查当前页面URL是否符合条件
                current_url = driver.current_url
                if "bi" in current_url:
                    print("地址栏中包含 'dynamic'，等待下一个UID")

                    #remove_completed_uid(uid)  # 删除已完成的UID
                    break
    except Exception as e:
        print(f"发生异常: {e}")
        sys.exit(10086)


    finally:
        driver.quit()


if __name__ == "__main__":
    main()
