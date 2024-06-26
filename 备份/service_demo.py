# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : service_demo.py.py
# Time       ：2023/11/14 17:10
# Author     ：yujia
# version    ：python 3.6
# Description：
"""
import base64
import requests

url = "http://localhost:8000/clickOn"

image_path = "docs/res.jpg"
with open(image_path, 'rb') as f:
    t = f.read()

data = {
  "dataType": 1,
  "imageSource": "static.geetest.com/captcha_v3/batch/v3/74358/2024-06-24T22/icon/b1b0a454d9dd45908b2a9d861a6bd90d.jpg",
  "imageID": "string"
}
import json

print(json.dumps(data, ensure_ascii=False, indent=4))
response = requests.post(url, json=data)
print(response.text)