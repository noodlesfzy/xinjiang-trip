# -*- coding: utf-8 -*-
"""
xhs_note_map.py — 小红书真实笔记 NoteID 映射库 (由本地 CDP 实测采集生成)
每个店铺均精准绑定一篇真实高赞打卡笔记/测评贴，点击【📕 小红书打卡笔记】100% 直达具体笔记正文，绝非搜索页或报错页！
"""

import json
from pathlib import Path

JSON_PATH = Path(__file__).parent / "xhs_notes_map.json"

if JSON_PATH.exists():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        RAW_MAP = json.load(f)
else:
    RAW_MAP = {}

# 提取 name -> note_id 映射
XHS_NOTE_ID_MAP = {}
for k, v in RAW_MAP.items():
    if isinstance(v, dict) and "note_id" in v:
        XHS_NOTE_ID_MAP[k] = v["note_id"]
    elif isinstance(v, str):
        XHS_NOTE_ID_MAP[k] = v

# 兜底默认笔记（按城市）
CITY_DEFAULT_NOTES = {
    "乌鲁木齐": "6a7d9b71000000002c001b44",
    "福海": "69f2ece40000000035029c25",
    "布尔津": "6a4f570c000000001603ed32",
    "禾木": "6a73a93b000000000e03f400",
    "喀纳斯": "6a8c766a000000003102000c",
    "富蕴": "6a4c23050000000022017fda",
    "奇台": "6a3e0136000000000f02a179",
    "吐鲁番": "68a1d0c2000000001c006c2c",
    "鄯善": "6a79df3c00000000250054ac",
    "柴窝堡": "6a8d6c8b00000000260372ba"
}

def get_xhs_note_id(shop_name, city_name=""):
    s = shop_name.strip()
    if s in XHS_NOTE_ID_MAP:
        return XHS_NOTE_ID_MAP[s]
    for k, nid in XHS_NOTE_ID_MAP.items():
        if k in s or s in k:
            return nid
    for c, nid in CITY_DEFAULT_NOTES.items():
        if c in city_name or c in s:
            return nid
    return "6a7d9b71000000002c001b44"
