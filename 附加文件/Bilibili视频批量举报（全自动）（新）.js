// ==UserScript==
// @name         Bilibili视频批量举报（全自动）（新）
// @namespace    http://tampermonkey.net/
// @version      0.0.1
// @description  Extract mid from URL, fetch AID from Bilibili API, and submit appeals with extracted CSRF token.
// @author       Your Name
// @match        https://space.bilibili.com/*
// @grant        GM_xmlhttpRequest
// @connect      api.bilibili.com
// @exclude      https://space.bilibili.com/*/dynamic
// @exclude      https://space.bilibili.com/*/article
// @icon         https://i2.hdslb.com/bfs/app/8920e6741fc2808cce5b81bc27abdbda291655d3.png@240w_240h_1c_1s_!web-avatar-space-header.avif
// ==/UserScript==

(function() {
    'use strict';






    function sendReportRequest() {
  const mid = window.location.href.match(/bilibili.com\/(\d+)\/video/)[1];
  const csrf = getCsrf();
  const xhr = new XMLHttpRequest();
  xhr.open("POST", 'https://space.bilibili.com/ajax/report/add', true);
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhr.onload = function () {
    const decodedResponse = JSON.parse(decodeURIComponent(this.response));
    updateDiagnosticInfo(`举报请求返回值：<strong>${Object.keys(decodedResponse).map(key => `${key}: ${decodedResponse[key]}`).join(', ')}</strong><br>`);
    // Call the existing functionality after the report request with a delay

  };
  xhr.send(`mid=${mid}&reason=1%2C3%2C2&reason_v2=3&csrf=${csrf}`);
}








    function modifyRelation() {
        const currentUrl = window.location.href; // 获取当前URL
        const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);
        const mid = midMatch && midMatch[1] ? midMatch[1] : null;

        if (!mid) {
            console.error("未找到 mid");
            return;
        }

        const xhr = new XMLHttpRequest();

        // 构建数据数组
        const params = new URLSearchParams();
        params.append('fid', mid); // 将 fid 替换为 mid
        params.append('act', '1');
        params.append('re_src', '11');
        params.append('gaia_source', 'web_main');
        params.append('spmid', '333.999.0.0');
        params.append('extend_content', JSON.stringify({
            entity: "user",
            entity_id: mid,
            fp: "0\\u00012560,,1440\\u0001Win32\\u00014\\u00018\\u000124\\u00011\\u0001zh-CN\\u00010\\u00010,,0,,0\\u0001Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }));
        params.append('csrf', getCsrf());

        xhr.open("POST", "https://api.bilibili.com/x/relation/modify", true);
        xhr.setRequestHeader('Accept', '*/*');
        xhr.setRequestHeader('Accept-Language', 'zh-CN,zh;q=0.9');
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        //xhr.setRequestHeader('Origin', 'https://space.bilibili.com');
        //xhr.setRequestHeader('Referer', `https://space.bilibili.com/${mid}?spm_id_from=333.1007.tianma.1-1-1.click`);
        //xhr.setRequestHeader('User-Agent', navigator.userAgent);

        // 从浏览器获取 Cookie
        xhr.withCredentials = true; // 确保发送凭证（cookie）

        xhr.onreadystatechange = function() {
            if (xhr.readyState === 4 && xhr.status === 200) {
                updateDiagnosticInfo(xhr.responseText);
            } else if (xhr.readyState === 4) {
                updateDiagnosticInfo(`请求失败，状态码: ${xhr.status}`);
            }
        };

        xhr.send(params.toString()); // 发送参数
    }







    const floatingWindow = document.createElement('div');
floatingWindow.style.position = 'fixed';
floatingWindow.style.top = '100px';
floatingWindow.style.right = '20px';
floatingWindow.style.zIndex = '9999';
floatingWindow.style.background = 'white';
floatingWindow.style.border = '1px solid #ccc';
floatingWindow.style.padding = '10px';
floatingWindow.style.maxWidth = '340px';
floatingWindow.style.overflow = 'auto'; // Add overflow property for scrolling
floatingWindow.style.height = '200px'; // Set a height for the window
floatingWindow.style.scrollBehavior = 'smooth'; // Enable smooth scrolling
document.body.appendChild(floatingWindow);

// Create diagnostic info container
const diagnosticInfo = document.createElement('div');
floatingWindow.appendChild(diagnosticInfo);

// Function to scroll to the bottom of the floating window
function scrollToBottom() {
  floatingWindow.scrollTop = floatingWindow.scrollHeight;
  // Scroll the last element into view
  const lastElement = floatingWindow.lastElementChild;
  if (lastElement) {
    lastElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }
}

// Updating the diagnosticInfo.innerHTML with the scroll to bottom
function updateDiagnosticInfo(content) {
  diagnosticInfo.innerHTML += content;
  scrollToBottom();
}











    let reportCount = 0
    let csrfText = ''; // 用于存储CSRF token
    let currentAidIndex = 0; // 当前处理的AID索引
    let aids = []; // 所有提取的AID

    // 获取当前URL
    const currentUrl = window.location.href;

    // 从URL中提取mid
// 函数：提取AID并提交申诉
function extractAndSubmitAIDs() {
    const currentUrl = window.location.href; // 获取当前URL
    const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);

    if (midMatch && midMatch[1]) {
        const mid = midMatch[1];

        // 构造API请求URL
        const apiUrl = `https://api.bilibili.com/x/series/recArchivesByKeywords?mid=${mid}&keywords=&ps=0`;

        // 使用GM_xmlhttpRequest进行跨域请求
        GM_xmlhttpRequest({
            method: "GET",
            url: apiUrl,
            onload: function(response) {
                if (response.status === 200) {
                    try {
                        const data = JSON.parse(response.responseText);
                        if (data.code === 0 && data.data && data.data.archives) {
                            // 提取并保存所有的aid
                            aids = data.data.archives.map(archive => archive.aid); // 使用全局变量
                            console.log("Extracted AIDs:", aids);

                            // 开始提交每个AID
                            currentAidIndex = 0; // 重置索引
                            submitNextAppeal(); // 提交下一个AID
                        } else {
                            console.error("No archives found or error in response:", data);
                        }
                    } catch (e) {
                        console.error("Error parsing JSON:", e);
                    }
                } else {
                    console.error("Failed to fetch data, status:", response.status);
                }
            },
            onerror: function(err) {
                console.error("Request failed:", err);
            }
        });
    } else {
        console.warn("No valid mid found in the URL.");
    }
}


// 页面加载完成后显示按钮
window.onload = function() {
    const button = document.createElement('button');
    button.textContent = '提取并提交AID';
    button.style.position = 'fixed';
    button.style.bottom = '20px';
    button.style.right = '20px';
    button.style.zIndex = '1000'; // 确保按钮在其他元素之上
    button.onclick = extractAndSubmitAIDs; // 点击按钮时调用函数

    document.body.appendChild(button); // 将按钮添加到页面
};

    // 提取CSRF Token的函数
    function getCsrf() {
        if (csrfText === '') {
            const cook = document.cookie.match(/bili_jct=(.*?);/) ?? [];
            if (cook.length === 2) {
                csrfText = cook[1];
            }
        }
        return csrfText;
    }

    // 提交每个AID的函数
function submitAppeal(aid, csrfToken, desc) {
    return new Promise((resolve, reject) => {
        const data = new URLSearchParams({
            'aid': aid,
            'attach': '',
            'block_author': 'false',
            'csrf': csrfToken,
            'desc': desc,
            'tid': '10022' //10014
        }).toString();

        // 创建新的 XMLHttpRequest 对象
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open('POST', 'https://api.bilibili.com/x/web-interface/appeal/v2/submit');

        // 设置请求头
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
        xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

        let timeoutId = setTimeout(() => {
            console.warn(`请求超时，AID ${aid}，请检查网络连接。`);
            xhr.abort(); // 取消请求
            resolve(); // 超时后直接 resolve，跳过错误处理
        }, 3000); // 设置为3000毫秒（3秒）

        xhr.onload = function() {
            clearTimeout(timeoutId); // 收到响应后清除超时

            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                updateDiagnosticInfo(`举报结果：<strong>${this.response}</strong><br>`);

                if (result.code === -999) { // 检查返回值是否为-352
                    showContinueButton(aid);
                    window.open(`https://www.bilibili.com/appeal/?avid=${aid}`, '_blank');
                    reject(`Encountered code -352 for AID ${aid}.`); // 返回拒绝
                } else {
                    // 忽略其他状态和返回值，不做处理
                    resolve(result); // 解析其他返回结果并成功解决 Promise
                }
            } else {
                console.warn(`请求返回错误，状态码: ${xhr.status}`);
                resolve(); // 只打印警告，不做处理
            }
        };

        xhr.onerror = function(err) {
            clearTimeout(timeoutId); // 清除超时
            console.error(`请求失败，AID ${aid}:`, err);
            // 忽略请求失败的情况
        };
        //*****************************************************************************************************





        const shoucangdelayInMilliseconds = 3500
        if (reportCount % 20 === 1) { // 每20次的第一条记录
            setTimeout(() => {
                const data = new URLSearchParams({
                    'rid': aid,
                    'type': '2',
                    'add_media_ids': 收藏夹编号, // 根据实际需求调整
                    'del_media_ids': '',
                    'csrf': getCsrf()
                });

                // 获取当前浏览器的 Cookies
                const cookies = document.cookie;

                // 创建收藏请求的 XMLHttpRequest 对象
                const favXhr = new XMLHttpRequest();
                favXhr.withCredentials = true;
                favXhr.open('POST', 'https://api.bilibili.com/x/v3/fav/resource/deal');

                // 设置请求头
                favXhr.setRequestHeader('accept', 'application/json, text/plain, */*');
                favXhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
                favXhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
                favXhr.setRequestHeader('cookie', cookies);
                favXhr.setRequestHeader('origin', 'https://www.bilibili.com');
                favXhr.setRequestHeader('user-agent', navigator.userAgent);

                // 监听收藏请求响应
                favXhr.onload = function() {
                    updateDiagnosticInfo(favXhr.response); // 打印返回值
                };

                // 发送收藏请求
                favXhr.send(data);
            }, shoucangdelayInMilliseconds);
        }






        //*********************************************************************

        // 发送请求
        xhr.send(data);
    });
}



    // 显示继续按钮的函数
      // 显示继续按钮的函数
    function showContinueButton(aid) {
        const button = document.createElement('button');
        button.textContent = `继续处理下一个 AID (当前: ${aid})`;
        button.style.position = 'fixed';
        button.style.bottom = '20px';
        button.style.right = '20px';
        button.style.zIndex = '1000';
        button.style.padding = '10px';
        button.style.backgroundColor = '#4CAF50';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '5px';
        button.style.cursor = 'pointer';

        document.body.appendChild(button);

        button.onclick = function() {
            document.body.removeChild(button);
            submitNextAppeal(); // 继续处理下一个 AID
        };
    }






    // 提交下一个AID的函数
// 提交下一个AID的函数
function submitNextAppeal() {
    reportCount++
    if (currentAidIndex < aids.length) {
        const aid = aids[currentAidIndex];
        const csrfToken = getCsrf();
        updateDiagnosticInfo(`开始举报稿件 <span style="color: red; font-weight: bold;">${reportCount}</span>，aid: ${aid}<br>`);

        // 使用 setTimeout 来添加延迟
        setTimeout(() => {
            submitAppeal(aid, csrfToken, "具有性暗示的封面和标题，视频内容为国外擦边视频、二次元同人色情视频剪辑、色情游戏录屏，并在评论区向站外色情内容引流") // 提交请求    侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号。
                .then(() => {
                    currentAidIndex++;
                    submitNextAppeal(); // 提交下一个AID
                })
                .catch(err => {
                    console.error(err);
                });
        }, 30); // 延迟
    } else {
        updateDiagnosticInfo('<strong style="font-size: 2em">本页全部举报成功</strong><br>');
      const spaceIdMatches = window.location.href.match(/space\.bilibili\.com\/(\d+)(\/|\?|$)/);
const spaceId = spaceIdMatches ? spaceIdMatches[1] : null;
      const jumpUrl = `https://space.bilibili.com/${spaceId}/article`;
      window.location.href = jumpUrl;

    }
}





window.onload = function() {

    sendReportRequest();
    modifyRelation();//自动关注函数，不用可以直接注释掉
    extractAndSubmitAIDs(); // 创建按钮


};

function createButton() {
    const button = document.createElement('button');
    button.textContent = '批量举报当前UID';
    button.style.position = 'fixed';
    button.style.top = '70px';
    button.style.right = '20px';
    button.style.zIndex = '1000'; // 确保按钮在其他元素之上
    button.onclick = extractAndSubmitAIDs; // 点击按钮时调用函数

    document.body.appendChild(button); // 将按钮添加到页面
}






})();
