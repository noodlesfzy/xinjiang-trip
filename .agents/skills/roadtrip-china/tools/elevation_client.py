#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
elevation_client.py — 中国自驾高程数据库与高原反应过夜安全评估工具

功能：
1. 查询全国自驾核心城市、城镇、垭口与景点的海拔高程（米）；
2. 对单日落脚点及过夜海拔进行高原反应风险等级评估（安全、适中、高风险、极高风险）；
3. 提供海拔爬升阶梯健康建议与制氧装备提醒。
"""

import sys
import json

# 中国核心自驾地标与垭口海拔数据库（单位：米）
ELEVATION_DB = {
    # --- 新疆地区 ---
    "乌鲁木齐": 918,
    "阿勒泰": 735,
    "布尔津": 475,
    "喀纳斯": 1374,
    "禾木": 1124,
    "白哈巴": 1260,
    "贾登峪": 1600,
    "哈巴河": 500,
    "富蕴": 810,
    "可可托海": 1200,
    "克拉玛依": 270,
    "赛里木湖": 2073,
    "伊宁": 640,
    "吐鲁番": 30,
    "鄯善": 410,
    "库木塔格沙漠": 450,
    "火焰山": 100,
    "艾丁湖": -154,

    # --- 川藏线 318 与川西 ---
    "成都": 500,
    "雅安": 580,
    "泸定": 1320,
    "康定": 2560,
    "折多山垭口": 4298,
    "新都桥": 3300,
    "高尔寺山": 4412,
    "雅江": 2530,
    "剪子弯山": 4659,
    "卡子拉山": 4718,
    "理塘": 4014,
    "海子山": 4685,
    "稻城": 3750,
    "亚丁": 2900,
    "巴塘": 2580,
    "竹巴笼": 2500,
    "海通沟": 3200,
    "宗拉山": 4150,
    "芒康": 3875,
    "拉乌山": 4376,
    "觉巴山": 3911,
    "东达山垭口": 5130,
    "左贡": 3800,
    "邦达": 4120,
    "业拉山垭口": 4658,
    "怒江72拐": 3100,
    "八宿": 3260,
    "安久拉山": 4475,
    "然乌湖": 3850,
    "波密": 2725,
    "通麦": 2030,
    "鲁朗": 3385,
    "色季拉山垭口": 4728,
    "林芝": 2900,
    "工布江达": 3440,
    "米拉山垭口": 5018,
    "拉萨": 3650,
    "羊卓雍措": 4441,
    "日喀则": 3836,
    "定日": 4300,
    "珠峰大本营": 5200,

    # --- 青甘大环线 ---
    "西宁": 2261,
    "日月山": 3520,
    "倒淌河": 3200,
    "青海湖": 3200,
    "橡皮山垭口": 3817,
    "茶卡盐湖": 3059,
    "德令哈": 2980,
    "大柴旦": 3174,
    "察尔汗盐湖": 2670,
    "当金山垭口": 3648,
    "敦煌": 1138,
    "嘉峪关": 1650,
    "张掖": 1474,
    "扁都口": 3500,
    "祁连县": 2787,
    "卓尔山": 2950,
    "门源": 2870,
}


def get_elevation(place_name: str) -> int:
    """获取地点海拔（米），若未收录则返回默认估算值"""
    name = (place_name or "").strip()
    if name in ELEVATION_DB:
        return ELEVATION_DB[name]
    
    for k, v in ELEVATION_DB.items():
        if k in name or name in k:
            return v
            
    return 800  # 默认低海拔


def evaluate_altitude_safety(place_name: str, previous_elevation: int = 500, is_overnight: bool = True) -> dict:
    """
    评估落脚点/过夜海拔高反风险
    返回:
      {
        "place": str,
        "elevation_m": int,
        "risk_level": "safe" | "moderate" | "high" | "severe",
        "elevation_gain_m": int,
        "warning": str or None,
        "suggestion": str
      }
    """
    elev = get_elevation(place_name)
    gain = elev - previous_elevation

    if elev < 2000:
        level = "safe"
        warning = None
        suggestion = "低海拔区域，无高原反应风险，适宜舒适过夜。"
    elif 2000 <= elev <= 3000:
        level = "moderate"
        warning = None if gain < 1500 else "单日爬升较大，初入可能稍有耳鸣或轻度头晕。"
        suggestion = "中等海拔，绝大多数人适应良好，建议夜间保暖防着凉。"
    elif 3000 < elev <= 3800:
        level = "high"
        warning = f"落脚点海拔达到 {elev} 米。"
        if is_overnight and previous_elevation < 1500:
            warning += " ⚠️ 从低海拔直接升至 3000m+ 过夜，高反发生率较高！"
        suggestion = "建议避免剧烈运动和饮酒，过夜备好保温壶与便携式氧气瓶。"
    else:
        level = "severe"
        warning = f"🚨 极高海拔警报：海拔达到 {elev} 米！"
        if is_overnight:
            warning += " 强烈不建议初次进高原者在此过夜，易诱发严重高原性失眠与急性高反！"
        suggestion = "如非必要请勿在此过夜，建议日落前下撤至 3000m 以下城镇住宿；随车务必携带医用氧气瓶与血氧仪。"

    return {
        "place": place_name,
        "elevation_m": elev,
        "risk_level": level,
        "elevation_gain_m": gain,
        "warning": warning,
        "suggestion": suggestion
    }


if __name__ == "__main__":
    place = sys.argv[1] if len(sys.argv) > 1 else "理塘"
    res = evaluate_altitude_safety(place, previous_elevation=500, is_overnight=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
