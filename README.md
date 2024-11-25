# BilibiliAutoReport  
## 使用[关键词](https://github.com/ayyayyayy2002/BilibiliAutoReport/blob/main/%E4%BA%91%E7%AB%AF%E6%96%87%E4%BB%B6/keyword.txt)搜索视频，举报作者的头像、签名、昵称、视频、专栏和动态  
## 注意：本仓库有两个分支：[main](https://github.com/ayyayyayy2002/BilibiliAutoReport/tree/main)分支是开发者自用分支，[public](https://github.com/ayyayyayy2002/BilibiliAutoReport/tree/public)分支是公开的完整可运行代码  
## 使用条款与免责声明
本项目是开源的，遵循以下条款和条件。请在使用本项目之前仔细阅读。
1. **无保证**：本项目以“现状”提供，不附带任何形式的明示或暗示保证，包括但不限于对适销性、特定用途适用性及不侵权的保证。  
2. **风险自担**：使用本项目过程中可能出现的问题或损失，使用者需自行承担所有风险。我们不对因使用本项目而引起的任何直接、间接、惩罚性或偶然的损害负责。此项目供仅学习使用，切勿用于违规操作。请于下载后24小时内删除。
3. **维护责任**：开发者不承诺对本项目的更新、维护或支持，用户应自行评估项目的适用性。

