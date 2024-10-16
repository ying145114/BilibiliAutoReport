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
            'tid': '10014'
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
            submitAppeal(aid, csrfToken, "视频封面标题以及内容违规，推广以原神、碧蓝档案等二次元游戏人物为主角的色情视频，以未成年人为主角的色情游戏，，并在置顶动态以及评论内向站外色情网站引流，严重危害青少年用户的身心健康") // 提交请求
                .then(() => {
                    currentAidIndex++;
                    submitNextAppeal(); // 提交下一个AID
                })
                .catch(err => {
                    console.error(err);
                });
        }, 20); // 延迟2000毫秒
    } else {
        updateDiagnosticInfo('<strong style="font-size: 2em">本页全部举报成功</strong><br>');
      const spaceIdMatches = window.location.href.match(/space\.bilibili\.com\/(\d+)(\/|\?|$)/);
const spaceId = spaceIdMatches ? spaceIdMatches[1] : null;
      const jumpUrl = `https://space.bilibili.com/${spaceId}/article`;
      window.location.href = jumpUrl;

    }
}





window.onload = function() {


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
