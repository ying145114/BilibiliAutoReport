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
    return new Promise((resolve, reject) => {
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
                            aids = data.data.archives.map(archive => archive.aid); // 提取 AID
                            console.log("Extracted AIDs:", aids);
                            currentAidIndex = 0; // 重置索引
                            submitNextAppeal().then(() => {
                                resolve("完成，结束");
                            }).catch(err => {
                                reject(err);
                            });
                        } else {
                            console.log("No archives found or error in response:", data);
                            resolve("没有找到记录，结束");
                        }
                    } catch (e) {
                        console.log("Error parsing JSON:", e);
                        reject("JSON解析错误");
                    }
                } else {
                    console.log("Failed to fetch data, status:", xhr.status);
                    reject(`请求失败，状态码: ${xhr.status}`);
                }
            };
            xhr.onerror = function(err) {
                console.log("Request failed:", err);
                reject("请求失败");
            };
            xhr.send();
        } else {
            reject("MID 提取失败");
        }
    });
}

function submitAppeal(aid) {
    return new Promise((resolve) => {
        const data = new URLSearchParams({
            'aid': aid,
            'attach': '',
            'block_author': 'false',
            'csrf': getCsrf(),
            'desc': "侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号",
            'tid': '10014'
        }).toString();
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open('POST', 'https://api.bilibili.com/x/web-interface/appeal/v2/submit');
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
        xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

        let timeoutId = setTimeout(() => {
            console.warn(`请求超时，AID ${aid}，请检查网络连接。`);
            xhr.abort(); // 超时则中止请求
            resolve();   // 解除 Promise
        }, 3000);

        xhr.onload = function() {
            clearTimeout(timeoutId);
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                updateDiagnosticInfo(`举报结果：<strong>${this.response}</strong><br>`);
                console.warn(this.response)

                if (result.code === -352) {
                    console.log(`AID ${aid} 的返回码为 -352，直接结束所有举报。`);
                    updateDiagnosticInfo('<strong style="font-size: 20px; color: red;">举报已被终止!</strong><br>');
                    resolve(false); // 返回 false 表示结束
                    return;          // 退出当前函数
                }

                // 其他代码和状态均不处理，直接 resolve
                resolve(true); // 正常情况下返回 true
            } else {
                // 对于其他状态码，不作处理，直接解除 Promise
                console.warn(`请求返回错误，状态码: ${xhr.status}`);
                resolve(true); // 继续执行后续逻辑
            }
        };

        xhr.onerror = function(err) {
            clearTimeout(timeoutId);
            console.error(`请求失败，AID ${aid}:`, err);
            resolve(true); // 请求失败时继续执行后续逻辑
        };
//**********************************************************************************************************************



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
    console.warn(xhr.responseText); // 更新诊断信息
};

// 发送请求
xhr.send(data.toString());

            }


//**********************************************************************************************************************
        xhr.send(data);
    });
}

function submitNextAppeal() {
    reportCount++;
    return new Promise((resolve) => {
        if (currentAidIndex < aids.length) {
            const aid = aids[currentAidIndex];
            updateDiagnosticInfo(`开始举报稿件 <span style="color: red; font-weight: bold;">${reportCount}</span>，aid: ${aid}<br>`);

            setTimeout(() => {
                submitAppeal(aid)
                    .then((shouldContinue) => {
                        if (!shouldContinue) {
                            resolve(); // 直接结束
                            return;     // 退出当前函数
                        }
                        currentAidIndex++;
                        submitNextAppeal().then(resolve);
                    });
            }, 30);
        } else {
            updateDiagnosticInfo('<strong style="font-size: 20px; color: green;">所有举报完成!</strong><br>');
            resolve(); // 完成后解除 Promise
        }
    });
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
            console.log(`Processing article ID: ${aid}`);
            sendComplaint(aid);
            index++;
            return new Promise((resolve) => {
                setTimeout(() => {
                    console.log(`Waiting 3500ms before processing the next ID...`);
                    processNext().then(resolve); // 确保每个请求完成后再继续
                }, 30);
            });
        } else {
            return Promise.resolve(); // 完成处理
        }
    }

    return processNext(); // 返回处理的 Promise
}

