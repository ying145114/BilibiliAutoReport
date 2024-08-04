from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def set_chrome_options(user_data_dir=None, chrome_binary_path=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir}')  # 设置用户数据目录
    if chrome_binary_path:
        options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
    return options


def main():
    print('设置用户数据目录')
    user_data_dir = r'D:\BilibiliAutoReport\User Data'  # 修改为你自己的目录
    print('设置 Chrome 可执行文件路径')
    chrome_binary_path = r'D:\BilibiliAutoReport\chrome-win\chrome.exe'  # 修改为你自己 Chrome 的可执行文件路径

    # 确保自定义的 ChromeDriver 路径也是正确的
    chrome_driver_path = r'D:\BilibiliAutoReport\chromedriver.exe'  # 替换为你的 chromedriver 路径

    options = set_chrome_options(user_data_dir, chrome_binary_path)
    print('启动浏览器')

    # 使用 Service 来指定 ChromeDriver 的路径
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    url = f"https://space.bilibili.com/"
    driver.get(url)




if __name__ == "__main__":
    main()
