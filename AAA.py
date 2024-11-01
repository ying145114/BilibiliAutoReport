from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
from src import jy_click
import argparse
import requests
import zipfile
import shutil
import time
import sys
import os
import re
from urllib import request

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="�û���")
parser.add_argument("-p", "--password", help="����")
args = parser.parse_args()

if args.username and args.password:
    username = args.username
    password = args.password

    url = 'https://github.com/ayyayyayy2002/BilibiliAutoReport/releases/download/V4.0.0/default.zip'

    request.urlretrieve(url, 'default.zip')

    # ���ļ�����д���ڴ��е� BytesIO ����
    zip_file = zipfile.ZipFile('default.zip', 'r')

    # ��ѹ���ļ����ű�����Ŀ¼
    current_dir = os.path.dirname(os.path.abspath(__file__))
    extract_dir = os.path.join(current_dir, 'extracted')

    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # �����ѹ�ļ��������������ļ�����������
    for file in zip_file.namelist():
        try:
            filename = file.encode('cp437').decode('gbk')
            if filename.startswith('�����ļ�/') and filename.endswith('/'):
                zip_file.extract(file, extract_dir)
                os.rename(os.path.join(extract_dir, file), os.path.join(extract_dir, filename))
        except UnicodeDecodeError:
            pass

    # ���ƽ�ѹ��ġ������ļ����ļ��е���ǰĿ¼
    src_dir = os.path.join(extract_dir, '�����ļ�')
    dest_dir = os.path.join(current_dir, '�����ļ�')
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)



else:
    username = 'username'
    password = 'password'


def get_location(target):
    # ��ȡԪ������Ļ�ϵ�λ����Ϣ
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


proxies = {'http': None, 'https': None}
base_dir = os.path.dirname(os.path.abspath(__file__))
user_data_dir = os.path.join(base_dir, '�����ļ�', 'User Data')
chrome_binary_path = os.path.join(base_dir, '�����ļ�', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '�����ļ�', '��������', 'chromedriver.exe')
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')  # �����û�����Ŀ¼
options.binary_location = chrome_binary_path  # ָ�� Chrome ������Ŀ�ִ���ļ�·��
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
if args.password and args.username:
    options.add_argument("--headless")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  #���û���
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # ���� Chrome �����
driver.set_window_size(1000, 700)  # ������������ڴ�С�����, �߶ȣ�
#driver.set_window_position(0, 0)  # �������������λ�ã�x, y��

url = f"https://space.bilibili.com/"
driver.get(url)
if args.password and args.username:

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input'))
    )
    input_element.send_keys(username)

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input'))
    )
    input_element.send_keys(password)

    while True:
        # ���ȷ��
        WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]'))
        ).click()

        # ���Ԫ���Ƿ����
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            print("��֤��Ԫ���ѳ��֣�")
            break  # ���Ԫ�س������˳�ѭ��
        except Exception:
            print("��֤��Ԫ��δ���֣����µ��ȷ��...")

    while True:
        try:
            img = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            f = img.get_attribute('style')
            attempt = 0  # ��ʼ�����Լ���
            while ('url("' not in f) and (attempt < 10):
                f = img.get_attribute('style')
                attempt += 1
                time.sleep(0.5)
            print(attempt)
            url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)

            content = requests.get(url, proxies=proxies, timeout=(5, 10)).content

            plan = jy_click.JYClick().run(content)

            print(plan)

            a, b = get_location(img)
            lan_x = 306 / 334
            lan_y = 343 / 384

            for crop in plan:
                x1, y1, x2, y2 = crop
                x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
                print(a + x * lan_x, b + y * lan_y, "�������")

                # ִ�е������
                ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
                ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                    -(b + y * lan_y)).perform()  # �ָ����λ��
                time.sleep(0.3)

            try:  # ִ�е��ȷ�ϰ�ť�Ĳ���
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
                )
                element.click()  # �ύ��֤��
            except Exception as e:
                print(f"�ύ��֤��ʱ��������: {e}")
                refresh_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_refresh'))
                )
                refresh_element.click()  # ���ˢ����֤��ť
                print('�ѵ��ˢ�°�ť')

            try:  # �ȴ� 'geetest_item_wrap' Ԫ����ʧ����ʾ��֤���ύ�ɹ�
                WebDriverWait(driver, 3).until(
                    EC.invisibility_of_element_located(
                        (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                )
                print("��֤������ʧ��")
                break




            except Exception as e:
                print(f"��֤����֤ʧ�ܣ�������: {e}")



        except Exception as e:
            print(f"�˻���֤ѭ����������: {e}")
            # log_error(f"�˻���֤ѭ����������: {e}")
            sys.exit('�˻���֤ѭ������')  # ��������쳣Ҳ�˳�����
    driver.quit()

else:
    input("�� Enter ���ر������...")  # ͨ������������������ر�

driver.quit()  # �ر������
