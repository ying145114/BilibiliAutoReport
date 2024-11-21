import requests
uid='3546778238454421'
search_url = f'https://api.bilibili.com/x/polymer/space/seasons_series_list?mid=3546778238454421&page_num=1&page_size=20'
headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
response = requests.get(search_url, headers=headers, timeout=(5, 10))
data = response.json()
print(response.text)
seasons_list = data.get('data', {}).get('items_lists', {}).get('seasons_list', [])

if data.get('data', {}).get('items_lists', {}).get('seasons_list', []) :
    first_video = data['data']['items_lists']['seasons_list'][0]['archives'][0]
    aid = first_video.get('aid')
    title = first_video.get('title')
    print(f"UID:{uid},  AID: {aid}, 标题: {title}")

else:
    print('aaaa')