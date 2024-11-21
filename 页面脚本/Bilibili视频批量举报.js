var callback = arguments[arguments.length - 1];

let reportCount = 0
let currentAidIndex = 0; // 当前处理的AID索引
let time_video = 2300
let aids = []; // 所有提取的AID
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

function sendReportRequest() {
    const mid = window.location.href.match(/bilibili.com\/(\d+)/)[1];
    const csrf = getCsrf();
    const xhr = new XMLHttpRequest();
    xhr.open("POST", 'https://space.bilibili.com/ajax/report/add', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onload = function () {
        updateDiagnosticInfo(`主页：${this.response}`)
        console.warn(`主页：${this.response}`)
    };
    xhr.send(`mid=${mid}&reason=1%2C3%2C2&reason_v2=3&csrf=${csrf}`);
}

//######################################################################################################################
//###################################################举报主页部分#########################################################
//######################################################################################################################







function extractSeries() {
    return new Promise((resolve, reject) => {
        const currentUrl = window.location.href;
        const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);
        if (midMatch && midMatch[1]) {
            const mid = midMatch[1];
            const apiUrl = `https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid=${mid}&page_num=1&page_size=1`;
            const xhr = new XMLHttpRequest();
            xhr.open("GET", apiUrl);
            xhr.onload = function () {
                if (xhr.status === 200) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        if (data.code === 0 && data.data && data.data.items_lists) {
                            seasonIds = data.data.items_lists.seasons_list.map(season => season.meta.season_id);// 提取 AID
                            console.log("Extracted seasonIds:", seasonIds);
                            currentAidIndex = 0; // 重置索引
                            extractSeasonAIDs(seasonIds).then(() => {
                                resolve("完成，结束");
                            }).catch(err => {
                                reject(err);
                            });
                        } else {
                            console.log("没有找到记录:", data);
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



function extractSeasonAIDs() {
    return new Promise((resolve, reject) => {
        if (currentAidIndex < seasonIds.length) {
            const seasonId = seasonIds[currentAidIndex];


            const currentUrl = window.location.href;
            const midMatch = currentUrl.match(/space\.bilibili\.com\/(\d+)/);

            if (midMatch && midMatch[1]) {
                const mid = midMatch[1];
                const apiUrl = `https://api.bilibili.com/x/polymer/space/seasons_archives_list?mid=${mid}&sort_reverse=false&season_id=${seasonId}&page_num=1&page_size=30`;
                const xhr = new XMLHttpRequest();
                xhr.open("GET", apiUrl);
                console.log(apiUrl)

                xhr.onload = function () {
                    if (xhr.status === 200) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            if (data.code === 0 && data.data && data.data.archives) {
                                aids = data.data.archives.map(archive => archive.aid); // 提取 AID
                                console.log("Extracted AIDs:", aids);
                                currentAidIndex = 0; // 重置索引

                                // 使用 Promise.race 设置超时机制
                                const submitPromise = submitNextAppeal(); // 假设此函数返回一个 Promise
                                const timeoutPromise = new Promise((_, reject) =>
                                    setTimeout(() => reject("提交超时"), 10000) // 10秒超时
                                );

                                Promise.race([submitPromise, timeoutPromise])
                                    .then(() => {
                                        resolve("完成，结束");
                                    })
                                    .catch(err => {
                                        console.log(err);
                                    });

                            } else {
                                console.log("没有找到记录:", data);
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

                xhr.onerror = function (err) {
                    console.log("Request failed:", err);
                    reject("请求失败");
                };
                xhr.send();
            } else {
                reject("MID 提取失败");
            }



        } else {
            updateDiagnosticInfo('合集举报完成!<br>');
            console.warn('合集举报完成!');
            resolve(); // 完成后解除 Promise

        }



    })
}




//######################################################################################################################
//###################################################举报合集部分#########################################################
//######################################################################################################################



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
                                        console.log("没有找到记录:", data);
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
                        updateDiagnosticInfo(`视频：请求超时<br>`);
                        console.warn(`视频：请求超时`);
                        xhr.abort(); // 超时则中止请求
                        resolve();   // 解除 Promise
                    }, 3000);

                    xhr.onload = function() {
                        clearTimeout(timeoutId);
                        if (xhr.status === 200) {
                            const result = JSON.parse(xhr.responseText);
                            updateDiagnosticInfo(`视频：${this.response}<br>`);
                            console.warn(`视频${reportCount}：${this.response}`)

                            if (result.code === -352) {
                                updateDiagnosticInfo(`视频：${this.response}<br>`);
                                console.warn(`视频${reportCount}：${this.response}`)
                                callback('352');
                                resolve(false); // 返回 false 表示结束
                                return;          // 退出当前函数
                            }

                            // 其他代码和状态均不处理，直接 resolve
                            resolve(true); // 正常情况下返回 true
                        } else {
                            // 对于其他状态码，不作处理，直接解除 Promise
                            updateDiagnosticInfo(`视频：${this.response}<br>`);
                            console.warn(`视频${reportCount}：${this.response}`);

                            resolve(true); // 继续执行后续逻辑
                        }
                    };

                    xhr.onerror = function(err) {
                        clearTimeout(timeoutId);
                        console.error(`请求失败:`, err);
                        resolve(true); // 请求失败时继续执行后续逻辑
                    };

//###############################################点赞视频部分#############################################################

                    if (reportCount % 50 === 49) {
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
                            updateDiagnosticInfo(`点赞：${xhr.responseText}<br>`); // 更新诊断信息
                            console.warn(`点赞：${xhr.responseText}`); // 更新诊断信息
                        };

// 发送请求
                        xhr.send(data.toString());

                    }

//###############################################点赞视频部分#############################################################

                    xhr.send(data);
                });
            }

            function submitNextAppeal() {
                reportCount++;
                return new Promise((resolve) => {
                    if (currentAidIndex < aids.length) {
                        const aid = aids[currentAidIndex];
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
                        }, time_video);
                    } else {
                        updateDiagnosticInfo('视频举报完成!<br>');
                        console.warn('视频举报完成!');
                        callback('视频举报完成!');
                        resolve(); // 完成后解除 Promise
                    }
                });
            }

//######################################################################################################################
//###################################################举报视频部分#########################################################
//######################################################################################################################

    async function main() {
                await sendReportRequest();//举报签名昵称头像
                await extractSeries();
                await extractAndSubmitAIDs(); //举报视频
            }

            main();
//######################################################################################################################
//###################################################函数入口部分#########################################################
//######################################################################################################################


