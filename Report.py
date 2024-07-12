import re
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests
from src import captcha



def remove_completed_uid(uid):
    try:
        with open('uid.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        with open('uid.txt', 'w', encoding='utf-8') as f:
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
def set_chrome_options(user_data_dir=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir} ')

        # 设置用户数据目录
    return options


def main():
    uids = read_uid_list('uid.txt')  # 从 uid.txt 中读取 uid 列表

    # 设置用户数据目录，如果不需要可以设为 None
    user_data_dir = r'D:\BilibiliAutoReport\User Data'  # 修改为你自己的目录
    options = set_chrome_options(user_data_dir)

    driver = webdriver.Chrome(options=options)

    try:
        if not uids:
            print("uid.txt 文件中没有可处理的UID，程序退出")
            exit(0)
        for uid in uids:
            url = f"https://space.bilibili.com/{uid}/video?tid=0&pn=1&keyword=&order=pubdate"
            driver.get(url)
            # time.sleep(2)
            # driver.refresh()
            print(f"UID: {uid} 页面已打开")
            current_window = driver.current_window_handle

            while True:
                # 等待60秒
                time.sleep(60)

                # 在当前标签页A中打开新标签页B执行其他任务
                driver.switch_to.new_window('tab')
                driver.get("https://www.bilibili.com/appeal/?avid=14692212")

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div[3]/div[2]/textarea'))
                )
                element.send_keys('Python')
                print('已输入理由')

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'))
                )
                element.click() #选择分类
                print('已选择分类')

                element = WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div[5]/div[2]'))
                )
                element.click() #生成验证码
                print('已点击确认')

                time.sleep(4)
                while True:
                    try:
                        # 等待并获取元素
                        img = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]')))
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
                        WebDriverWait(driver, 3).until(
                            EC.invisibility_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]')))
                        print('验证码已消失')

                        print("验证码验证成功！")
                        break  # 成功验证后跳出循环

                    except Exception as e:
                        print(f"发生异常: {e}")
                        time.sleep(1)  # 等待1秒后重新执行整个过程

                time.sleep(3)

                driver.close()

                # 切回到之前的窗口或标签页
                driver.switch_to.window(current_window)

                # 检查当前页面URL是否符合条件
                current_url = driver.current_url
                if "pn=1&" in current_url:
                    print("地址栏中包含 'pn=1'，等待下一个UID")
                    remove_completed_uid(uid)  # 删除已完成的UID
                    break

    except Exception as e:
        print(f"发生异常: {e}")

    finally:
        driver.quit()
        exit(0)


if __name__ == "__main__":
    main()
