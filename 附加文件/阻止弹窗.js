// ==UserScript==
// @name         阻止弹窗
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  用于阻止举报成功后的弹窗，使脚本正常运行
// @author       You
// @match        *://*/*
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
