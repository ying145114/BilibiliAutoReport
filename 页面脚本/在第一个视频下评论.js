let wordCount = {};
let topWord = [];



function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
    }
    return csrfText;
}

function extractAndSubmitAIDs() {
    const currentUrl = window.location.href; // 获取当前URL
    const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);

    if (midMatch && midMatch[1]) {
        const mid = midMatch[1];

        // 构造API请求URL
        const apiUrl = `https://api.bilibili.com/x/series/recArchivesByKeywords?mid=${mid}&keywords=&ps=0`;

        // 使用XMLHttpRequest进行请求
        const xhr = new XMLHttpRequest();
        xhr.open("GET", apiUrl, true);

        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    if (data.code === 0 && data.data && data.data.archives) {
                    const titles = data.data.archives.map(archive => archive.title);

// 统计词频


titles.forEach(title => {
    // 使用正则表达式提取中文和英文字符
    const words = title.match(/[\u4e00-\u9fa5a-zA-Z]+/g);
    if (words) {
        words.forEach(word => {
            // 过滤掉长度小于2的词
            if (word.length > 1) {
                const lowerCaseWord = word.toLowerCase(); // 转换为小写以便不区分大小写
                wordCount[lowerCaseWord] = (wordCount[lowerCaseWord] || 0) + 1;
            }
        });
    }
});

// 获取出现频率最高的词
const sortedWords = Object.entries(wordCount).sort((a, b) => b[1] - a[1]);
const topWord = sortedWords[0];

// 输出结果
if (topWord) {
    console.log(`出现频率最高的词: "${topWord[0]}", 次数: ${topWord[1]}`);

} else {
    console.log("没有找到任何词。");
}












































                        // 提取第一个AID
                        const firstAid = data.data.archives[0]?.aid;
                        if (firstAid) {
                            console.log("Extracted AID:", firstAid);
                            sendComment(firstAid,topWord); // 使用第一个AID调用sendComment函数
                        } else {
                            console.error("No AID found in the response.");
                        }
                    } else {
                        console.error("No archives found or error in response:", data);
                    }
                } catch (e) {
                    console.error("Error parsing JSON:", e);
                }
            } else {
                console.error("Failed to fetch data, status:", xhr.status);
            }
        };

        xhr.onerror = function() {
            console.error("Request failed.");
        };

        // 发送请求
        xhr.send();
    } else {
        console.warn("No valid mid found in the URL.");
    }
}

// 使用示例，调用提取和提交函数


// 使用示例，调用提取和提交函数























    function sendComment(oid,topWord) {
const dataObj = {
    plat: 1,
    oid: oid,
    type: 1,
    message: `该作者标题中经常出现的词是: "${topWord[0]}", 出现次数: ${topWord[1]} 这个视频是否存在某些问题？\n是    否\n👇    👇`,
    // at_name_to_mid: JSON.stringify({"自动举报姬": 3494374224694043}), // 将对象转换为 JSON 字符串
    sync_to_dynamic: 1,
    gaia_source: 'main_web',
    csrf: getCsrf(),
    statistics: JSON.stringify({ appId: 100, platform: 5 }) // 转换 statistics 对象为 JSON 字符串
};


// 使用 URLSearchParams 将对象转换为 URL 编码的字符串
const data = new URLSearchParams(dataObj).toString();


    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('POST', 'https://api.bilibili.com/x/v2/reply/add?');
    xhr.setRequestHeader('accept', '*/*');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

    xhr.onload = function() {
        console.log(xhr.response);
    };

    xhr.send(data);
}

// 使用示例
extractAndSubmitAIDs();