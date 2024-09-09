import requests
from lxml import html
import os

# 获取页面内容
url = "https://proxycompass.com/cn/free-proxies/asia/china/"
response = requests.get(url)

if response.status_code == 200:
    tree = html.fromstring(response.content)
    script_text = tree.xpath('//*[@id="proxylister-js-js-extra"]/text()')[0]

    # 提取nonce值
    start_index = script_text.find('"nonce":"') + len('"nonce":"')
    end_index = script_text.find('"', start_index)
    nonce_value = script_text[start_index:end_index]

    # 替换链接中的nonce变量值
    download_url = "https://proxycompass.com/wp-admin/admin-ajax.php?action=proxylister_download&nonce={}&format=txt&filter={{}}".format(nonce_value)

    # 发起GET请求并下载文件
    response = requests.get(download_url)

    if response.status_code == 200:
        # 保存文件
        file_path = os.path.join("附加文件", "proxy.txt")

        with open(file_path, "wb") as file:
            file.write(response.content)

        print("文件已成功下载并保存到:", file_path)
    else:
        print("无法下载文件。状态码:", response.status_code)
else:
    print("无法获取网页内容。状态码:", response.status_code)