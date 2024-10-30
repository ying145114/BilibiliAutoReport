import json
import os
from time import sleep
import requests


def get_name_by_uid(uid, output_file, blacklist_file):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    search_url = f"https://api.bilibili.com/x/web-interface/card?mid={uid}"

    try:
        # 发起HTTP GET请求获取用户信息
        response = requests.get(search_url, headers=headers, timeout=(5, 10))
        response.raise_for_status()  # 检查请求是否成功

        print(response.text)
        sleep(0.1)

        # 加载JSON响应数据
        data = json.loads(response.text)

        # 提取名称
        name = data["data"]["card"]["name"]

        # 检查名字是否为“账号已注销”
        if name == "账号已注销":
            with open(blacklist_file, 'a', encoding='utf-8') as bf:
                bf.write(f"\n{uid}")  # 添加到黑名单文件，并在前面加上换行符
        else:
            # 动态写入正常输出文件
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"{uid}\n#{name}\n")

    except Exception as e:
        print(f"获取UID {uid} 的名称时发生错误: {e}")

        # 在出现错误时也将UID写入输出文件
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(f"{uid}\n#未能获取名称\n")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, 'uid.txt')  # uid.txt在附加文件文件夹下
    output_file = os.path.join(base_dir, 'organized.txt')  # organized.txt也在附加文件夹下
    blacklist_file = os.path.join(base_dir, 'blacklist.txt')  # black_list在云端文件文件夹下

    if os.path.exists(output_file):
        os.remove(output_file)

    if not os.path.exists(os.path.dirname(blacklist_file)):
        os.makedirs(os.path.dirname(blacklist_file))  # 确保云端文件文件夹存在

    with open(input_file, 'r', encoding='utf-8') as f:
        uids = [line.strip() for line in f if not line.startswith('#')]

    # 清空或创建输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        pass  # 创建或清空文件

    for uid in uids:
        if uid:  # 确保UID不为空
            get_name_by_uid(uid, output_file, blacklist_file)

    print(f"UID与名称已写入 {output_file}，黑名单已更新至 {blacklist_file}.")


if __name__ == "__main__":
    main()
