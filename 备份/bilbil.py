import re
import time
import base64

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.devtools.v126 import browser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from src import captcha


def set_chrome_options(user_data_dir=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    return options


class BilBil(object):
    def __init__(self):
        chrome_options = self.options()
        user_data_dir = r'C:\Users\Joshua\Desktop\User Data'  # 修改为你自己的目录
        options = set_chrome_options(user_data_dir)

        self.browser = webdriver.Chrome(options=options)
        self.browser.switch_to.new_window('tab')
        # self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 30)
        self.url = "https://www.bilibili.com/video/BV1Gx411G7ox"
        self.cap = captcha.TextSelectCaptcha()

    def options(self):
        chrome_options = webdriver.ChromeOptions()
        return chrome_options

    def click(self, xpath):
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).click()

    def get_location(self, element):
        # 获取元素在屏幕上的位置信息
        location = element.location
        size = element.size
        height = size['height']
        width = size['width']
        left = location['x']
        top = location['y']
        right = left + width
        bottom = top + height
        script = f"return {{'left': {left}, 'top': {top}, 'right': {right}, 'bottom': {bottom}}};"
        rect = self.browser.execute_script(script)

        # # 计算元素的中心坐标
        # center_x = int((rect['left'] + rect['right']) / 2)
        # center_y = int((rect['top'] + rect['bottom']) / 2)
        # # 计算元素左上
        center_x = int(rect['left'])
        center_y = int(rect['top'])
        return center_x, center_y

    def bibi(self):
        url = "https://www.bilibili.com/video/BV1Gx411G7ox"
        self.browser.get(url)

        trigger_element = self.wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="arc_toolbar_report"]/div[2]/div[3]/span')))
        ActionChains(self.browser).move_to_element(trigger_element).perform()

        trigger_element = WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="arc_toolbar_report"]/div[2]/div[3]/span'))
        )
        # 使用 ActionChains 移动到触发元素
        ActionChains(self.browser).move_to_element(trigger_element).perform()
        # 执行 JavaScript 脚本点击视频投诉按钮
        js_script = 'document.querySelector(".video-complaint").click();'
        self.browser.execute_script(js_script)
        time.sleep(1)
        js_switch_to_iframe = """
                        const iframeElement = document.querySelector('div.appeal-box iframe');
                        const iframeDocument = iframeElement.contentDocument || iframeElement.contentWindow.document;
                        const buttonInsideIframe = iframeDocument.querySelector('.sub-tag-item .item-check-btn.blue');
                        buttonInsideIframe.click();
                        const textarea = iframeDocument.querySelector('textarea.cnt');
                        textarea.value = 'aaaaaaaa';
                        const inputEvent = new Event('input', {
                            bubbles: true,
                            cancelable: true,
                        });
                        textarea.dispatchEvent(inputEvent);
                        const confirmButton = iframeDocument.querySelector(".btn-confirm");
                        confirmButton.click();
                    """
        self.browser.execute_script(js_switch_to_iframe)



        # xpath = '//*[@id="van-popover-7155"]/div/div[4]/svg'
        # self.wait.until(EC.element_to_be_clickable(
        #     (By.XPATH, xpath))).click()

        # xpath = '//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[1]/div[3]/input'
        # self.wait.until(EC.presence_of_element_located(
        #     (By.XPATH, xpath))).send_keys('Python')
        # xpath = '//*[@id="app"]/div[2]/div[2]/div[3]/div[2]/div[2]/div[2]'
        # self.click(xpath)

        time.sleep(5)
        xpath = '//*[@class="geetest_item_wrap"]'
        logo = self.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath)))
        print(logo)
        # 获取图片路径
        f = logo.get_attribute('style')

        from urlextract import URLExtract

        extractor = URLExtract()
        # url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
        url="https://static.geetest.com/captcha_v3/batch/v3/74432/2024-06-25T17/word/8485c21a58934d128e7f1b63d3205dac.jpg"
        print(url)

        content = requests.get(url).content
        # 送入模型识别
        plan = self.cap.run(content)
        # 获取验证码坐标

        a, b = self.get_location(logo)
        print(a,b,"验证码左上角")

        # 前端展示对于原图的缩放比例
        lan_x = 305 / 344
        lan_y = 341 / 384
        for crop in plan:
            x1, y1, x2, y2 = crop
            x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
            print(x, y,"偏移前坐标")
            print( a+x * lan_x, b+y * lan_y, "点击坐标")
            ActionChains(self.browser).move_by_offset(140, 127).click().perform()
            print("击完成")
            ActionChains(self.browser).move_by_offset(-(a + x * lan_x), -(b + y * lan_y)).perform()  # 将鼠标位置恢复到移动前
            time.sleep(0.5)
        xpath = "/html/body/div[4]/div[2]/div[6]/div/div/div[3]/a/div"
        self.click(xpath)

        # if url:
        #
        #
        #     try:
        #         time.sleep(1)
        #         xpath = "/html/body/div[4]/div[2]/div[6]/div/div/div[3]/div/a[2]"
        #         self.click(xpath)
        #         sign = False
        #     except:
        #         sign = True
        # else:
        #     print("error: 未获得到验证码")
        #     sign = False
        #
        # return sign


if __name__ == '__main__':
    jd = BilBil()
    s = jd.bibi()
