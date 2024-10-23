from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
from src.method import jy_click
import requests
import time
import sys
import re
import os



skip = 9
proxies = {'http': None,'https': None}
base_dir = os.path.dirname(os.path.abspath(__file__))
uid_path = os.path.join(base_dir, '附加文件', 'uid.txt')
log_file_path = os.path.join(base_dir, '错误记录.txt')
success_directory = os.path.join(base_dir, '附加文件', '成功验证码')
fail_directory = os.path.join(base_dir, '附加文件', '失败验证码')
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')
os.makedirs(success_directory, exist_ok=True)
os.makedirs(fail_directory, exist_ok=True)


def log_error(message):
    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
        log_file.write(f"\n\n{timestamp} {message}")


def remove_completed_uid(uid):
    try:
        with open('附加文件/uid.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open('附加文件/uid.txt', 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip() != uid:
                    f.write(line)
        print(f"删除UID: {uid}")
    except Exception as e:
        print(f"删除UID时发生错误: {e}")


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


def trigger_captcha(browser):
    try:
        # 选择分类
        WebDriverWait(browser, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
        ).click()

        # 输入举报理由
        WebDriverWait(browser, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
        ).send_keys('视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频')

        while True:
            # 点击确认
            WebDriverWait(browser, 20, 1).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
            ).click()

            # 检查元素是否存在
            try:
                WebDriverWait(browser, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                )
                print("验证码元素已出现！")
                break  # 如果元素出现则退出循环
            except Exception:
                print("验证码元素未出现，重新点击确认...")

    except Exception as e:
        print(f"发生错误: {e}")


uids = []
with open(uid_path, 'r', encoding='utf-8') as f:# 以读取模式打开文件
    for line in f:
        line = line.strip()  # 去掉行首尾的空白字符
        if line:  # 如果不是空行，则认为是UID
            uids.append(line)


if not uids:
    print("uid.txt 文件中没有可处理的UID，程序退出")
    log_error("uid.txt 文件中没有可处理的UID，程序退出")
    exit(0)


options = webdriver.ChromeOptions()
options.add_argument('--enable-logging')  # 启用控制台日志
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
#options.add_argument("--headless")
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)# 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
#driver.set_window_position(-850, 775)  # 设置浏览器窗口位置（x, y）
driver.set_window_position(-850, 1355)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


try:
    for uid in uids:


        try:
            search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=1'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            response.raise_for_status()
            data = response.json()


            if 'data' in data and 'archives' in data['data'] and len(data['data']['archives']) > 0:
                first_video = data['data']['archives'][0]
                aid = first_video.get('aid')
                title = first_video.get('title')
                print(f"UID:{uid}, 第一个视频 AID: {aid}, 标题: {title}")


                if skip == 9:
                    print("不跳过人机验证")
                    url = f"https://www.bilibili.com/appeal/?avid={aid}"
                    driver.get(url)
                    trigger_captcha(driver)






                    while True:
                        try:
                            img = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                            )
                            f = img.get_attribute('style')
                            attempt = 0  # 初始化尝试计数
                            while ('url("' not in f) and (attempt < 10):
                                f = img.get_attribute('style')
                                attempt += 1
                                time.sleep(0.5)
                            print(attempt)
                            url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
                            print(url)
                            content = requests.get(url, proxies=proxies, timeout=(5, 10)).content


                            plan = jy_click.JYClick().run(content)
                            print(plan)

                            a, b = get_location(img)
                            lan_x = 306 / 334
                            lan_y = 343 / 384

                            for crop in plan:
                                x1, y1, x2, y2 = crop
                                x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                                print(a + x * lan_x, b + y * lan_y, "点击坐标")

                                # 执行点击操作
                                ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
                                ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                                    -(b + y * lan_y)).perform()  # 恢复鼠标位置
                                time.sleep(0.3)

                            try:  # 执行点击确认按钮的操作
                                element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
                                )
                                element.click()  # 提交验证码
                            except Exception as e:
                                print(f"提交验证码时发生错误: {e}")
                                refresh_element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh'))
                                )
                                refresh_element.click()  # 点击刷新验证按钮
                                print('已点击刷新按钮')




                            try:  # 等待 'geetest_item_wrap' 元素消失，表示验证码提交成功
                                WebDriverWait(driver, 3).until(
                                    EC.invisibility_of_element_located(
                                        (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                                )
                                print("验证码已消失！")


                                try:
                                    WebDriverWait(driver, 5).until(EC.alert_is_present())  # 等待最多5秒，直到弹窗出现
                                    alert = driver.switch_to.alert  # 切换到弹窗
                                    alert_text = alert.text  # 获取弹窗文本
                                    # 检查弹窗内容
                                    if not "-352" in alert_text:
                                        alert.accept()
                                        print("验证码验证成功！")
                                        success_name = url.split('/')[-1]
                                        success_path = os.path.join(success_directory, success_name)
                                        with open(success_path, 'wb') as file:
                                            file.write(content)
                                        print(f"图片已保存至: {success_path}")
                                        break
                                    else:
                                        log_error('意外情况，弹窗出现-352')
                                        sys.exit('意外情况，弹窗出现-352')
                                except TimeoutException:
                                    log_error('多次验证失败，程序退出')
                                    sys.exit('多次验证失败，程序退出')


                            except Exception as e:
                                print(f"验证码验证失败！，错误: {e}")
                                fail_name = url.split('/')[-1]
                                fail_path = os.path.join(fail_directory, fail_name)
                                with open(fail_path, 'wb') as file:
                                    file.write(content)
                                print(f"图片已保存至: {fail_path}")


                        except Exception as e:
                            print(f"人机验证循环出错，错误: {e}")
                            log_error(f"人机验证循环出错，错误: {e}")
                            sys.exit('人机验证循环出错')  # 如果发生异常也退出程序

                    skip = 0


                else:
                    print("跳过人机验证")
                    skip = skip + 1
                print(f"打开UID:{uid}")
                userurl = f"https://space.bilibili.com/{uid}/video"
                driver.get(userurl)
                start_time = time.time()

                while True:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= 6:  # 如果已超过 7 秒
                        break
                remove_completed_uid(uid)
                continue  # 使用 continue 继续下一个 UID



            else:
                print(f"UID {uid} 没有找到视频，继续下一个 UID。")
                remove_completed_uid(uid)
                continue  # 找不到任何视频，继续下一个 UID
        except (requests.exceptions.HTTPError, requests.exceptions.RequestException) as e:
            print(f"UID循环内发生错误,错误UID：{uid}，错误: {e}")
            log_error(f"UID循环内发生错误,错误UID：{uid}，错误: {e}")
            sys.exit(f"UID循环内发生错误,错误UID：{uid}")
    driver.quit()# 完成所有操作后关闭浏览器


except Exception as e:
    print(f"从文件获取UID时发生错误,错误: {e}")
    log_error(f"从文件获取UID时发生错误,错误: {e}")
    sys.exit('从文件获取UID时发生错误')


finally:
    driver.quit()


