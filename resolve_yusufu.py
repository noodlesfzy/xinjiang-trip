#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from curl_cffi import requests
import re

urls = [
    ("余苏甫大眼睛烤肉店 [1]", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8LW4kcgwko9fgsB5dhC6S6ZkL5hFoI4ag7gvyVfwoxdLiYFy1MRlGiS5hxEpy7km0pF_nz6iWU5hfCAgNVVkD5DgbkaXSHGHfNxRFNxg29StriLhz6jJh1GQpKIpLZZ7kSFkZDhdtTqJZz9g-bNdg"),
    ("余苏甫大眼睛烤肉店 [2]", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHbqyeUxQf9sUhT1trCpJN30bYxBZowWmZxr1JU6QNtJul2yt-hzQBUfjcTTSrWTlP7rQwqKSJ1PL413lF2N0H_cy0wEzi0lsnmc49xRv--UCaVAVM94_mSX44_5ujwhczH56ejTS2JXSGY48UOs3cfAFb9VLSa-z0ON2jWorQSJZLH"),
    ("余苏甫大眼睛烤肉店 [3]", "https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEw72kbjD-40WwliXZupkkawdUxQLhRiLTfIvydc8LlJl0CiWV2cR-tUAFoCfWw7P92OVWXdNgV9u_TUPc-Rq7mpJIeXoW83b1NWMg6YOmVGyJ9C_6ER-iru66lP8-FUOJABU6q0bz5XZsD6bNFvjgOUp94TwF0Jvpevawg36wYs6WgD8iWc9iExYl_POTXJzDLgZ5kCQ==")
]

session = requests.Session(impersonate="chrome")
for name, u in urls:
    try:
        resp = session.get(u, allow_redirects=False, timeout=10)
        loc = resp.headers.get("Location")
        if loc:
            m = re.search(r'shop/([A-Za-z0-9]+)', loc)
            if m:
                sid = m.group(1)
                resp_shop = session.get(f"https://m.dianping.com/shop/{sid}", headers={"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}, timeout=8)
                t_m = re.search(r'<title>(.*?)</title>', resp_shop.text, re.S)
                title = t_m.group(1).strip() if t_m else "No title"
                print(f"🎯 {name} ➔ ShopID: {sid} ➔ 真实Title: {title}")
    except Exception as e:
        print(f"Error {name}: {e}")
