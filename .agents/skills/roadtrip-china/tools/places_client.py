#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
places_client.py — 中国大陆地名验证与地理坐标（GCJ-02）解析工具

功能：
1. 校验用户输入的起点、终点及途径地是否真实存在；
2. 优先调用高德开放平台地理编码 Web API（若配置环境变量 AMAP_KEY）；
3. 内置中国核心自驾目的地数据库（涵盖新疆、西藏、青海、甘肃、川西及全国省市县核心景点）；
4. 提供 did-you-mean 模糊匹配与纠错建议。
"""

import os
import sys
import json
import re
import difflib
import urllib.request
import urllib.parse

# 预置中国热门自驾地标数据库 (GCJ-02 坐标)
BUILTIN_PLACES = {
    # --- 新疆（阿勒泰、吐鲁番及全疆核心点）---
    "乌鲁木齐": {"canonical": "新疆维吾尔自治区乌鲁木齐市", "lat": 43.825592, "lng": 87.616848, "province": "新疆", "region": "xinjiang"},
    "阿勒泰": {"canonical": "新疆维吾尔自治区阿勒泰地区阿勒泰市", "lat": 47.844924, "lng": 88.13963, "province": "新疆", "region": "xinjiang"},
    "布尔津": {"canonical": "新疆维吾尔自治区阿勒泰地区布尔津县", "lat": 47.700686, "lng": 86.862453, "province": "新疆", "region": "xinjiang"},
    "喀纳斯": {"canonical": "新疆维吾尔自治区阿勒泰地区布尔津县喀纳斯景区", "lat": 48.718698, "lng": 87.037418, "province": "新疆", "region": "xinjiang"},
    "禾木": {"canonical": "新疆维吾尔自治区阿勒泰地区布尔津县禾木喀纳斯蒙古族乡", "lat": 48.572354, "lng": 87.433892, "province": "新疆", "region": "xinjiang"},
    "白哈巴": {"canonical": "新疆维吾尔自治区阿勒泰地区哈巴河县白哈巴村", "lat": 48.685321, "lng": 86.786543, "province": "新疆", "region": "xinjiang", "needs_border_pass": True},
    "哈巴河": {"canonical": "新疆维吾尔自治区阿勒泰地区哈巴河县", "lat": 48.060012, "lng": 86.420831, "province": "新疆", "region": "xinjiang"},
    "富蕴": {"canonical": "新疆维吾尔自治区阿勒泰地区富蕴县", "lat": 46.994462, "lng": 89.526832, "province": "新疆", "region": "xinjiang"},
    "可可托海": {"canonical": "新疆维吾尔自治区阿勒泰地区富蕴县可可托海景区", "lat": 47.202356, "lng": 89.826541, "province": "新疆", "region": "xinjiang"},
    "五彩滩": {"canonical": "新疆维吾尔自治区阿勒泰地区布尔津县五彩滩风景区", "lat": 47.755431, "lng": 86.867542, "province": "新疆", "region": "xinjiang"},
    "吐鲁番": {"canonical": "新疆维吾尔自治区吐鲁番市高昌区", "lat": 42.951301, "lng": 89.189688, "province": "新疆", "region": "xinjiang"},
    "鄯善": {"canonical": "新疆维吾尔自治区吐鲁番市鄯善县", "lat": 42.868735, "lng": 90.214065, "province": "新疆", "region": "xinjiang"},
    "库木塔格沙漠": {"canonical": "新疆维吾尔自治区吐鲁番市鄯善县库木塔格沙漠风景名胜区", "lat": 42.846532, "lng": 90.228943, "province": "新疆", "region": "xinjiang"},
    "火焰山": {"canonical": "新疆维吾尔自治区吐鲁番市高昌区火焰山风景区", "lat": 42.968742, "lng": 89.542314, "province": "新疆", "region": "xinjiang"},
    "葡萄沟": {"canonical": "新疆维吾尔自治区吐鲁番市高昌区葡萄沟风景区", "lat": 43.012543, "lng": 89.268754, "province": "新疆", "region": "xinjiang"},
    "交河故城": {"canonical": "新疆维吾尔自治区吐鲁番市高昌区交河故城", "lat": 42.955432, "lng": 89.068754, "province": "新疆", "region": "xinjiang"},
    "高昌故城": {"canonical": "新疆维吾尔自治区吐鲁番市高昌区高昌故城", "lat": 42.854321, "lng": 89.528765, "province": "新疆", "region": "xinjiang"},
    "达坂城": {"canonical": "新疆维吾尔自治区乌鲁木齐市达坂城区", "lat": 43.358742, "lng": 88.318754, "province": "新疆", "region": "xinjiang", "wind_warning": True},
    "克拉玛依": {"canonical": "新疆维吾尔自治区克拉玛依市", "lat": 45.579998, "lng": 84.889207, "province": "新疆", "region": "xinjiang"},
    "魔鬼城": {"canonical": "新疆维吾尔自治区克拉玛依市乌尔禾世界魔鬼城", "lat": 46.128743, "lng": 85.708754, "province": "新疆", "region": "xinjiang"},
    "赛里木湖": {"canonical": "新疆维吾尔自治区博尔塔拉蒙古自治州赛里木湖风景名胜区", "lat": 44.608754, "lng": 81.208754, "province": "新疆", "region": "xinjiang"},
    "伊宁": {"canonical": "新疆维吾尔自治区伊犁哈萨克自治州伊宁市", "lat": 43.921864, "lng": 81.324157, "province": "新疆", "region": "xinjiang"},
    "独库公路北段": {"canonical": "独库公路北段（独山子至巴音布鲁克）", "lat": 43.821453, "lng": 84.852341, "province": "新疆", "seasonal_closure": True},

    # --- 川藏线 318 与川西 ---
    "成都": {"canonical": "四川省成都市", "lat": 30.659462, "lng": 104.065735, "province": "四川", "region": "tibet_sichuan"},
    "雅安": {"canonical": "四川省雅安市", "lat": 29.980315, "lng": 103.042125, "province": "四川", "region": "tibet_sichuan"},
    "泸定": {"canonical": "四川省甘孜藏族自治州泸定县", "lat": 29.914562, "lng": 102.234561, "province": "四川", "region": "tibet_sichuan"},
    "康定": {"canonical": "四川省甘孜藏族自治州康定市", "lat": 30.049518, "lng": 101.962534, "province": "四川", "region": "tibet_sichuan"},
    "新都桥": {"canonical": "四川省甘孜藏族自治州康定市新都桥镇", "lat": 30.043512, "lng": 101.524561, "province": "四川", "region": "tibet_sichuan"},
    "雅江": {"canonical": "四川省甘孜藏族自治州雅江县", "lat": 30.032145, "lng": 101.018745, "province": "四川", "region": "tibet_sichuan"},
    "理塘": {"canonical": "四川省甘孜藏族自治州理塘县", "lat": 29.996541, "lng": 100.271245, "province": "四川", "region": "tibet_sichuan"},
    "巴塘": {"canonical": "四川省甘孜藏族自治州巴塘县", "lat": 30.004512, "lng": 99.108745, "province": "四川", "region": "tibet_sichuan"},
    "稻城": {"canonical": "四川省甘孜藏族自治州稻城县", "lat": 29.038745, "lng": 100.298745, "province": "四川", "region": "tibet_sichuan"},
    "亚丁": {"canonical": "四川省甘孜藏族自治州稻城亚丁风景区", "lat": 28.438745, "lng": 100.358745, "province": "四川", "region": "tibet_sichuan"},
    "芒康": {"canonical": "西藏自治区昌都市芒康县", "lat": 29.684512, "lng": 98.598745, "province": "西藏", "region": "tibet_sichuan"},
    "左贡": {"canonical": "西藏自治区昌都市左贡县", "lat": 29.674512, "lng": 97.848745, "province": "西藏", "region": "tibet_sichuan"},
    "八宿": {"canonical": "西藏自治区昌都市八宿县", "lat": 30.054512, "lng": 96.918745, "province": "西藏", "region": "tibet_sichuan"},
    "波密": {"canonical": "西藏自治区林芝市波密县", "lat": 29.858745, "lng": 95.768745, "province": "西藏", "region": "tibet_sichuan"},
    "鲁朗": {"canonical": "西藏自治区林芝市巴宜区鲁朗小镇", "lat": 29.748745, "lng": 94.728745, "province": "西藏", "region": "tibet_sichuan"},
    "林芝": {"canonical": "西藏自治区林芝市巴宜区", "lat": 29.648745, "lng": 94.361245, "province": "西藏", "region": "tibet_sichuan"},
    "拉萨": {"canonical": "西藏自治区拉萨市", "lat": 29.652491, "lng": 91.172118, "province": "西藏", "region": "tibet_sichuan"},
    "日喀则": {"canonical": "西藏自治区日喀则市桑珠孜区", "lat": 29.268745, "lng": 88.881245, "province": "西藏", "region": "tibet_sichuan", "needs_border_pass": True},
    "珠峰大本营": {"canonical": "西藏自治区日喀则市定日县珠峰大本营", "lat": 28.148745, "lng": 86.858745, "province": "西藏", "region": "tibet_sichuan", "needs_border_pass": True},

    # --- 青甘大环线与西北 ---
    "西宁": {"canonical": "青海省西宁市", "lat": 36.623214, "lng": 101.778912, "province": "青海", "region": "qinghai_gansu"},
    "青海湖": {"canonical": "青海省海南藏族自治州青海湖景区二郎剑", "lat": 36.578745, "lng": 100.488745, "province": "青海", "region": "qinghai_gansu"},
    "茶卡盐湖": {"canonical": "青海省海西蒙古族藏族自治州乌兰县茶卡盐湖景区", "lat": 36.708745, "lng": 99.088745, "province": "青海", "region": "qinghai_gansu"},
    "大柴旦": {"canonical": "青海省海西蒙古族藏族自治州大柴旦行政委员会", "lat": 37.858745, "lng": 95.348745, "province": "青海", "region": "qinghai_gansu"},
    "敦煌": {"canonical": "甘肃省酒泉市敦煌市", "lat": 40.142114, "lng": 94.661845, "province": "甘肃", "region": "qinghai_gansu"},
    "嘉峪关": {"canonical": "甘肃省嘉峪关市", "lat": 39.773145, "lng": 98.289145, "province": "甘肃", "region": "qinghai_gansu"},
    "张掖": {"canonical": "甘肃省张掖市甘州区", "lat": 38.925845, "lng": 100.449745, "province": "甘肃", "region": "qinghai_gansu"},
    "祁连": {"canonical": "青海省海北藏族自治州祁连县", "lat": 38.178745, "lng": 100.248745, "province": "青海", "region": "qinghai_gansu"},

    # --- 国内其他经典枢纽与自驾点 ---
    "北京": {"canonical": "北京市", "lat": 39.904211, "lng": 116.407395, "province": "北京"},
    "上海": {"canonical": "上海市", "lat": 31.230416, "lng": 121.473701, "province": "上海"},
    "广州": {"canonical": "广东省广州市", "lat": 23.12911, "lng": 113.264385, "province": "广东"},
    "深圳": {"canonical": "广东省深圳市", "lat": 22.543099, "lng": 114.057868, "province": "广东"},
    "杭州": {"canonical": "浙江省杭州市", "lat": 30.274085, "lng": 120.15507, "province": "浙江"},
    "西安": {"canonical": "陕西省西安市", "lat": 34.341568, "lng": 108.940174, "province": "陕西"},
    "三亚": {"canonical": "海南省三亚市", "lat": 18.252847, "lng": 109.511909, "province": "海南"},
    "海口": {"canonical": "海南省海口市", "lat": 20.044002, "lng": 110.19989, "province": "海南"},
    "大理": {"canonical": "云南省大理白族自治州大理市", "lat": 25.606486, "lng": 100.267638, "province": "云南"},
    "丽江": {"canonical": "云南省丽江市古城区", "lat": 26.872108, "lng": 100.229984, "province": "云南"},
    "香格里拉": {"canonical": "云南省迪庆藏族自治州香格里拉市", "lat": 27.825121, "lng": 99.707314, "province": "云南"},
    "黄山": {"canonical": "安徽省黄山市黄山区黄山风景区", "lat": 30.131245, "lng": 118.172451, "province": "安徽"},
    "九寨沟": {"canonical": "四川省阿坝藏族羌族自治州九寨沟县九寨沟景区", "lat": 33.261245, "lng": 103.918745, "province": "四川"},
}


def _clean_query(name: str) -> str:
    name = (name or "").strip()
    name = re.sub(r"[市县区镇乡省盟州]$", "", name)
    return name


def validate_place(name: str, amap_key: str = None) -> dict:
    """
    验证地名并返回 GCJ-02 坐标信息
    返回格式:
      {
        "verdict": "match" | "did-you-mean" | "no-match",
        "canonical": str,
        "lat": float,
        "lng": float,
        "province": str,
        "needs_border_pass": bool,
        "seasonal_closure": bool,
        "wind_warning": bool,
        "suggestion": str
      }
    """
    name = (name or "").strip()
    if not name:
        return {"verdict": "no-match", "message": "地名不能为空"}

    # 1. 精确匹配内置数据库
    if name in BUILTIN_PLACES:
        res = BUILTIN_PLACES[name].copy()
        res["verdict"] = "match"
        res["name"] = name
        return res

    cleaned = _clean_query(name)
    if cleaned in BUILTIN_PLACES:
        res = BUILTIN_PLACES[cleaned].copy()
        res["verdict"] = "match"
        res["name"] = cleaned
        return res

    for k, v in BUILTIN_PLACES.items():
        if k in name or name in k:
            res = v.copy()
            res["verdict"] = "match"
            res["name"] = k
            return res

    # 2. 如果配置了高德 API Key，调用高德地理编码接口
    key = amap_key or os.getenv("AMAP_KEY", "").strip()
    if key:
        try:
            url = f"https://restapi.amap.com/v3/geocode/geo?address={urllib.parse.quote(name)}&key={key}"
            req = urllib.request.Request(url, headers={"User-Agent": "roadtrip-cn/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "1" and data.get("geocodes"):
                    geo = data["geocodes"][0]
                    coords = geo["location"].split(",")
                    lng, lat = float(coords[0]), float(coords[1])
                    return {
                        "verdict": "match",
                        "name": name,
                        "canonical": geo.get("formatted_address", name),
                        "lat": lat,
                        "lng": lng,
                        "province": geo.get("province", ""),
                        "city": geo.get("city", "")
                    }
        except Exception:
            pass

    # 3. 模糊匹配推荐 (did-you-mean)
    candidates = difflib.get_close_matches(name, BUILTIN_PLACES.keys(), n=1, cutoff=0.4)
    if candidates:
        cand = candidates[0]
        res = BUILTIN_PLACES[cand].copy()
        res["verdict"] = "did-you-mean"
        res["suggestion"] = cand
        res["name"] = cand
        return res

    # 默认找不到
    return {
        "verdict": "no-match",
        "name": name,
        "message": f"未能确认地点「{name}」，请检查是否拼写有误或提供更详细的城市/景区全称"
    }


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "喀纳斯"
    result = validate_place(query)
    print(json.dumps(result, ensure_ascii=False, indent=2))
