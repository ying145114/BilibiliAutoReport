import re
import sys
from datetime import datetime
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

skip = 9
proxies = {
    'http': None,
    'https': None
}

base_dir = os.path.dirname(os.path.abspath(__file__))
log_folder = os.path.join(base_dir)  # 确保目录存在
os.makedirs(log_folder, exist_ok=True)
log_file_path = os.path.join(log_folder, 'log.txt')

def log_error(message):
    """记录错误信息到日志文件"""
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

    #print('设置用户数据目录')
    user_data_dir = os.path.join(base_dir, '附加文件', 'User Data')  # 使用相对路径
    #print('设置 Chrome 可执行文件路径')
    chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')  # 使用相对路径
    blacklist_file = os.path.join(base_dir, '云端文件', 'blacklist.txt')  # black_list在云端文件文件夹下

    # 确保自定义的 ChromeDriver 路径也是正确的
    chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')  # 使用相对路径

    options = set_chrome_options(user_data_dir, chrome_binary_path)
    #print('启动浏览器')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    # 使用 Service 来指定 ChromeDriver 的路径
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    # 设置浏览器窗口大小（宽度, 高度）
    driver.set_window_size(1000, 700)
    # 设置浏览器窗口位置（x, y）
    #driver.set_window_position(-850, 775)
    driver.set_window_position(-850, 1355)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    try:
        if not uids:
            print("uid.txt 文件中没有可处理的UID，程序退出")
            log_error("uid.txt 文件中没有可处理的UID，程序退出")
            exit(0)

        for uid in uids:
            try:
                search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0'
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                }

                response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
                response.raise_for_status()

                data = response.json()
                # print(response.text)

                # 检查返回数据是否包含 archives
                if 'data' in data and 'archives' in data['data'] and len(data['data']['archives']) > 0:
                    first_video = data['data']['archives'][0]
                    aid = first_video.get('aid')
                    title = first_video.get('title')

                    if aid and title:
                        print(f"UID:{uid}, 第一个视频 AID: {aid}, 标题: {title}")

                        # 找到 aid 后，打开链接并进行进一步处理
                        global skip
                        if skip == 9:
                            print("不跳过人机验证")
                            url = f"https://www.bilibili.com/appeal/?avid={aid}"
                            driver.get(url)

                            element = WebDriverWait(driver, 20, 1).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
                            )
                            element.send_keys(
                                '视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频')
                            #print('已输入理由')

                            element = WebDriverWait(driver, 20, 1).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
                            )
                            element.click()  # 选择分类
                            #print('已选择分类')

                            element = WebDriverWait(driver, 20, 1).until(
                                EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                            )
                            element.click()  # 生成验证码
                            #print('已点击确认')

                            #time.sleep(4)
                            while True:
                                try:
                                    # 等待并获取元素，增加了对超时的处理
                                    try:
                                        img = WebDriverWait(driver, 5).until(
                                            EC.presence_of_element_located(
                                                (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                                        )


                                    except TimeoutException:
                                        print('验证码未出现，再次尝试点击')
                                        element = WebDriverWait(driver, 20, 1).until(
                                            EC.presence_of_element_located(
                                                (By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                                        )
                                        element.click()  # 再次尝试点击确认

                                        try:
                                            img = WebDriverWait(driver, 5).until(
                                                EC.presence_of_element_located(
                                                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                                            )
                                        except TimeoutException:
                                            print("等待验证码超时，程序退出")
                                            log_error('等待验证码超时，程序退出')
                                            sys.exit('等待验证码超时，程序退出')  # 超时退出

                                    #time.sleep(2)
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
                                        #print(x, y, "偏移前坐标")
                                        print(a + x * lan_x, b + y * lan_y, "点击坐标")
                                        ActionChains(driver).move_by_offset(a + x * lan_x,
                                                                            b + y * lan_y).click().perform()
                                        ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                                            -(b + y * lan_y)).perform()  # 将鼠标位置恢复到移动前
                                        time.sleep(0.5)

                                    # 执行点击确认按钮的操作
                                    try:
                                        element = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip')))
                                        element.click()  # 点击确认按钮
                                        #print('已提交验证码')
                                    except:
                                        refresh_element = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh')))
                                        refresh_element.click()  # 点击刷新验证按钮
                                        print('已点击刷新按钮')
                                        save_directory = os.path.join(base_dir, '附加文件', '失败验证码')
                                        os.makedirs(save_directory, exist_ok=True)  # 创建文件夹，如果已经存在则不会报错

                                        # 从URL中提取文件名
                                        file_name = url.split('/')[-1]
                                        file_path = os.path.join(save_directory, file_name)

                                        # 保存图片
                                        with open(file_path, 'wb') as file:
                                            file.write(content)

                                        print(f"图片已保存至: {file_path}")

                                    # 等待 'geetest_item_wrap' 元素消失，表示验证码验证成功
                                    try:
                                        WebDriverWait(driver, 3).until(
                                            EC.invisibility_of_element_located(
                                                (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                                        )
                                        #print('验证码已消失')
                                        print("验证码验证成功！")
                                        save_directory = os.path.join(base_dir, '附加文件', '成功验证码')
                                        os.makedirs(save_directory, exist_ok=True)  # 创建文件夹，如果已经存在则不会报错

                                        # 从URL中提取文件名
                                        file_name = url.split('/')[-1]
                                        file_path = os.path.join(save_directory, file_name)

                                        # 保存图片
                                        with open(file_path, 'wb') as file:
                                            file.write(content)

                                        print(f"图片已保存至: {file_path}")

                                        try:
                                            WebDriverWait(driver, 5).until(EC.alert_is_present())  # 等待最多10秒，直到弹窗出现
                                            alert = driver.switch_to.alert  # 切换到弹窗
                                            alert_text = alert.text  # 获取弹窗文本
                                            # 检查弹窗内容
                                            if not "-352" in alert_text:
                                                alert.accept()
                                                break
                                            else:
                                                log_error('意外情况，弹窗出现-352')
                                                sys.exit('意外情况，弹窗出现-352')
                                        except TimeoutException:
                                            log_error('多次验证失败，程序退出')
                                            sys.exit('多次验证失败，程序退出')


                                    except Exception as e:
                                        print(f"验证码验证失败！")
                                        save_directory = os.path.join(base_dir, '附加文件', '失败验证码')
                                        os.makedirs(save_directory, exist_ok=True)  # 创建文件夹，如果已经存在则不会报错

                                        # 从URL中提取文件名
                                        file_name = url.split('/')[-1]
                                        file_path = os.path.join(save_directory, file_name)

                                        # 保存图片
                                        with open(file_path, 'wb') as file:
                                            file.write(content)

                                        print(f"图片已保存至: {file_path}")

                                except Exception as e:
                                    print(f"人机验证循环出错，错误: {e}")
                                    log_error(f"人机验证循环出错，错误: {e}")
                                    sys.exit('人机验证循环出错')  # 如果发生异常也退出程序

                            #time.sleep(2)
                            skip = 0

                        else:
                            print("跳过人机验证")
                            skip = skip + 1

                        print(f"打开UID:{uid}")
                        userurl = f"https://space.bilibili.com/{uid}"
                        driver.get(userurl)
                        #time.sleep(5)
                        start_time = time.time()

                        # 循环检查是否已达到 7 秒
                        while True:
                            elapsed_time = time.time() - start_time
                            if elapsed_time >= 6:  # 如果已超过 7 秒
                                break
                        remove_completed_uid(uid)
                        # 处理完成后继续下一个 UID
                        continue  # 使用 continue 继续下一个 UID


                else:
                    print(f"UID {uid} 没有找到视频，继续下一个 UID。")
                    remove_completed_uid(uid)
                    continue  # 找不到任何视频，继续下一个 UID

            except Exception as e:
                print(f"处理UID的循环内发生错误,错误UID：{uid}，错误: {e}")
                log_error(f"处理UID的循环内发生错误,错误UID：{uid}，错误: {e}")
                sys.exit(f"处理UID的循环内发生错误,错误UID：{uid}")
                # continue  # 如果在处理过程中出现异常，继续下一个 UID

        # 完成所有操作后关闭浏览器
        driver.quit()






    except Exception as e:
        print(f"从文件获取UID时发生错误,错误: {e}")
        log_error(f"从文件获取UID时发生错误,错误: {e}")
        sys.exit('从文件获取UID时发生错误')


    finally:
        driver.quit()


if __name__ == "__main__":
    main()
