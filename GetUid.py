from urllib.parse import urlencode
from bs4 import BeautifulSoup
import requests
import datetime
import shutil
import os


proxies = {'http': None,'https': None}
output_file = os.path.join(os.getcwd(), '附加文件/uid.txt')
whitelist_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/whitelist.txt'
whitelist_filename = '附加文件/whitelist.txt'
blacklist_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/blacklist.txt'
blacklist_filename = '附加文件/blacklist.txt'
if os.path.exists(output_file):
    os.remove(output_file)
else:
    print(f"文件 {output_file} 不存在，无需删除。")



def fetch_keywords():# 定义获取关键词的函数
    keywords_url = 'https://raw.kkgithub.com/ayyayyayy2002/BiliBiliVideoAutoReport/main/云端文件/keyword.txt'  # 替换为实际的GitHub URL
    keywords_filename = '附加文件/keyword.txt'


    try:
        response = requests.get(keywords_url, proxies=proxies, timeout=(5, 10))
        if response.status_code == 200:
            with open(keywords_filename, 'wb') as f_out:
                f_out.write(response.content)
            print(f"成功下载关键词文件 {keywords_url} 并保存为 {keywords_filename}")
        else:
            print(f"无法访问 {keywords_url}，状态码：{response.status_code}")
            return load_local_keywords(keywords_filename)  # 返回本地关键词
    except requests.exceptions.RequestException as e:
        print(f"下载关键词文件时发生请求异常：{e}")
        return load_local_keywords(keywords_filename)  # 返回本地关键词

    return load_local_keywords(keywords_filename)


def load_local_keywords(filename):# 定义从本地文件加载关键词的函数
    keywords = []
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith('#'):  # 排除空行和以“#”开头的行
                    keywords.append(stripped_line)
    else:
        print(f"本地关键词文件 {filename} 不存在。")

    return keywords


def search_and_extract_uid(keyword):# 定义搜索函数
    base_url = 'https://search.bilibili.com/video?'
    search_params_list = [
        {
            'keyword': keyword,
            'from_source': 'video_tag',
        },
        {
            'keyword': keyword,
            'from_source': 'video_tag',
            'page': '2',
            'o': '30'
        },
        {
            'keyword': keyword,
            'from_source': 'video_tag',
            'order': 'pubdate'
        }
    ]


    for search_params in search_params_list:
        search_url = base_url + urlencode(search_params)
        print(search_url)


        try:
            # 添加头部信息
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/91.0.4472.124 Safari/537.36',
            }
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            response.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(response.text, 'html.parser')
            uid_list = []
            count = 0  # 计数器，用于限制获取的UID数量
            for link in soup.select('.bili-video-card .bili-video-card__info--owner'):
                if count >= 10:
                    break
                href = link['href']
                uid = href.split('/')[-1]  # 获取链接中最后的数字部分作为UID
                uid_list.append(uid)
                count += 1
            process_uid_list(keyword, uid_list)
        except requests.exceptions.RequestException as e:
            print(f"关键词 \"{keyword}\" 搜索页面请求失败：", e)


def process_uid_list(keyword, uid_list):# 定义处理UID列表的函数（追加写入同一文件）
    print(f" \"{keyword}\" UID：", uid_list)

    # 将UID列表追加写入文件
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f" \"{keyword}\" UID：\n")
        for uid in uid_list:
            f.write(uid + '\n')
        f.write('\n')  # 添加空行分隔每个关键词的UID列表


def main():# 主函数，循环运行搜索和处理
    while True:
        unique_uids = set()  # 使用集合存储唯一的 UID
        keywords = fetch_keywords()  # 使用fetch_keywords函数替代原有的keywords定义


        for keyword in keywords:# 遍历关键词列表，进行搜索和处理
            search_and_extract_uid(keyword)
        print('读取当前文件中所有的 UID，并添加到集合中去重')
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                uid = line.strip()
                if uid.isdigit():  # 假设 UID 是数字格式
                    unique_uids.add(uid)

        try:
            # 获取当前时间并格式化
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f'附加文件/UID记录/{timestamp}.txt'

            shutil.copy('附加文件/uid.txt', backup_filename)
            print(f"成功保存备份：{backup_filename}")
        except IOError as e:
            print(f"复制保存备份时发生错误：{e}")


        try:
            response = requests.get(whitelist_url, proxies=proxies, timeout=(5, 10))
            if response.status_code == 200:
                with open(whitelist_filename, 'wb') as f_out:
                    f_out.write(response.content)
                print(f"成功下载文件 {whitelist_url} 并保存为 {whitelist_filename}")
            else:
                print(f"无法访问 {whitelist_url}，状态码：{response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"下载文件时发生请求异常：{e}")
        except IOError as e:
            print(f"文件操作发生错误：{e}")
        except Exception as e:
            print(f"发生未知错误：{e}")


        with open(whitelist_filename, 'r', encoding='utf-8') as f:# 处理 whitelist_file
            lines = f.readlines()
            for line in lines:
                uid = line.strip()
                if uid.isdigit():  # 假设 UID 是数字格式
                    unique_uids.add(uid)


        try:
            response = requests.get(blacklist_url, proxies=proxies, timeout=(5, 10))
            if response.status_code == 200:
                with open(blacklist_filename, 'wb') as f_out:
                    f_out.write(response.content)
                print(f"成功下载文件 {blacklist_url} 并保存为 {blacklist_filename}")
            else:
                print(f"无法访问 {blacklist_url}，状态码：{response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"下载文件时发生请求异常：{e}")
        except IOError as e:
            print(f"文件操作发生错误：{e}")
        except Exception as e:
            print(f"发生未知错误：{e}")
        print('继续执行其他操作，不受文件下载错误的影响')
        exclude_uids = set()


        with open(blacklist_filename, 'r', encoding='utf-8') as exclude_file:
            exclude_lines = exclude_file.readlines()
            for line in exclude_lines:
                exclude_uid = line.strip()
                if exclude_uid.isdigit():  # 假设 UID 是数字格式
                    exclude_uids.add(exclude_uid)
        print('从 unique_uids 中移除在 exclude_uids 中存在的 UID')
        unique_uids -= exclude_uids
        print('将唯一的 UID 列表按格式写入文件')


        with open(output_file, 'w', encoding='utf-8') as f:
            for uid in unique_uids:
                f.write(uid + '\n')
        print('关键词搜索和UID全部处理完成')
        exit(0)




if __name__ == "__main__":
    main()
