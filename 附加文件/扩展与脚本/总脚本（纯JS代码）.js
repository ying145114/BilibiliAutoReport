
let reportCount = 0
let csrfText = ''; // 用于存储CSRF token
let currentAidIndex = 0; // 当前处理的AID索引
let aids = []; // 所有提取的AID
const currentUrl = window.location.href;// 获取当前URL

const floatingWindow = document.createElement('div');// 创建诊断信息窗口
    floatingWindow.style.position = 'fixed';
    floatingWindow.style.top = '100px';
    floatingWindow.style.right = '20px';
    floatingWindow.style.zIndex = '9999';
    floatingWindow.style.background = 'white';
    floatingWindow.style.border = '1px solid #ccc';
    floatingWindow.style.padding = '10px';
    floatingWindow.style.maxWidth = '340px';
    floatingWindow.style.overflow = 'auto'; // 为滚动添加溢出属性
    floatingWindow.style.height = '200px';
    floatingWindow.style.scrollBehavior = 'smooth'; // 启用平滑滚动
    document.body.appendChild(floatingWindow);

const diagnosticInfo = document.createElement('div');// 创建诊断信息容器
    floatingWindow.appendChild(diagnosticInfo);







function sendReportRequest() {
    const mid = window.location.href.match(/bilibili.com\/(\d+)/)[1];
    const csrf = getCsrf();
    const xhr = new XMLHttpRequest();
    xhr.open("POST", 'https://space.bilibili.com/ajax/report/add', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onload = function () {

        const decodedResponse = JSON.parse(decodeURIComponent(this.response));
        updateDiagnosticInfo(`举报请求返回值：<strong>${Object.keys(decodedResponse).map(key => `${key}: ${decodedResponse[key]}`).join(', ')}</strong><br>`);
        };
    xhr.send(`mid=${mid}&reason=1%2C3%2C2&reason_v2=3&csrf=${csrf}`);
}

function scrollToBottom() {// 滚动到浮动窗口底部的函数
    floatingWindow.scrollTop = floatingWindow.scrollHeight;
    const lastElement = floatingWindow.lastElementChild;// 将最后一个元素滚动到视图中
    if (lastElement) {
        lastElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
}

function updateDiagnosticInfo(content) {// 使用滚动到底部更新 diagnosticInfo.innerHTML
    diagnosticInfo.innerHTML += content;
    scrollToBottom();
}

function getCsrf() { // 提取CSRF Token的函数
    if (csrfText === '') {
        const cook = document.cookie.match(/bili_jct=(.*?);/) ?? [];
        if (cook.length === 2) {
            csrfText = cook[1];
            }
        }
    return csrfText;
}

function extractAndSubmitAIDs() {
    const currentUrl = window.location.href;
    const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);
     if (midMatch && midMatch[1]) {
         const mid = midMatch[1];
         const apiUrl = `https://api.bilibili.com/x/series/recArchivesByKeywords?mid=${mid}&keywords=&ps=0`;
         const xhr = new XMLHttpRequest();
         xhr.open("GET", apiUrl);
          xhr.onload = function () {
              if (xhr.status === 200) {
                  try {
                      const data = JSON.parse(xhr.responseText);
                      if (data.code === 0 && data.data && data.data.archives) {
                          aids = data.data.archives.map(archive => archive.aid); // 使用全局变量，提取并保存所有的aid
                          console.log("Extracted AIDs:", aids);// 开始提交每个AID
                          currentAidIndex = 0; // 重置索引
                          submitNextAppeal(); // 提交下一个AID
                          } else {
                              console.log("No archives found or error in response:", data);
                              }
                      } catch (e) {
                          console.log("Error parsing JSON:", e);
                          }
                  } else {
                      console.log("Failed to fetch data, status:", xhr.status);
                      }
              };
         xhr.onerror = function(err) {
             console.log("Request failed:", err);
             };
         xhr.send();
         }
}

function submitAppeal(aid) {
    return new Promise((resolve, reject) => {
        const data = new URLSearchParams({
            'aid': aid,
            'attach': '',
            'block_author': 'false',
            'csrf': getCsrf(),
            'desc': "侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号",
            'tid': '10014' //10014
        }).toString();
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open('POST', 'https://api.bilibili.com/x/web-interface/appeal/v2/submit');
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
        xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
        let timeoutId = setTimeout(() => {
            console.warn(`请求超时，AID ${aid}，请检查网络连接。`);
            xhr.abort();
            resolve();
        }, 3000);
        xhr.onload = function() {
            clearTimeout(timeoutId);
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                updateDiagnosticInfo(`举报结果：<strong>${this.response}</strong><br>`);
                if (result.code === -352){
                    getAid(currentPage);
                    reject(`AID ${aid} 的返回码为 -352。`);
                    } else {
                        resolve(result);
                        }
                } else {
                    console.warn(`请求返回错误，状态码: ${xhr.status}`);
                    resolve();
                    }
            };
        xhr.onerror = function(err) {
            clearTimeout(timeoutId);
            console.error(`请求失败，AID ${aid}:`, err);
            };
//************************************************************************************************************************************************************************************



        if (reportCount % 10 === 9) {
            const data = new URLSearchParams({
    'aid': aid, // 确保 aid 的值是字符串或数字
    'like': '1',
    'csrf': getCsrf() // 请确保这是从浏览器中获取到的有效值
});

let xhr = new XMLHttpRequest();
xhr.withCredentials = true; // 允许跨域请求携带凭证
xhr.open("POST", "https://api.bilibili.com/x/web-interface/archive/like");
xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');


xhr.onload = function() {
    updateDiagnosticInfo(xhr.responseText); // 更新诊断信息
};

// 发送请求
xhr.send(data.toString());

            }



//***************************************************************************************************************************************************************************************


        xhr.send(data);
        });
}


