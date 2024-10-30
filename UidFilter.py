import requests
import os



base_dir = os.path.dirname(os.path.abspath(__file__))
cloud_whitelist_filename = '附加文件/云端文件/whitelist.txt'
uid_path = os.path.join(base_dir, '附加文件','数据文件','uid.txt')
proxies = {'http': None, 'https': None}
categories = {
    "色情游戏": {
        "关键词": ["SLG", "ACT", "RPG", "黄油","ADV", "GAL","动态","汉化","步兵","无码"],
        "权重": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    },
    "色情同人": {
        "关键词": ["AKT", "同人", "大佬", "vicineko", "新作"],
        "权重": [1, 1, 1, 1, 1]
    },

}




with open(uid_path, 'r', encoding='utf-8') as f:
    uids = f.readlines()

for uid in uids:
    uid = uid.strip()  # 去掉换行符和空格
    if uid:  # 确保 uid 非空
        search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=100'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            print(uid)
            response = requests.get(search_url, headers=headers, proxies=proxies, timeout=(5, 10))
            response.raise_for_status()
            data = response.json()

            if data['code'] == 0 and 'data' in data and 'archives' in data['data']:
                titles = [archive['title'] for archive in data['data']['archives']]
                titles_str = ', '.join(titles)
                n = len(titles)


                # 调用标记函数

                titles = titles_str.split('|||')  # 这里使用 '|||' 作为分隔符
                if len(titles) > n:
                    titles = titles[:n]  # 只取前n个标题

                scores = {category: 0 for category in categories}

                # 统计每个类别的得分
                total_score = 0

                for title in titles:
                    for category, info in categories.items():
                        keywords = info["关键词"]
                        points = info["权重"]

                        for keyword, point in zip(keywords, points):
                            count = title.count(keyword)
                            if count > 0:
                                category_score = count * point
                                scores[category] += category_score
                                total_score += category_score

                # 对账号进行分类

                labels = []
                for category, score in scores.items():
                    if total_score > 0 and (score / n) > 1:
                        labels.append(category)
                        print(f'{uid}:{labels}')
                        with open(cloud_whitelist_filename, 'a', encoding='utf-8') as f:
                            f.write(f"\n{uid}")






        except Exception as e:
            print(f"Error processing UID {uid}: {e}")

        # 在处理全部 uid 后

with open(cloud_whitelist_filename, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 去除每行末尾的换行符，并将内容转换为整数，仅处理非空行
numbers = []
for line in lines:
    stripped_line = line.strip()
    if stripped_line:  # 确保不是空行
        try:
            numbers.append(int(stripped_line))
        except ValueError:
            print(f"警告: '{stripped_line}' 不是有效的整数，已跳过。")

# 排序
sorted_numbers = sorted(numbers)

# 将排序后的结果写回文件
with open(cloud_whitelist_filename, 'w', encoding='utf-8') as file:
    for number in sorted_numbers:
        file.write(f"{number}\n")

# 将文件 A 的内容覆盖到文件 B
with open(cloud_whitelist_filename, 'r', encoding='utf-8') as file_a:
    content_a = file_a.read()

# 将文件 A 的内容覆盖到文件 B
with open(uid_path, 'w', encoding='utf-8') as file_b:
    file_b.write(content_a)
exit(0)