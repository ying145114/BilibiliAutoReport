// ==UserScript==
// @name         Bilibili举报弹窗屏蔽
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  用于阻止举报成功后的弹窗，使脚本正常运行
// @author       You
// @match        https://www.bilibili.com/*
// @icon         https://i2.hdslb.com/bfs/app/8920e6741fc2808cce5b81bc27abdbda291655d3.png@240w_240h_1c_1s_!web-avatar-space-header.avif
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    // Override window.alert to do nothing
    window.alert = function(str) {
        return;
    };

    // Override window.confirm to always return true
    window.confirm = function(str) {
        return true;
    };

    // Override window.prompt to always return null
    window.prompt = function(str) {
        return null;
    };

    // Add additional overrides as needed

})();
