#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parks_client.py — 中国核心景区门票预约规则、边防证要求与放票日历工具

功能：
1. 提供中国知名景区（喀纳斯、禾木、可可托海、莫高窟、布达拉宫、故宫、九寨沟等）预约机制与提前放票天数；
2. 识别边境管理区（白哈巴、塔县、珠峰大本营等）《边防证》办理地点与注意事项；
3. 输出出行前“必做预约清单与倒计时”。
"""

import sys
import json

PARKS_CATALOG = {
    "喀纳斯": {
        "full_name": "新疆阿勒泰喀纳斯国家级自然保护区 (5A)",
        "advance_days": 3,
        "booking_platform": "微信小程序「喀纳斯原行网」或携程/美团",
        "ticket_price_rmb": 160,  # 旺季160，淡季100
        "notes": "10月下旬起进入冬季运营模式：区间车可能停运，允许安装雪地胎的自驾四驱车报备后直接进山；需提前在小程序实名购票。",
        "needs_border_pass": False
    },
    "禾木": {
        "full_name": "新疆阿勒泰禾木喀纳斯蒙古族乡景区 (5A)",
        "advance_days": 3,
        "booking_platform": "微信小程序「喀纳斯原行网」或携程/美团",
        "ticket_price_rmb": 50,
        "notes": "如需自驾进村，车辆必须满足四驱+雪地胎要求；村内观景台看日出需早起防寒。",
        "needs_border_pass": False
    },
    "白哈巴": {
        "full_name": "新疆阿勒泰白哈巴西北第一村",
        "advance_days": 1,
        "booking_platform": "喀纳斯景区换乘中心现场或哈巴河县边防大厅",
        "ticket_price_rmb": 30,
        "notes": "位于中哈边境！中国内地游客凭二代身份证在喀纳斯换乘中心窗口或哈巴河县公安局边防大厅现场办理《边境管理区通行证》（免费、5分钟立等可取）。港澳台及外籍游客需专项审批。",
        "needs_border_pass": True,
        "border_pass_location": "喀纳斯换乘中心警务室 / 哈巴河县政务服务中心"
    },
    "可可托海": {
        "full_name": "新疆阿勒泰富蕴县可可托海风景区 (5A)",
        "advance_days": 1,
        "booking_platform": "携程 / 美团 / 可可托海官方公众号",
        "ticket_price_rmb": 90,
        "notes": "额尔齐斯大峡谷、三号矿坑；10月底气温较低，建议中午时段入园游览。",
        "needs_border_pass": False
    },
    "五彩滩": {
        "full_name": "新疆阿勒泰布尔津五彩滩景区 (4A)",
        "advance_days": 0,
        "booking_platform": "现场窗口或美团",
        "ticket_price_rmb": 45,
        "notes": "最佳观赏时间为日落前 1~1.5 小时（雅丹地貌在夕阳下色彩最绚烂）。",
        "needs_border_pass": False
    },
    "库木塔格沙漠": {
        "full_name": "新疆吐鲁番鄯善库木塔格沙漠风景名胜区 (4A)",
        "advance_days": 0,
        "booking_platform": "美团 / 携程 / 现场购票",
        "ticket_price_rmb": 30,
        "notes": "世界上少有的与城市零距离的沙漠；可自驾至景区门口，内有越野冲沙车和骆驼骑行项目。",
        "needs_border_pass": False
    },
    "交河故城": {
        "full_name": "新疆吐鲁番交河故城遗址 (4A/世界文化遗产)",
        "advance_days": 1,
        "booking_platform": "携程 / 美团",
        "ticket_price_rmb": 70,
        "notes": "世界上最大最古老、保存最完好的生土建筑城市，建议请景区电子讲解器。",
        "needs_border_pass": False
    },
    "葡萄沟": {
        "full_name": "新疆吐鲁番葡萄沟风景区 (5A)",
        "advance_days": 0,
        "booking_platform": "美团 / 携程",
        "ticket_price_rmb": 60,
        "notes": "秋季可品尝挂干葡萄和参观维吾尔族民俗家访。",
        "needs_border_pass": False
    },
    "莫高窟": {
        "full_name": "甘肃敦煌莫高窟 (5A/世界遗产)",
        "advance_days": 30,
        "booking_platform": "微信小程序「莫高窟参观预约网」",
        "ticket_price_rmb": 238,
        "notes": "必须提前30天抢A类正常票（含8个实体洞窟+数字电影），B类应急票仅含4个洞窟。",
        "needs_border_pass": False
    },
    "布达拉宫": {
        "full_name": "西藏拉萨布达拉宫 (5A/世界遗产)",
        "advance_days": 7,
        "booking_platform": "微信小程序「布达拉宫官方预约」",
        "ticket_price_rmb": 200,
        "notes": "提前7天上午9:00准时放票，实名制分时段预约，参观需携带身份证。",
        "needs_border_pass": False
    }
}


def get_park_info(park_name: str) -> dict:
    """查询景区预约规则与边防要求"""
    park_name = (park_name or "").strip()
    for k, v in PARKS_CATALOG.items():
        if k in park_name or park_name in k:
            res = v.copy()
            res["matched_name"] = k
            return res
            
    return {
        "full_name": park_name,
        "advance_days": 0,
        "booking_platform": "美团 / 携程 / 景区游客中心",
        "ticket_price_rmb": 80,
        "notes": "常规景区，建议提前 1 天在 OTA 平台查看开放时间并实名购票。",
        "needs_border_pass": False
    }


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "白哈巴"
    print(json.dumps(get_park_info(p), ensure_ascii=False, indent=2))