function getAid(page) {
    return new Promise((resolve, reject) => {
        const mid = window.location.pathname.split('/')[1];
        const url = `https://api.bilibili.com/x/space/article?mid=${mid}&pn=${page}&ps=${pageSize}&sort=publish_time`;
        const xhr = new XMLHttpRequest();
        xhr.open("GET", url, true);
        xhr.onload = function() {
            if (xhr.status === 200) {
                const data = JSON.parse(xhr.responseText);
                console.log("Response Data:", data);
                if (data.code === 0 && data.data) {
                    const { count, pn } = data.data;
                    if (!data.data.articles || data.data.articles.length === 0) {
                        console.log("No articles found for this account. Exiting...");
                        resolve(); // 退出，不再请求下一页
                        return;
                    }
                    const totalPages = Math.ceil(count / pageSize);
                    console.log(`Current Page: ${pn}, Total Pages: ${totalPages}, Total Count: ${count}`);
                    if (pn >= totalPages) {
                        updateDiagnosticInfo('<strong style="font-size: 2em; color: blue;">全部专栏举报完成</strong><br>');
                    }
                    const articles = data.data.articles || [];
                    const articleIds = articles.map(article => article.id);
                    console.log("Article IDs:", articleIds);
                    processArticleIds(articleIds)
                        .then(resolve) // 处理完所有文章ID后解析 Promise
                        .catch(reject); // 如果有错误，则拒绝 Promise
                } else {
                    console.error("Error in response:", data.message);
                    reject(new Error(data.message));
                }
            } else {
                console.error("Request failed with status:", xhr.status);
                reject(new Error(`Request failed with status: ${xhr.status}`));
            }
        };
        xhr.onerror = function(err) {
            console.error("Request error:", err);
            reject(err);
        };
        xhr.send();
    });
}



function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
        }
    return csrfText;
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
    let allDyids = []; // 用于存储所有获取到的 dyid

    while (true) { // 循环处理请求
        try {
            const result = await getAllDynamic(offset); // 使用 await 来等待 getAllDynamic 的 Promise 结果
            const dyids = result.ids; // 当前请求的动态 ID

            // 收集当前批次的动态 ID
            if (dyids.length > 0) {
                allDyids.push(...dyids);
            }

            offset = result.nextOffset; // 更新 offset

            // 如果 offset 为空，表示没有更多数据可请求，退出循环
            if (!offset) {
                console.log('已达到最后一页，退出循环。');
                break;
            }

        } catch (error) {
            updateDiagnosticInfo("Error occurred while getting dyids:", error + '\n'); // 修改错误提示
            break; // 出现错误时退出循环
        }
    }

    // 在退出循环后处理所有收集到的 dyid
    if (allDyids.length > 0) {
        await processDyids(uid, allDyids);
    } else {
        console.log('没有可报告的动态。');
    }
}

// 添加一个新的函数来处理所有收集到的 dyid
async function processDyids(uid, dyids) {
    let index = 0;
    const interval = 30; // 延迟

    function sendReportRequest() {
        if (index < dyids.length) { // 处理每个 dyid
            reportDynamic(uid, dyids[index]);
            index++;
            setTimeout(sendReportRequest, interval);
        }
    }

    sendReportRequest();
    await new Promise(resolve => setTimeout(resolve, dyids.length * interval)); // 等待所有请求完成
}









function reportDynamic(uid, dyid) {
    const csrf = getCsrf(); // 获取 CSRF 令牌
    const data = JSON.stringify({
        'accused_uid': Number(uid), // 确保 uid 是整数
        'dynamic_id': String(dyid), // 确保 dynamic_id 是字符串
        'reason_type': 4,
        'reason_desc': ''
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






function waitFor70Seconds() {
    const start = Date.now();
    // 循环直到 70 秒过去
    while (Date.now() - start < 70000) {
        // 空循环
    }
    console.log("已等待 70 秒");
}



async function main() {


        await sendReportRequest();//举报签名昵称头像
        await extractAndSubmitAIDs(); //举报视频
        await getAid(currentPage);//举报专栏
        await reportAllDynamic();//举报动态



    }
main();
