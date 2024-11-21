
let currentPage = 1; // 初始页码
let pageSize = 30;
let time_article = 30
let seasonIds= [];
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

                    processNext().then(resolve); // 确保每个请求完成后再继续
                }, time_article);
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
                        updateDiagnosticInfo('无可举报专栏！<br>');
                        console.warn('无可举报专栏！');
                        resolve(); // 退出，不再请求下一页
                        return;
                    }
                    const totalPages = Math.ceil(count / pageSize);
                    console.log(`Current Page: ${pn}, Total Pages: ${totalPages}, Total Count: ${count}`);
                    if (pn >= totalPages) {
                        updateDiagnosticInfo('专栏举报完成！<br>');
                        console.warn('专栏举报完成！<br>');
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

function sendComplaint(aid) {
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
        updateDiagnosticInfo(`专栏：${xhr.responseText}<br>`);
        console.warn(`专栏：${xhr.responseText}`);
    };
    xhr.send(data);
}

//######################################################################################################################
//###################################################举报专栏部分#########################################################
//######################################################################################################################

async function main() {

    await getAid(currentPage);//举报专栏



}

main();


//######################################################################################################################
//###################################################函数入口部分#########################################################
//######################################################################################################################
