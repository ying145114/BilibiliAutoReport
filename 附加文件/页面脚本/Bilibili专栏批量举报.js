let currentPage = 1; // 初始页码
let pageSize = 30;
let reportCount = 0
const urlParams = new URLSearchParams(window.location.search);
const floatingWindow = document.createElement('div');

    floatingWindow.style.position = 'fixed';
    floatingWindow.style.top = '90px';
    floatingWindow.style.right = '20px';
    floatingWindow.style.zIndex = '9999';
    floatingWindow.style.background = 'white';
    floatingWindow.style.border = '1px solid #ccc';
    floatingWindow.style.padding = '10px';
    floatingWindow.style.maxWidth = '250px';
    floatingWindow.style.overflow = 'auto';
    floatingWindow.style.height = '200px';
    floatingWindow.style.scrollBehavior = 'smooth';
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
                    return"全部完成"; // 退出，不再请求下一页
                    }
                const totalPages = Math.ceil(count / pageSize); // 计算总页数
                console.log(`Current Page: ${pn}, Total Pages: ${totalPages}, Total Count: ${count}`); // 调试输出
                if (pn >= totalPages) {
                    updateDiagnosticInfo('<strong style="font-size: 2em; color: blue;">全部专栏举报完成</strong><br>');
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

getAid(currentPage);
