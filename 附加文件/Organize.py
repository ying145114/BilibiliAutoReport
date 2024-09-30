import json
import os
from time import sleep
import requests


def get_name_by_uid(uid, output_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    search_url = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"

    try:
        # 发起HTTP GET请求获取用户信息
        response = requests.get(search_url, headers=headers, timeout=(5, 10))
        response.raise_for_status()  # 检查请求是否成功

        print(response.text)
        sleep(1.5)

        # 加载JSON响应数据
        data = json.loads(response.text)

        # 提取并返回名称
        name = data["data"]["card"]["name"]

        # 动态写入文件
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{uid}\n#{name}\n")

    except Exception as e:
        print(f"获取UID {uid} 的名称时发生错误: {e}")

        # 在出现错误时也将UID写入输出文件
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{uid}\n#未能获取名称\n")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir,  'uid.txt')  # uid.txt在附加文件文件夹下
    output_file = os.path.join(base_dir,  'organized.txt')  # organized.txt也在附加文件夹下
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(input_file, 'r') as f:
        uids = f.read().splitlines()

    # 清空或创建输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        pass  # 创建或清空文件

    # 使用utf-8编码读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        uids = f.read().splitlines()

    for uid in uids:
        get_name_by_uid(uid, output_file)

    print(f"UID与名称已写入 {output_file}.")


if __name__ == "__main__":
    main()
