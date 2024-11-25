let csrfText = ''

function getCsrf() {
    if (csrfText === '') {
        const cook = document.cookie.match(/bili_jct=(.*?);/) ?? [];
        if (cook.length === 2) {
            csrfText = cook[1];
        }
    }
    return csrfText;
}

const data = new URLSearchParams({
    'jsonp': 'jsonp',
    'csrf': getCsrf()
});

let xhr = new XMLHttpRequest();
xhr.withCredentials = true;
xhr.open('POST', 'https://api.bilibili.com/x/v2/history/toview/clear');
xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
xhr.onload = function () {
    console.log(xhr.response);
};

xhr.send(data);