
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


            xhr.onload = function () {
                updateDiagnosticInfo(`点赞：${xhr.responseText}<br>`); // 更新诊断信息
                console.log(`点赞：${xhr.responseText}`); // 更新诊断信息
                output += `点赞：${xhr.responseText}\n`
            };

// 发送请求
            xhr.send(data.toString());

        }