//let output = ''
//const mid = window.location.pathname.split('/')[1];
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

console.log(urls);// 输出提取到的链接
const output = urls.map(url => url.split('@')[0]).join(',');// 输出提取到的链接并格式化为期望的字符串
console.log(output);// 输出结果
function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
    }
    return csrfText;
}


const ticketData = {
    write_type: 0,
    ticket_info: {
        ticket_id: "",
        business_info: {
            business_id: 10059
        },
        template_id: 10010,
        source_type: 4,
        is_visible: true,
        info: {
            problem_desc: `账号${mid}多次发布具有色情内容暗示的视频，使用标题和封面吸引眼球，并推广色情群组链接获利`,
            customer_demand: "下架视频并封禁该账号",
            tipoff_reason: "该账号发布的视频标题和封面是动漫人物色情二创作品的名称或截图，以此吸引用户点击。并在置顶动态和评论暗示用户进行互动以获取色情内容。",
            tipoff_content_position: window.location.href,
            violation_uid: `${mid}`,
            contact_tel: "18147294457",
            pic: output,
            uid: "3546744296049110"
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
};

xhr.send(data);
