


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

async function main() {



        await extractAndSubmitAIDs(); // 执行 extractAndSubmitAIDs
        console.log("Extract and Submit AIDs completed. Now running Function B...");

        await console.log("Function B finished.");

    }
main();