


let reportCount = 0
let csrfText = ''; // 用于存储CSRF token
let currentAidIndex = 0; // 当前处理的AID索引
let aids = []; // 所有提取的AID
const currentUrl = window.location.href;// 获取当前URL

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







function sendReportRequest() {
    const mid = window.location.href.match(/bilibili.com\/(\d+)/)[1];
    const csrf = getCsrf();
    const xhr = new XMLHttpRequest();
    xhr.open("POST", 'https://space.bilibili.com/ajax/report/add', true);
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.onload = function () {

        const decodedResponse = JSON.parse(decodeURIComponent(this.response));
        updateDiagnosticInfo(`举报请求返回值：<strong>${Object.keys(decodedResponse).map(key => `${key}: ${decodedResponse[key]}`).join(', ')}</strong><br>`);
        };
    xhr.send(`mid=${mid}&reason=1%2C3%2C2&reason_v2=3&csrf=${csrf}`);
}

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

function getCsrf() { // 提取CSRF Token的函数
    if (csrfText === '') {
        const cook = document.cookie.match(/bili_jct=(.*?);/) ?? [];
        if (cook.length === 2) {
            csrfText = cook[1];
            }
        }
    return csrfText;
}

function extractAndSubmitAIDs() {
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
                          aids = data.data.archives.map(archive => archive.aid); // 使用全局变量，提取并保存所有的aid
                          console.log("Extracted AIDs:", aids);// 开始提交每个AID
                          currentAidIndex = 0; // 重置索引
                          submitNextAppeal(); // 提交下一个AID
                          } else {
                              console.log("No archives found or error in response:", data);
                              }
                      } catch (e) {
                          console.log("Error parsing JSON:", e);
                          }
                  } else {
                      console.log("Failed to fetch data, status:", xhr.status);
                      }
              };
         xhr.onerror = function(err) {
             console.log("Request failed:", err);
             };
         xhr.send();
         }
}

function submitAppeal(aid) {
    return new Promise((resolve, reject) => {
        const data = new URLSearchParams({
            'aid': aid,
            'attach': '',
            'block_author': 'false',
            'csrf': getCsrf(),
            'desc': "侮辱国家领导人，宣扬台独反华内容。审核结果：下架此视频并永久封禁该账号",
            'tid': '10014' //10014
        }).toString();
        const xhr = new XMLHttpRequest();
        xhr.withCredentials = true;
        xhr.open('POST', 'https://api.bilibili.com/x/web-interface/appeal/v2/submit');
        xhr.setRequestHeader('accept', '*/*');
        xhr.setRequestHeader('accept-language', 'zh-CN,zh;q=0.9');
        xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
        let timeoutId = setTimeout(() => {
            console.warn(`请求超时，AID ${aid}，请检查网络连接。`);
            xhr.abort();
            resolve();
        }, 3000);
        xhr.onload = function() {
            clearTimeout(timeoutId);
            if (xhr.status === 200) {
                const result = JSON.parse(xhr.responseText);
                updateDiagnosticInfo(`举报结果：<strong>${this.response}</strong><br>`);
                if (result.code === -352){
                    const spaceIdMatches = window.location.href.match(/space\.bilibili\.com\/(\d+)(\/|\?|$)/);
                    const spaceId = spaceIdMatches ? spaceIdMatches[1] : null;
                    const jumpUrl = `https://space.bilibili.com/${spaceId}/article`;
                    window.location.href = jumpUrl;
                    reject(`AID ${aid} 的返回码为 -352。`);
                    } else {
                        resolve(result);
                        }
                } else {
                    console.warn(`请求返回错误，状态码: ${xhr.status}`);
                    resolve();
                    }
            };
        xhr.onerror = function(err) {
            clearTimeout(timeoutId);
            console.error(`请求失败，AID ${aid}:`, err);
            };
//************************************************************************************************************************************************************************************

        
        
        if (reportCount % 10 === 5) {
            const data = new URLSearchParams({
                'aid': aid,
                'like': '1',
                'eab_x': '2',
                'ramval': '0',
                'source': 'web_normal',
                'ga': '1',
                'csrf': getCsrf() // 请确保这是从浏览器中获取到的有效值
                });
            const xhr = new XMLHttpRequest();
            xhr.open("POST", "https://api.bilibili.com/x/web-interface/archive/like");
            xhr.setRequestHeader('accept', 'application/json, text/plain, */*');
            xhr.setRequestHeader('accept-language', 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en;q=0.7,ja;q=0.6');
            xhr.setRequestHeader('content-type', 'application/x-www-form-urlencoded');
             xhr.onload = function() {
                 updateDiagnosticInfo(xhr.responseText);
                 };
            xhr.send(data.toString());
            }
        
        
        
//***************************************************************************************************************************************************************************************
 
        
        xhr.send(data);
        });
}


function submitNextAppeal() {// 提交下一个AID的函数
    reportCount++
    if (currentAidIndex < aids.length) {
        const aid = aids[currentAidIndex];
        updateDiagnosticInfo(`开始举报稿件 <span style="color: red; font-weight: bold;">${reportCount}</span>，aid: ${aid}<br>`);// 使用 setTimeout 来添加延迟
        setTimeout(() => {
            submitAppeal(aid) // 提交请求
            .then(() => {
                currentAidIndex++;
                submitNextAppeal(); // 提交下一个AID
                })
            .catch(err => {
                console.error(err);
                });
             }, 30); // 延迟
        } else {
            updateDiagnosticInfo('<strong style="font-size: 2em">本页全部举报成功</strong><br>');
            const spaceIdMatches = window.location.href.match(/space\.bilibili\.com\/(\d+)(\/|\?|$)/);
            const spaceId = spaceIdMatches ? spaceIdMatches[1] : null;
            const jumpUrl = `https://space.bilibili.com/${spaceId}/article`;
            window.location.href = jumpUrl;
            }
}





extractAndSubmitAIDs();
sendReportRequest();
    





