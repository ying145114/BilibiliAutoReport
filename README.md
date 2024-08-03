# Bilibili视频全自动举报———我能跑一整天！  
# BilibiliVideoAutoReport———I can do this all day!
20240803更新  
**推荐使用方法（可能仅限Windows，需要下载PyCharm）** 
1，下载安装[PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC)  
2，按照[教程](https://www.bing.com/search?q=PyCharm%E5%AE%89%E8%A3%85%E6%B1%89%E5%8C%96%E6%95%99%E7%A8%8B)安装和汉化PyCharm  
3，下载Relaease，解压至D盘  
4，在Pycharm中打开“D:\BilibiliAutoReport”文件夹，在软件的最上方会有一个绿色三角形，点击可以运行指定文件，用左边向下的三角来切换脚本  
5，脚本解释：AAA可以打开浏览器进行配置，并测试Bilibili是否登录成功，Getuid用于运行搜索+举报功能，Report仅会举报当前文件内的uid  
6，先运行AAA，在打开的浏览器中[登录Bilibili](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E7%99%BB%E5%BD%95%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9)，并[安装油猴脚本](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E5%AE%89%E8%A3%85%E6%B2%B9%E7%8C%B4%E8%84%9A%E6%9C%AC)  
7，双击上方红色按钮关闭脚本，点击左边向下三角，切换并运行Getuid  
8，脚本已运行  


**不推荐使用方法（可能仅限Windows）**   
1，下载Relaease，解压至D盘  
2，进入“D:\BilibiliAutoReport”文件夹，在地址栏输入“cmd”，回车后会出现一个命令窗口  
3，在窗口中输入：  
```cmd
venv\Scripts\activate
```
这将进入Python虚拟环境  
4，继续输入  
```cmd
python AAA.py
```
在打开的浏览器窗口内登录BiliBili账号，并安装篡改猴和两个油猴脚本  
5，在命令窗口使用“Ctrl+C”关闭浏览器，在命令窗口中继续输入  
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
6，每秒50进行一次人机验证，并检查一次举报进度  
  
**目前问题**  
1，采用关键词搜索寻找目标的方法容易误杀，将在未来采取更好的方法来避免  
2，B站似乎会包庇粉丝量高的账号，比如[这位](https://space.bilibili.com/452078996/video)，还有某些特殊的账号比如[这位](https://space.bilibili.com/3546674746100411/video)  


**引用信息**  
1，项目中过人机验证的代码来自于[MgArcher/Text_select_captcha: 实现文字点选、选字、选择、点触验证码识别，基于pytorch训练](https://github.com/MgArcher/Text_select_captcha/)，感谢大佬  
2，油猴脚本的手动版在[这里](https://greasyfork.org/zh-CN/scripts/497079-bilibili%E7%A8%BF%E4%BB%B6%E6%89%B9%E9%87%8F%E4%B8%BE%E6%8A%A5)  
3，ChromeDriver的[官方下载地址](https://developer.chrome.com/docs/chromedriver?hl=zh-cn)  


  
**甲级战犯展示**  
![3546674746100411](/逆天账号截图/3546674746100411.png "3546674746100411")  
![452078996](/逆天账号截图/452078996.png "452078996")  

