//let output = ''
//const mid = window.location.pathname.split('/')[1];
var callback = arguments[arguments.length - 1];
let contentlocation = `${window.location.href}\n`;



const itemNodes = document.querySelectorAll('.small-item');// 查找所有类名为 small-item 的 <div> 元素
const urls = [];
for (const itemNode of itemNodes) {// 使用 for...of 循环遍历找到的元素，并提取 srcset URL
    const sourceNode = itemNode.querySelector('source[srcset]');// 查找第一个具有 srcset 属性的 <source> 元素
    if (sourceNode) {// 提取 srcset 属性并拼接成完整链接
        const fullUrl = 'https:' + sourceNode.getAttribute('srcset').match(/(\/\/i[0-9]\.hdslb\.com\/[^\s]+)/)[1];
        urls.push(fullUrl);
    }
    if (urls.length >= 3) { // 如果已经提取了 3 个链接，停止循环
        break; // 停止循环
    }
}
const imglink = urls.map(url => url.split('@')[0]).join(',');// 输出提取到的链接并格式化为期望的字符串
console.log(urls,imglink);// 输出结果





function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
    }
    return csrfText;
}












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
            xhr.onerror = function (err) {
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
                            (data.code === 0 && data.data && data.data.archives)

                            aids = data.data.archives.map(archive => archive.aid); // 提取 AID
                            console.log("Extracted AIDs:", aids);

                            // 针对 aid 数组中的每个元素进行处理
                            aids.forEach(id => {
                                contentlocation += `https://www.bilibili.com/video/av${id}\n`;
                            });
                            resolve();
                            // 使用 Promise.race 设置超时机制





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

            console.log('合集举报完成!');
            resolve(); // 完成后解除 Promise

        }


    })
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
                    const data = JSON.parse(xhr.responseText);
                    (data.code === 0 && data.data && data.data.archives)

                    aids = data.data.archives.map(archive => archive.aid); // 提取 AID
                    console.log("Extracted AIDs:", aids);


                    // 针对 aid 数组中的每个元素进行处理
                    aids.forEach(id => {
                        contentlocation += `https://www.bilibili.com/video/av${id}\n`;
                    });

                    // 输出最终的 location 变量
                    console.log(contentlocation);
                    sendTicket(contentlocation)

                } else {
                    console.log("Failed to fetch data, status:", xhr.status);
                    reject(`请求失败，状态码: ${xhr.status}`);
                    callback(`请求失败，状态码: ${xhr.status}`);
                }
            };
            xhr.onerror = function (err) {
                console.log("Request failed:", err);
                reject("请求失败");
                callback("请求失败");
            };
            xhr.send();
        } else {
            reject("MID 提取失败");
            callback("MID 提取失败");
        }
    });
}




function sendTicket(contentlocation){

    const ticketData = {
        write_type: 0,
        ticket_info: {
            ticket_id: "",
            business_info: {
                business_id: 10047
            },
            template_id: 10010,
            source_type: 4,
            is_visible: true,
            info: {
                problem_desc: `${contentlocation}以上视频具有色情内容暗示，使用标题和封面吸引眼球，并推广色情群组链接获利`,
                customer_demand: "下架该账号的违规视频",
                tipoff_reason: "这些视频的标题和封面是动漫人物色情二创作品的名称或截图，以此吸引用户点击。视频内容是色情游戏的剪辑和录屏，侮辱国家领导人，宣扬台独反华内容，并在置顶动态和评论暗示用户进行互动以获取色情内容。",
                tipoff_content_position: contentlocation,
                violation_uid: `${mid}`,
                contact_tel: "18147294457",
                pic: imglink,
                uid: DedeUserID
            },
            create_channel_type: 9,
            extra: {}
        }
    };

    const data = new URLSearchParams({
        'data': JSON.stringify(ticketData),
        'csrf': getCsrf()
    });

    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('POST', 'https://customerservice.bilibili.com/x/custom/call_svr/v1/write_ticket');
    xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
    xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');


    xhr.onload = function () {
        console.log(xhr.response);
        callback(xhr.response)
    };

    xhr.send(data);





}

async function main() {
    await extractSeries();
    await extractAndSubmitAIDs(); //举报视频

}

main();