function submitNextAppeal() {// 提交下一个AID的函数
    reportCount++
    if (currentAidIndex < aids.length) {
        const aid = aids[currentAidIndex];
        updateDiagnosticInfo(`开始举报稿件 <span style="color: red; font-weight: bold;">${reportCount}</span>，aid: ${aid}<br>`);// 使用 setTimeout 来添加延迟
        setTimeout(() => {
            submitAppeal(aid) // 提交请求
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
            getAid(currentPage);
            }
}
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
let currentPage = 1; // 初始页码
let pageSize = 30;
const urlParams = new URLSearchParams(window.location.search);

floatingWindow.appendChild(diagnosticInfo);




function processArticleIds(articleIds) {
    let index = 0;
    function processNext() {
        if (index < articleIds.length) {
            const aid = articleIds[index];
            console.log(`Processing article ID: ${aid}`); // 打印当前处理的ID
            sendComplaint(aid); // 调用处理函数
            index++;
            setTimeout(() => {
                console.log(`Waiting 3500ms before processing the next ID...`); // 等待提示
                processNext(); // 继续处理下一个
                }, 30); //延迟
            } else {
                currentPage++;
                getAid(currentPage); // 处理完毕后请求下一页
                }
        }
    processNext(); // 开始处理 ID
}


function getAid(page) {
    const mid = window.location.pathname.split('/')[1]; // 从地址栏获取 mid
    const url = `https://api.bilibili.com/x/space/article?mid=${mid}&pn=${page}&ps=${pageSize}&sort=publish_time`;
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true); // 异步请求
    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            console.log("Response Data:", data); // 打印完整的响应数据
            if (data.code === 0 && data.data) {
                const { count, pn } = data.data;
                if (!data.data.articles || data.data.articles.length === 0) {
                    console.log("No articles found for this account. Exiting...");
                    reportAllDynamic();
                    }
                const totalPages = Math.ceil(count / pageSize); // 计算总页数
                console.log(`Current Page: ${pn}, Total Pages: ${totalPages}, Total Count: ${count}`); // 调试输出
                if (pn >= totalPages) {
                    updateDiagnosticInfo('<strong style="font-size: 2em; color: blue;">全部专栏举报完成</strong><br>');
                    reportAllDynamic();
                    }
                const articles = data.data.articles || [];
                const articleIds = articles.map(article => article.id);
                console.log("Article IDs:", articleIds); // 打印所有ID到控制台
                processArticleIds(articleIds); // 处理所有文章ID
                } else {
                    console.error("Error in response:", data.message);
                    }
            } else {
                console.error("Request failed with status:", xhr.status);
                }
        };
    xhr.onerror = function(err) {
        console.error("Request error:", err);
        };
    xhr.send(); // 发送请求
}






