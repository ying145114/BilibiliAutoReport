let time_dynamic = 30
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

//######################################################################################################################
//###########################################共用变量定义部分##############################################################
//######################################################################################################################

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
function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
    }
    return csrfText;
}

//######################################################################################################################
//#################################################共用函数定义部分########################################################
//######################################################################################################################

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
    function sendReportRequest() {
        if (index < dyids.length) { // 处理每个 dyid
            reportDynamic(uid, dyids[index]);
            index++;
            setTimeout(sendReportRequest, time_dynamic);
        }
    }
    sendReportRequest();
    await new Promise(resolve => setTimeout(resolve, dyids.length * time_dynamic)); // 等待所有请求完成
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
            updateDiagnosticInfo(`动态：${xhr.responseText}<br>`);
            console.warn(`动态：${xhr.responseText}`);

        } else {
            updateDiagnosticInfo(`动态失败: ${xhr.status}<br>`);
            console.warn(`动态失败: ${xhr.status}`);
        }
    };
    xhr.onerror = function() {
        console.error('网络错误');
    };
    xhr.send(data); // 发送请求
}

//######################################################################################################################
//###################################################举报动态部分#########################################################
//######################################################################################################################

async function main() {

    await reportAllDynamic();//举报动态



}

main();


//######################################################################################################################
//###################################################函数入口部分#########################################################
//######################################################################################################################
