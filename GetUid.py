import os
import time
import subprocess
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

# 定义搜索关键词列表
keywords = [
    '安卓 直装',
    '原神 同人',
    'SLG',
    '自取',
    'GAL',
    'RPG',
    '三连关注',
    '月入',
    '本子',
    '黄油'

    # 可以根据需要添加更多关键词
]

# 文件路径和文件名
output_file = os.path.join(os.getcwd(), 'uid.txt')


# 定义搜索函数
def search_and_extract_uid(keyword):
    # 构建搜索链接
    base_url = 'https://search.bilibili.com/video?'
    search_params = {
        'keyword': keyword,
        'from_source': 'webtop_search',
        'order': 'pubdate'
    }
    search_url = base_url + urlencode(search_params)

    try:
        # 添加头部信息
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        # 发起HTTP GET请求获取搜索结果页面内容
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 使用BeautifulSoup加载HTML内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 存储解析出的UID列表
        uid_list = []

        # 使用CSS选择器定位搜索结果的链接，并提取UID
        for link in soup.select('.bili-video-card .bili-video-card__info--owner'):
            href = link['href']
            uid = href.split('/')[-1]  # 获取链接中最后的数字部分作为UID
            uid_list.append(uid)

        # 将UID列表传递给处理函数（这里假设是process_uid_list函数）
        process_uid_list(keyword, uid_list)

    except requests.exceptions.RequestException as e:
        print(f"关键词 \"{keyword}\" 搜索页面请求失败：", e)


# 定义处理UID列表的函数（追加写入同一文件）
def process_uid_list(keyword, uid_list):
    print(f"关键词 \"{keyword}\" 的UID列表：", uid_list)

    # 将UID列表追加写入文件
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"关键词 \"{keyword}\" 的UID列表：\n")
        for uid in uid_list:
            f.write(uid + '\n')
        f.write('\n')  # 添加空行分隔每个关键词的UID列表

    print(f"关键词 \"{keyword}\" 的UID列表已追加至文件: uid.txt")


# 主函数，循环运行搜索和处理
def main():
    while True:
        for keyword in keywords:
            search_and_extract_uid(keyword)

        # 所有关键词搜索和处理完成后，通过虚拟机在指定路径运行 report.py
        report_script = r"D:\BiliBiliAutoReport\venv\Scripts\python.exe D:\BiliBiliAutoReport\Report.py"
        try:
            subprocess.run(report_script, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"report.py 执行错误: {e}")

        # 等待 report.py 执行完成
        # 监控 report.py 进程是否结束
        report_process = subprocess.Popen(report_script, shell=True)

        while report_process.poll() is None:
            time.sleep(1)  # 等待1秒钟

        # 清空当前的 UID 文件，准备下一轮搜索
        with open(output_file, 'w') as f:
            f.write('')  # 清空文件内容


if __name__ == "__main__":
    main()
