# import re
# import subprocess
#
# from selenium import webdriver
# import time
# import subprocess
# import os
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.action_chains import ActionChains
# import requests
#
# from src import captcha
#
#
# def read_uid_list(filename):
#     uids = []
#     with open(filename, 'r', encoding='utf-8') as f:
#         for line in f:
#             line = line.strip()
#             if line.startswith("关键词"):
#                 continue  # 如果是关键词行，则跳过
#             elif line:  # 如果不是空行，则认为是UID
#                 uids.append(line)
#     return uids
#
#
# # 设置 ChromeOptions
# def set_chrome_options(user_data_dir=None):
#     options = webdriver.ChromeOptions()
#     options.add_experimental_option("detach", True)
#     options.add_argument('--enable-logging')  # 启用控制台日志
#     if user_data_dir:
#         options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
#     return options
#
#
# def main():
#     uids = read_uid_list('uid.txt')  # 从 uid.txt 中读取 uid 列表
#
#     # 设置用户数据目录，如果不需要可以设为 None
#     user_data_dir = r'C:\Users\Joshua\Desktop\User Data'  # 修改为你自己的目录
#     options = set_chrome_options(user_data_dir)
#     driver = webdriver.Chrome(options=options)
#
#
#     try:
#         for uid in uids:
#             url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=2&keyword=&order=pubdate"
#             driver.get(url)
#             print(f"UID: {uid} 页面已打开")
#             current_window = driver.current_window_handle
#             time.sleep(6)
#
#             driver.switch_to.new_window('tab')
#             driver.get("https://www.bilibili.com/appeal/?avid=14692212")
#             element = WebDriverWait(driver, 20, 0.5).until(
#                 EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
#             )
#             element.send_keys('Python')
#             element = WebDriverWait(driver, 20, 0.5).until(
#                 EC.presence_of_element_located(
#                     (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
#             )
#             element.click()
#             element = WebDriverWait(driver, 20, 0.5).until(
#                 EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
#             )
#             element.click()
#             time.sleep(3)
#             img = WebDriverWait(driver, 20, 0.5).until(
#                 EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
#             )
#             f = img.get_attribute('style')
#             from urlextract import URLExtract
#
#             extractor = URLExtract()
#             url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
#
#             print(url)
#             content = requests.get(url).content
#             plan = captcha.TextSelectCaptcha().run(content)
#             print(plan)
#
#             def get_location(target):
#                 # 获取元素在屏幕上的位置信息
#                 location = target.location
#                 size = target.size
#                 height = size['height']
#                 width = size['width']
#                 left = location['x']
#                 top = location['y']
#                 right = left + width
#                 bottom = top + height
#                 script = f"return {{'left': {left}, 'top': {top}, 'right': {right}, 'bottom': {bottom}}};"
#                 rect = driver.execute_script(script)
#                 left_x = int(rect['left'])
#                 top_y = int(rect['top'])
#                 return left_x, top_y
#
#             a, b = get_location(img)
#             lan_x = 306 / 334
#             lan_y = 343 / 384
#             for crop in plan:
#                 x1, y1, x2, y2 = crop
#                 x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
#                 print(x, y, "偏移前坐标")
#                 print(a + x * lan_x, b + y * lan_y, "点击坐标")
#                 ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
#                 print(a + x * lan_x, b + y * lan_y)
#                 ActionChains(driver).move_by_offset(-(a + x * lan_x),
#                                                     -(b + y * lan_y)).perform()  # 将鼠标位置恢复到移动前
#                 time.sleep(0.5)
#
#             element = driver.find_element(By.CLASS_NAME, 'geetest_commit_tip')
#             element.click()
#             time.sleep(1)
#
#             driver.close()
#
#             # 切回到之前的窗口或标签页
#             driver.switch_to.window(current_window)
#
#                 # 检查页面URL是否包含"pn=1"
#             current_url = driver.current_url
#             if "pn=1" in current_url:
#                 print("地址栏中包含 'pn=1'，切换到下一个UID")
#
#
#
#
#     except Exception as e:
#         print(f"发生异常: {e}")
#
#     finally:
#         driver.quit()
#
#
# if __name__ == "__main__":
#     main()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
import re
import subprocess

from selenium import webdriver
import time
import subprocess
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests

from src import captcha


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
    options.add_argument('--unexpectedAlertBehaviour=dismiss')
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir} ')
        options.add_argument('--unexpectedAlertBehaviour=dismiss')
        # 设置用户数据目录
    return options


def main():
    uids = read_uid_list('uid.txt')  # 从 uid.txt 中读取 uid 列表

    # 设置用户数据目录，如果不需要可以设为 None
    user_data_dir = r'D:\BilibiliAutoReport\User Data'  # 修改为你自己的目录
    options = set_chrome_options(user_data_dir)

    driver = webdriver.Chrome(options=options)

    try:
        for uid in uids:
            url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=2&keyword=&order=pubdate"
            driver.get(url)
            print(f"UID: {uid} 页面已打开")
            current_window = driver.current_window_handle

            while True:
                # 等待60秒
                time.sleep(60)

                # 在当前标签页A中打开新标签页B执行其他任务
                driver.switch_to.new_window('tab')
                driver.get("https://www.bilibili.com/appeal/?avid=14692212")
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                element = WebDriverWait(driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
                )
                element.send_keys('Python')
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                element = WebDriverWait(driver, 20, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
                )
                element.click()
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                element = WebDriverWait(driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                )
                element.click()
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                time.sleep(4)
                img = WebDriverWait(driver, 20, 0.5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                )
                f = img.get_attribute('style')
                from urlextract import URLExtract

                extractor = URLExtract()
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

                element = driver.find_element(By.CLASS_NAME, 'geetest_commit_tip')
                element.click()
                time.sleep(3)

                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except:
                    pass
                driver.close()

                # 切回到之前的窗口或标签页
                driver.switch_to.window(current_window)

                # 检查当前页面URL是否符合条件
                current_url = driver.current_url
                if "pn=1" in current_url:
                    print("地址栏中包含 'pn=1'，等待下一个UID")
                    break

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        driver.quit()
        exit(0)






if __name__ == "__main__":
    main()
