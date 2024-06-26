

from selenium import webdriver


def set_chrome_options(user_data_dir=None):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    options.add_argument('--enable-logging')  # 启用控制台日志
    options.add_argument('--unexpectedAlertBehaviour=dismiss')
    if user_data_dir:
        options.add_argument(f'--user-data-dir={user_data_dir} ')
        options.add_argument('--unexpectedAlertBehaviour=dismiss')
        # 设置用户数据目录
    return options


def main():

    # 设置用户数据目录，如果不需要可以设为 None
    user_data_dir = r'D:\BilibiliAutoReport\User Data'  # 修改为你自己的目录
    options = set_chrome_options(user_data_dir)

    driver = webdriver.Chrome(options=options)
    url = f"https://space.bilibili.com/"
    driver.get(url)
if __name__ == "__main__":
    main()
