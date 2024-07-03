# BiliBili全自动举报———我能跑一整天！  
# BiliBiliAutoReport———I can do this all day!  


**使用方法（应该仅限Windows）**  
1,安装Chrome  
2，下载Relaease，解压至D盘  
3，下载对应版本的ChromeDriver驱动，放在项目文件夹里  
4，进入“D:\BilibiliAutoReport”文件夹，在地址栏输入“cmd”，回车后会出现一个命令窗口  
5，在窗口中输入：  
```cmd
venv\Scripts\activate
```
这将进入Python虚拟环境  
6，继续输入  
```cmd
python AAA.py
```
在打开的浏览器窗口内登录BiliBili账号，并安装篡改猴和油猴脚本  
6，关闭浏览器，在命令窗口中继续输入  
```cmd
python GetUid.py
```
命令窗口将开始输出关键词搜索情况，程序成功运行。  

**程序逻辑**   
1，GetUid使用代码所提供的关键词进行搜索，从返回页面抓取uid，并将uid和关键词写入文件保存  
2，读取所有uid，去重，过排除列表，重新写入文件  
3，启动Report进行举报，如果中途出错将重新启动Report，如果运行结束则重新运行搜索  
4，Report脚本读取uid，逐个调用油猴脚本进行举报，举报完成后删除该uid  
5，油猴脚本会自动运行，跳转到该UP主投稿的最后一页向前举报  
6，每60秒进行一次人机验证，并检查一次举报进度  
**目前问题** 
1，采用关键词搜索寻找目标的方法容易误杀，将在未来采取更好的方法来避免  
2，B站似乎会包庇粉丝量高的账号，比如[这位](https://space.bilibili.com/452078996/video)，还有某些特殊的账号比如[这位](https://space.bilibili.com/3546674746100411/video)  


**引用信息**  
1，项目中过人机验证的代码来自于[MgArcher/Text_select_captcha: 实现文字点选、选字、选择、点触验证码识别，基于pytorch训练](https://github.com/MgArcher/Text_select_captcha/)，感谢大佬  
2，油猴脚本的手动版在[这里](https://greasyfork.org/zh-CN/scripts/497079-bilibili%E7%A8%BF%E4%BB%B6%E6%89%B9%E9%87%8F%E4%B8%BE%E6%8A%A5)  
3，ChromeDriver的[官方下载地址](https://developer.chrome.com/docs/chromedriver?hl=zh-cn)  