function sendComplaint(aid) {
    reportCount++
    const csrfToken = getCsrf();
    const data = new URLSearchParams({
        'aid': aid, // 使用传入的 aid 值
        'cid': '1',
        'reason': '侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号',
        'images': '',
        'csrf': csrfToken
        });
    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('POST', 'https://api.bilibili.com/x/article/complaints');
    xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
    xhr.setRequestHeader('accept-language', navigator.language || 'zh-CN,zh;q=0.9');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        updateDiagnosticInfo(`成功举报${reportCount}，文章ID: ${aid} - 响应内容: ${xhr.responseText}<br>`);
        };
    xhr.send(data);
}
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



function getUid() {
    const currentUrl = window.location.href;
    const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);
     if (midMatch && midMatch[1]) {
         const mid = midMatch[1];
    return mid; // 返回UID或null
}

}

function getAllDynamic(offset = '') {
    const uid = getUid();
    updateDiagnosticInfo('提取的UID:', uid);
    updateDiagnosticInfo("getAllDynamic function called\n");

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        const url = `https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=${offset}&host_mid=${uid}&timezone_offset=-480&platform=web&features=itemOpusStyle,listOnlyfans,opusBigCover,onlyfansVote,decorationCard,forwardListHidden,ugcDelete,onlyfansQaCard&web_location=333.999`;

        xhr.open("GET", url, true);
        xhr.withCredentials = true; // Enable withCredentials

        // Set headers
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
        xhr.onload = function () {
            try {
                if (xhr.status >= 200 && xhr.status < 300) {
                    var jsonResponse = JSON.parse(xhr.responseText);
                    console.log('完整的响应对象:', jsonResponse);
                    let idStrArray = [];
                    if (jsonResponse && jsonResponse.data && jsonResponse.data.items) {
                        jsonResponse.data.items.forEach(item => {
                            if (item && item.id_str) {
                                idStrArray.push(item.id_str);
                            }
                        });
                    }
                    const nextOffset = jsonResponse.data.offset;
                    console.log('提取的 id_str:', idStrArray);
                    console.log('提取的 offset:', nextOffset);
                    resolve({ ids: idStrArray, nextOffset: nextOffset });
                } else {
                    throw new Error(`请求失败，状态码: ${xhr.status}`);
                }
            } catch (error) {
                console.error('解析响应失败:', error);
                reject(error);
            }
        };

        xhr.onerror = function () {
            console.error('请求失败:', xhr.statusText);
            reject(new Error('网络错误'));
        };

        xhr.send();
    });
}





async function reportAllDynamic() {
    const uid = getUid();
    let offset = ''; // 初始化 offset
    while (true) { // 循环处理请求
        try {
            const result = await getAllDynamic(offset); // 使用 await 来等待 getAllDynamic 的 Promise 结果
            const dyids = result.ids; // 当前请求的动态 ID
            offset = result.nextOffset; // 更新 offset
            if (dyids.length === 0) {
                break;
                }
            let index = 0;
            const interval = 30;// 延迟
            function sendReportRequest() {
                if (index < dyids.length) { // 修改此处，使用 dyids
                    reportDynamic(uid, dyids[index]); // 修改此处，使用 dyids
                    index++;
                    setTimeout(sendReportRequest, interval);
                    }
                }
            sendReportRequest();
            await new Promise(resolve => setTimeout(resolve, dyids.length * interval)); // 简单的等待方式，根据需求调整
            } catch (error) {
                updateDiagnosticInfo("Error occurred while getting dyids:", error + '\n'); // 修改错误提示
                break; // 出现错误时退出循环
                }
        }
}








function reportDynamic(uid, dyid) {
    const csrf = getCsrf(); // 获取 CSRF 令牌
    const data = JSON.stringify({
        'accused_uid': Number(uid), // 确保 uid 是整数
        'dynamic_id': String(dyid), // 确保 dynamic_id 是字符串
        'reason_type': 9,
        'reason_desc': '侮辱国家领导人，宣扬反华内容。审核结果：下架此视频并永久封禁该账号'
    });
    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true; // 允许跨域请求携带凭证
    xhr.open('POST', `https://api.bilibili.com/x/dynamic/feed/dynamic_report/add?csrf=${csrf}`, true);
    xhr.setRequestHeader('accept', '*/*');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
    xhr.setRequestHeader('content-type', 'application/json');
    xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 300) {
            updateDiagnosticInfo(xhr.responseText + '\n');
            } else {
                console.error(`请求失败，状态码: ${xhr.status}`);
                }
        };
    xhr.onerror = function() {
        console.error('网络错误');
        };
    xhr.send(data); // 发送请求
}


extractAndSubmitAIDs();
sendReportRequest();
