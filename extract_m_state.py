#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re
from pathlib import Path
from curl_cffi import requests

COOKIE_FILE = Path.home() / ".cn-scraper-cookies" / "dianping.json"
cookies = json.load(open(COOKIE_FILE)) if COOKIE_FILE.exists() else {}
session = requests.Session(impersonate="chrome")
headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
    "Referer": "https://m.dianping.com/",
    "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
}

resp = session.get("https://m.dianping.com/search/keyword/325/0_%E6%A5%BC%E5%85%B0%E7%A7%98%E7%83%A4", headers=headers)
scripts = re.findall(r'<script[^>]*>(.*?)</script>', resp.text, re.S)
for s in scripts:
    if "shopId" in s or "shopUuid" in s or "poi" in s:
        print("Found script snippet:", s[:500])
        # 提取 shopId 或 shopUuid
        ids = re.findall(r'["\']shopUuid["\']\s*:\s*["\']([^"\']+)["\']|["\']shopId["\']\s*:\s*(\d+)', s)
        print("Extracted ids:", ids)
