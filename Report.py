from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
import requests
import JYClick
import time
import sys
import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
########################################################################################################################
chrome_driver_path = os.path.join(base_dir, '附加文件','chromedriver.exe')
report_video = os.path.join(base_dir, '附加文件', '页面脚本', '总脚本.js')
send_comment = os.path.join(base_dir, '附加文件','页面脚本', '随机评论视频.js')
write_ticket = os.path.join(base_dir, '附加文件','页面脚本', '提交留言.js')
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')
########################################################################################################################
title_file = os.path.join(base_dir, '运行记录','标题记录.txt')
log_file = os.path.join(base_dir,  '运行记录','错误记录.txt')
success_directory = os.path.join(base_dir,'运行记录',  '成功验证码')
uid_file = os.path.join(base_dir, '附加文件', 'uid.txt')
fail_directory = os.path.join(base_dir,'运行记录',  '失败验证码')
log_directory = os.path.join(base_dir, '运行记录')
os.makedirs(log_directory, exist_ok=True)
########################################################################################################################
proxies = {'http': None, 'https': None}
uids = set()
aid = ''


def log_error(message):
    with open(log_file, 'a', encoding='utf-8') as log:
        timestamp = datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')
        log.write(f"\n\n{timestamp} {message}")
    driver.save_screenshot(os.path.join(log_directory, f'screenshot_{timestamp}.png'))
    print(f'{timestamp} {message}')
    print(os.path.join(log_directory, f'screenshot_{timestamp}.png'))

def remove_completed_uid(uid):
    try:
        with open(uid_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(uid_file, 'w', encoding='utf-8') as f:
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



with open(uid_file, 'r', encoding='utf-8') as f:  # 以读取模式打开文件
    for line in f:
        line = line.strip()  # 去掉行首尾的空白字符
        if line:  # 如果不是空行，则认为是UID
            uids.add(line)

if not uids:
    print("uid.txt 文件中没有可处理的UID，程序退出")
    log_error("uid.txt 文件中没有可处理的UID，程序退出")


options = webdriver.ChromeOptions()
options.timeouts = { 'script': 119000 }
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")#禁用缓存
options.add_argument("--headless")
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
#driver.set_window_position(-850, 775)  # 设置浏览器窗口位置（x, y）
#driver.set_window_position(-850, 1355)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

try:
    for uid in uids:
        try:

            search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=1'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            data = response.json()
            if 'data' in data and 'archives' in data['data'] and len(data['data']['archives']) > 0:
                first_video = data['data']['archives'][0]
                aid = first_video.get('aid')
                title = first_video.get('title')
                print(f"UID: {uid} ，AID: {aid} ，投稿视频: {title}")
                with open(title_file, 'a', encoding='utf-8') as file:
                    file.write(f"\nUID: {uid} ，AID: {aid} ，投稿视频: {title}")

            else:
                print(f"UID: {uid} 未找到投稿视频")
                with open(title_file, 'a', encoding='utf-8') as file:
                    file.write(f"\nUID: {uid} 未找到投稿视频")

                search_url = f'https://api.bilibili.com/x/polymer/space/seasons_series_list?mid={uid}&page_num=1&page_size=5'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
                response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
                data = response.json()

                if data.get('data', {}).get('items_lists', {}).get('seasons_list', []):
                    first_video = data['data']['items_lists']['seasons_list'][0]['archives'][0]
                    aid = first_video.get('aid')
                    title = first_video.get('title')
                    print(f"UID: {uid} ，AID: {aid} ，合集视频: {title}")
                    with open(title_file, 'a', encoding='utf-8') as file:
                        file.write(f"\nUID: {uid} ，AID: {aid} ，合集视频: {title}")
                else:
                    print(f"\nUID: {uid} 未找到合集视频")
                    with open(title_file, 'a', encoding='utf-8') as file:
                        file.write(f"\nUID: {uid} 未找到合集视频")




            userurl = f"https://space.bilibili.com/{uid}"
            driver.get(userurl)
            print(f'\n{userurl}\n')





            with open(report_video, "r", encoding="utf-8") as file:
                report = file.read()
            report_result = driver.execute_async_script(report)
            print(report_result)

            if "412" in report_result:
                log_error('报错412，等待5分钟')
                time.sleep(60)
                print('还剩4分钟')
                time.sleep(60)
                print('还剩3分钟')
                time.sleep(60)
                print('还剩2分钟')
                time.sleep(60)
                print('还剩1分钟')
                time.sleep(60)
                print('程序继续')







            if "352" in report_result or "412" in report_result:





#                logs = driver.get_log('browser')
#                warning_logs = [log for log in logs if log['level'] == 'WARNING']
#                for log in warning_logs:
#                    print(log['message'])
###############################################人机验证部分###############################################################
                url = f"https://www.bilibili.com/appeal/?avid={aid}"
                driver.get(url)
                try:
                    WebDriverWait(driver, 20, 1).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
                    ).click()
                    WebDriverWait(driver, 20, 1).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
                    ).send_keys('视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频')

                    while True:
                        # 点击确认
                        WebDriverWait(driver, 20, 1).until(
                            EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                        ).click()

                        # 检查元素是否存在
                        try:
                            WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                            )
                            print("验证码元素已出现！")
                            break  # 如果元素出现则退出循环
                        except Exception:
                            print("验证码元素未出现，重新点击确认...")
                        time.sleep(3)
                except Exception as e:
                    print(f"发生错误: {e}")


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

                        content = requests.get(url, proxies=proxies, timeout=(5, 10)).content

                        plan = JYClick.JYClick().run(content)

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
                            try:
                                refresh_element = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh'))
                                )
                                refresh_element.click()  # 点击刷新验证按钮
                                print('已点击刷新按钮')
                            except Exception as e:
                                print('点击刷新按钮出错！')
                                log_error('点击刷新按钮出错！')


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
                                    os.makedirs(success_directory, exist_ok=True)
                                    success_name = url.split('/')[-1]
                                    success_path = os.path.join(success_directory, success_name)
                                    with open(success_path, 'wb') as file:
                                        file.write(content)
                                    # print(f"图片已保存至: {success_path}")
                                    break
                                else:
                                    log_error('意外情况，弹窗出现-352')

                            except TimeoutException:
                                log_error('多次验证失败，程序退出')
                                raise


                        except Exception as e:
                            print(f"验证码验证失败！，错误: {e}")
                            os.makedirs(fail_directory, exist_ok=True)
                            fail_name = url.split('/')[-1]
                            fail_path = os.path.join(fail_directory, fail_name)
                            with open(fail_path, 'wb') as file:
                                file.write(content)
                            # print(f"图片已保存至: {fail_path}")



                    except Exception as e:
                        print(f"人机验证循环出错，错误: {e}")
                        log_error(f"人机验证循环出错，错误: {e}")
                        raise



###############################################人机验证部分###############################################################





            remove_completed_uid(uid)
            continue




        except Exception as e:
            print(f"UID循环出错,错误UID：{uid}，错误: {e}")
            log_error(f"UID循环出错,错误UID：{uid}，错误: {e}")
            raise
    driver.quit()  # 完成所有操作后关闭浏览器


except Exception as e:
    print(f"出错退出: {e}")
    log_error(f"出错退出: {e}")
    sys.exit('出错退出')


finally:
    driver.quit()