## 写在前面————前言🤓☝️ 
**20240907更新：**  
一切都开始于某个中午，似乎是去年的我在家刷B站时被推广黄油的视频烦破防了，在Google上搜索了“Bilibili批量举报”，在一个中文论坛上找到了这个[bilibili批量举报【高危脚本】-油猴中文网](https://bbs.tampermonkey.net.cn/thread-5222-2-1.html)，下完后发现用不了。  
我当时上大四，学的软件工程，代码一点不会，完成课设全靠网上找项目，油猴脚本是用JavaScript写的，我一窍不通。只能把代码发给AI，描述需求，提供报错。当天下午脚本就完成了。  
最初B站还没有对举报频率进行限制，我甚至可以开多个窗口，同时举报多个UP，有的人甚至一天之内稿件被下架清空。大概过了一个月后，B站加了举报频率限制，举报频率过快会封禁IP，开个代理或者等一段时间就能解决问题。  
人机验证是一直都有的，每个账号每天可以免验证举报几十次，后续每60秒一次人机验证。  
当时还没有制作全自动脚本的打算。直到后来我买了个玩客云的小盒子，我发现青龙可以定时运行各种脚本。  
整个程序花了大概三天，全是用ChatGPT写的，先是用关键词获取违规视频，再获取发布违规视频的账号。后来发现用Selenium重写举报过程太麻烦，就直接把油猴脚本改了一下，安装到测试浏览器上。  
真正运行起来时才发现有人机验证，只能去找过人机验证的项目，再把项目融合进程序里，写好人机验证的循环。每天就是运行、发现问题、解决问题、运行然后发现新问题。好在当时毕设已经完事了，我有足够的时间。毕设也是用ChatGPT写的。  
今天是2024年9月7号，放假，可以写点东西。前两天刚发现B站采用了新机制，运行在测试浏览器上的小号过不了人机验证，开代理后恢复正常，运行在常用浏览器上的大号一切正常，切换到小号也一切正常。初步的解决方案是在代码里加个请求代理的脚本，吧找到的代理存起来，每次运行浏览器时随机用一个代理，运行完成后把代理删除。具体怎么办等我先测试一下详细的机制。  
B站也是离谱，发现举报变多了，不去治理被举报目标，反而开始阻止用户举报......   
  
**20241022更新：**  
前两天发现了新的api，可以请求到已注销账号的视频aid，另外B站似乎取消了对举报请求频率的限制，就修改了一下程序  
今天跑脚本时发现电脑挺热的，开了任务管理器发现PyCharm占用了很大一部分资源，找ChatGPT要了个bat脚本来解决这个问题，现在项目可以使用bat脚本直接启动了    

**20241022更新：**  
牢B再次收紧风控，我重写了GetUid和Report的逻辑，调整举报间隔为2500ms，程序会根据每轮的举报结果决定进行人机验证还是开始下一个UID  
使用Pyinstaller打包了EXE文件，现在可以开袋即食了  

## 开袋即食（仅限Windows）😋   
1，前往[public](https://github.com/ayyayyayy2002/BilibiliAutoReport/tree/public)分支下载程序   
2，前往[Release](https://github.com/ayyayyayy2002/BilibiliAutoReport/releases)页面下载驱动，并解压后将”附加文件“文件夹合并  
3，双击AAA.exe，在打开的浏览器窗口登录账号。关闭浏览器，双击Start.exe，程序将自动开始运行  

## 源码使用方法（仅限Windows，可能需要下载PyCharm）🐍 
1，前往[public](https://github.com/ayyayyayy2002/BilibiliAutoReport/tree/public)分支下载程序   
2，前往[Release](https://github.com/ayyayyayy2002/BilibiliAutoReport/releases)页面下载驱动，并解压后将”附加文件“文件夹合并  
2，下载安装[Python3.10](https://www.python.org/downloads/release/python-3100/)
  
<details>
<summary>不使用Pycharm： </summary>
  
 - 3a.1，进入解压后的文件夹，双击打开“启动脚本”，双击运行“安装依赖.bat”，等待运行结束   
 - 3a.2，双击运行“AAA.bat”，在打开的浏览器里登陆账号，然后关闭窗口  
 - 3a.3，双击运行”Start.bat“  
</details>
  
<details>
<summary>使用Pycharm：</summary>  
  
 - 3b.1，下载安装[PyCharm](https://www.jetbrains.com/pycharm/download/download-thanks.html?platform=windows&code=PCC)  
 - 3b.1，按照[教程](https://www.bing.com/search?q=PyCharm%E5%AE%89%E8%A3%85%E6%B1%89%E5%8C%96%E6%95%99%E7%A8%8B)安装和汉化PyCharm  
 - 3b.3，在Pycharm中打开源码文件夹，在软件的左侧是项目文件，右键点击指定文件，选择”运行“    
 - 3b.4，先运行AAA，在打开的浏览器中[登录Bilibili](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E7%99%BB%E5%BD%95%E5%93%94%E5%93%A9%E5%93%94%E5%93%A9)，并[安装油猴脚本](https://www.bing.com/search?q=%E5%A6%82%E4%BD%95%E5%AE%89%E8%A3%85%E6%B2%B9%E7%8C%B4%E8%84%9A%E6%9C%AC)  
 - 3b.5，关闭浏览器，点击左边向下三角，切换并运行Getuid，并查看是否成功启动浏览器  
 - 3b.6，双击红色停止按钮，彻底停止脚本，切换至Start，点击绿色三角 
</details>  
4，脚本已运行  


## 程序逻辑🧠   
1，Start.是守护进程，负责启动其他两个脚本，运行后会启动Getuid  
2，Getuid从云端加载关键词列表、黑名单和白名单，用关键词搜索得到原始列表。原始列表+白名单-黑名单后，去重，重新写入文件uid.txt  
3，处理完uid会自动启动Report进行举报，如果中途出错将重新启动Report，如果Report正常退出则重新运行Getuid获得新列表  
4，Report脚本读取uid，逐个进行举报，根据返回值决定是进行人机验证还是开始下一个uid      

## 目前问题😒  
1，采用关键词搜索寻找目标的方法容易误杀，未来可能会采取更好的方法来获取目标  
2，B站似乎会包庇粉丝量高的账号，比如[收藏夹里没东西](https://space.bilibili.com/452078996/video)，和[山海之花](https://space.bilibili.com/297993336/video)  

## 引用信息🤝  
1，项目中过人机验证的代码来自于[MgArcher/Text_select_captcha: 实现文字点选、选字、选择、点触验证码识别，基于pytorch训练](https://github.com/MgArcher/Text_select_captcha/)，感谢大佬  
2，油猴脚本版本的举报程序在[这里](https://greasyfork.org/zh-CN/scripts/497079-bilibili%E7%A8%BF%E4%BB%B6%E6%89%B9%E9%87%8F%E4%B8%BE%E6%8A%A5)  

 

