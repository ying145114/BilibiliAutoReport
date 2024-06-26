#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: jiajia
@file: bilbil.py
@time: 2020/8/22 18:48
"""
import re
import time
import base64

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from src import captcha


def set_chrome_options(user_data_dir=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", False)
    options.add_argument('--enable-logging')  # 启用控制台日志
    options.add_argument('--new-tab')  # 在新标签页中打开网页
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    return options



class BilBil(object):
    def __init__(self):
        user_data_dir = r'C:\Users\Joshua\Desktop\User Data'  # 修改为你自己的目录
        options = set_chrome_options(user_data_dir)
        self.browser = webdriver.Chrome(options=options)
        options.add_argument('--new-tab')
        # self.browser.maximize_window()
        self.wait = WebDriverWait(self.browser, 30)
        self.url = "https://www.bilibili.com/appeal/?avid=1555964834"
        self.cap = captcha.TextSelectCaptcha()

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
        url = "https://www.bilibili.com/appeal/?avid=1555964834"
        self.browser.get(url)
        xpath = '/html/body/div/div/div[3]/div[2]/textarea'
        self.wait.until(EC.presence_of_element_located(
            (By.XPATH, xpath))).send_keys('Python')
        xpath = '/html/body/div/div/div[2]/div[1]/div[2]/div[1]/div'
        self.click(xpath)
        xpath = '/html/body/div/div/div[5]/div[2]'
        self.click(xpath)



        time.sleep(2)
        xpath = '//*[@class="geetest_item_wrap"]'
        logo = self.wait.until(EC.presence_of_element_located(
        (By.XPATH, xpath)))
        # 获取图片路径
        f = logo.get_attribute('style')
        url = re.findall('url\("(.+?)"\);', f)

        if url:
            url = url[0]
            print(url)
            content = requests.get(url).content
            #送入模型识别
            plan = self.cap.run(content)
            # 获取验证码坐标
            X, Y = self.get_location(logo)
            print(X,Y,"图片左上角坐标")
            # 前端展示对于原图的缩放比例
            lan_x = 306/334
            lan_y = 343/384
            for crop in plan:
                x1, y1, x2, y2 = crop
                x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                print(x, y,"偏移前坐标")
                print(X+x * lan_x, Y+y * lan_y, "点击坐标")
                ActionChains(self.browser).move_by_offset(X + x*lan_x, Y + y*lan_y).click().perform()
                print(X + x*lan_x,Y + y*lan_y)
                ActionChains(self.browser).move_by_offset(-(X + x*lan_x), -(Y + y*lan_y)).perform()  # 将鼠标位置恢复到移动前
                time.sleep(0.5)
            xpath = "/html/body/div[3]/div[2]/div[6]/div/div/div[3]/a/div"
            self.click(xpath)

            try:
                time.sleep(1)
                xpath = "/html/body/div[3]/div[2]/div[6]/div/div/div[3]/div/a[2]"
                self.click(xpath)
                sign = False
            except:
                sign = True
        else:
            print("error: 未获得到验证码地址")
            # draw(content, res)
            sign = False

        return sign


if __name__ == '__main__':
    jd = BilBil()
    s = jd.bibi()