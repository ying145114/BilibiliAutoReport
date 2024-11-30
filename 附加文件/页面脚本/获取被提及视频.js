var callback = arguments[arguments.length - 1];
let SourceIds = [];
let SubjectIds = [];
let currentAidIndex = 0
let mids = [];


function getCsrf() {
    let csrfText = '';
    const cookieMatch = document.cookie.match(/bili_jct=(.*?);/) ?? [];
    if (cookieMatch.length === 2) {
        csrfText = cookieMatch[1];
    }
    return csrfText;
}


function checkAt() {
    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('GET', 'https://api.vc.bilibili.com/x/im/web/msgfeed/unread?build=0&mobi_app=web');
    xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
    xhr.onload = function () {
        console.log(xhr.response);
        const data = JSON.parse(xhr.response);
        //data.data.at = 2
        if (data.code === 0) {
            console.log(data.data.at)
            if (data.data.at !== 0) {
                getAt(data.data.at)
            }
            else{
                console.log(SubjectIds)
                callback(SubjectIds)
            }
        }
    };
    xhr.send();
}

function getAt(at) {
    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('GET', 'https://api.bilibili.com/x/msgfeed/at?build=0&mobi_app=web');
    xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
    xhr.onload = function () {
        //console.log(xhr.response);
        data = JSON.parse(xhr.response);
        if (data && data.data && data.data.items) {
            // 使用map函数从data.data.items中提取item.source_id和item.subject_id
            SourceIds = data.data.items.slice(0, at).map(item => item.item.source_id);
            SubjectIds = data.data.items.slice(0, at).map(item => item.item.subject_id);
        }

        if (at !== 0) {
            submitNextAppeal()
        }
    };
    xhr.send();
}


function submitNextAppeal() {
    return new Promise((resolve) => {
        if (currentAidIndex < SourceIds.length) {
            console.log(currentAidIndex, SourceIds.length);
            const subject_id = SubjectIds[currentAidIndex];
            const source_id = SourceIds[currentAidIndex];
            setTimeout(() => {
                //fetchMid(subject_id)
                sendComment(subject_id, source_id)

                    .then((shouldContinue) => {
                        if (!shouldContinue) {
                            resolve(); // 直接结束
                            return;     // 退出当前函数
                        }
                        currentAidIndex++;
                        submitNextAppeal().then(resolve);
                    });
            }, 1000);
        } else {
            resolve(); // 完成后解除 Promise
            console.log('完成')
            console.log(SubjectIds)
            callback(SubjectIds)
        }
    });
}

function sendComment(subject_id, source_id) {
    return new Promise((resolve) => {
        console.log(subject_id, source_id)
        const dataObj = {
            plat: 1,
            oid: subject_id,
            type: 1,
            root: source_id,
            parent: source_id,
            message: '[OK]',
            at_name_to_mid: JSON.stringify({}), // 将对象转换为 JSON 字符串
            //sync_to_dynamic: 1,
            gaia_source: 'main_web',
            csrf: getCsrf(),
            statistics: JSON.stringify({appId: 100, platform: 5}) // 转换 statistics 对象为 JSON 字符串
        };
        const data = new URLSearchParams(dataObj).toString();


        let xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open('POST', 'https://api.bilibili.com/x/v2/reply/add?');
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
        xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');

        xhr.onload = function () {
            console.log('评论', xhr.response);
            resolve(true);
        };

        xhr.send(data);
    });

}

function fetchMid(subject_id) {
    let xhr = new XMLHttpRequest();
    xhr.withCredentials = true;
    xhr.open('GET', 'https://api.bilibili.com/x/web-interface/view?aid=85440373');
    xhr.setRequestHeader('accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7');
    xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
    xhr.setRequestHeader('cache-control', 'max-age=0');
    xhr.onload = function() {
        //console.log(xhr.response);
        const data = JSON.parse(xhr.responseText);
        if (data && data.data && data.data.owner && data.data.owner.mid) {
            mids.push(data.data.owner.mid);
        }


    };

    xhr.send();

}


checkAt();


