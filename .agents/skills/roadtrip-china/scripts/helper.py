#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
helper.py — 中国自驾规划请求槽位解析、模式识别与区域主题提取工具

功能：
1. 从用户自然语言中提取：起点、天数、出发日期、随行人员、车型；
2. 识别模式：
   - light mode (从零规划模式)
   - heavy mode (核验已有行程模式，如包含 Day1/Day2 等排期)
3. 匹配中国特色自驾主题区域（新疆、川藏、青甘、云贵、海南等）。
"""

import sys
import json
import re

REQUIRED_SLOTS = ["start", "days", "date", "party", "vehicle"]

REGION_KEYWORDS = {
    "xinjiang": ["新疆", "阿勒泰", "喀纳斯", "禾木", "布尔津", "可可托海", "富蕴", "吐鲁番", "鄯善", "库木塔格", "乌鲁木齐", "伊宁", "赛里木湖", "独库", "南疆", "北疆"],
    "tibet_sichuan": ["川藏", "318", "川西", "成都", "康定", "新都桥", "理塘", "稻城", "亚丁", "拉萨", "林芝", "波密", "然乌湖", "西藏", "日喀则", "珠峰"],
    "qinghai_gansu": ["青甘", "大环线", "西宁", "青海湖", "茶卡", "大柴旦", "敦煌", "莫高窟", "张掖", "祁连", "嘉峪关"],
    "yunnan": ["云南", "滇藏", "大理", "丽江", "香格里拉", "泸沽湖", "丙察察", "西双版纳"],
    "hainan": ["海南", "环岛", "三亚", "海口", "万宁", "陵水"]
}

HEAVY_MODE_PATTERNS = [
    r"day\s*\d+", r"d\d+", r"第[一二三四五六七八九十\d]+天", r"行程如下", r"我的路线", r"帮我核实", r"帮我看看", r"现有行程"
]


def detect_mode(text: str) -> str:
    """判定是 light(新建规划) 还是 heavy(核验已有)"""
    low = text.lower()
    matches = 0
    for p in HEAVY_MODE_PATTERNS:
        matches += len(re.findall(p, low))
    return "heavy" if matches >= 2 else "light"


def detect_region(text: str) -> str:
    """识别自驾区域主题"""
    for region, kws in REGION_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                return region
    return "general"


def parse_slots(text: str) -> dict:
    """提取核心槽位"""
    slots = {
        "start": None,
        "days": None,
        "date": None,
        "party": None,
        "vehicle": None,
        "destinations": [],
        "region": detect_region(text),
        "mode": detect_mode(text)
    }

    # 1. 提取天数
    day_match = re.search(r"(\d+)\s*天", text)
    if day_match:
        slots["days"] = int(day_match.group(1))

    # 2. 提取日期 (如 2025.10.25, 2025-10-25, 10月25日)
    date_match = re.search(r"(20\d{2}[\.\-\/年]\d{1,2}[\.\-\/月]\d{1,2}日?)", text)
    if date_match:
        raw_d = date_match.group(1)
        clean_d = re.sub(r"[年\.\/]", "-", raw_d).replace("月", "-").replace("日", "")
        slots["date"] = clean_d
    else:
        date_short = re.search(r"(\d{1,2}月\d{1,2}日?)", text)
        if date_short:
            slots["date"] = f"2025-{date_short.group(1).replace('月', '-').replace('日', '')}"

    # 3. 提取车型
    if any(k in text.lower() for k in ["电车", "电动", "ev", "特斯拉", "model y", "蔚来", "理想", "小鹏", "极氪"]):
        slots["vehicle"] = "纯电动车 (EV)"
    elif any(k in text for k in ["房车", "rv"]):
        slots["vehicle"] = "房车 (RV)"
    elif any(k in text for k in ["混动", "phev", "增程"]):
        slots["vehicle"] = "插电/增程混动"
    else:
        slots["vehicle"] = "燃油SUV / 轿车"

    # 4. 提取目的地关键词
    for reg, kws in REGION_KEYWORDS.items():
        for kw in kws:
            if kw in text and kw not in slots["destinations"]:
                slots["destinations"].append(kw)

    # 5. 默认补齐
    if not slots["start"]:
        if "乌鲁木齐" in text:
            slots["start"] = "乌鲁木齐"
        elif "成都" in text:
            slots["start"] = "成都"
        elif "西宁" in text:
            slots["start"] = "西宁"
        elif slots["region"] == "xinjiang":
            slots["start"] = "乌鲁木齐"
        else:
            slots["start"] = "待确认起点"

    if not slots["party"]:
        slots["party"] = "2位成人 (自驾出行)"

    # 计算缺失的必填槽位
    missing = []
    if not slots["days"]: missing.append("days (出行天数)")
    if not slots["start"] or slots["start"] == "待确认起点": missing.append("start (出发城市)")

    slots["missing_slots"] = missing
    return slots


if __name__ == "__main__":
    test_input = sys.argv[1] if len(sys.argv) > 1 else "我下一个行程会在2025.10.25到11.07去新疆的阿勒泰和吐鲁番地区，14天自驾游"
    res = parse_slots(test_input)
    print(json.dumps(res, ensure_ascii=False, indent=2))
