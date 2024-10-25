const floatingWindow = document.createElement('div');
floatingWindow.style.position = 'fixed';
floatingWindow.style.top = '90px';
floatingWindow.style.right = '20px';
floatingWindow.style.zIndex = '9999';
floatingWindow.style.background = 'white';
floatingWindow.style.border = '1px solid #ccc';
floatingWindow.style.padding = '10px';
floatingWindow.style.maxWidth = '250px';
floatingWindow.style.overflow = 'auto'; // Add overflow property for scrolling
floatingWindow.style.height = '200px'; // Set a height for the window
floatingWindow.style.scrollBehavior = 'smooth'; // Enable smooth scrolling
document.body.appendChild(floatingWindow);

const diagnosticInfo = document.createElement('div');
floatingWindow.appendChild(diagnosticInfo);



function scrollToBottom() {
    floatingWindow.scrollTop = floatingWindow.scrollHeight;
    const lastElement = floatingWindow.lastElementChild;
    if (lastElement) {
        lastElement.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
}


function updateDiagnosticInfo(content) {
    diagnosticInfo.innerHTML += content;
    scrollToBottom();
}



function getUid() {
    const url = window.location.href;
    const match = url.match(/space\.bilibili\.com\/(\d+)\/dynamic/);
    return match ? match[1] : null; // 返回UID或null
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







let csrfText = '';
function getCsrf() {
    if (csrfText === '') {
        const cook = document.cookie.match(/bili_jct=(.*?);/) ?? [];
        if (cook.length === 2) {
            csrfText = cook[1];
            }
        }
    return csrfText;
}





reportAllDynamic();
