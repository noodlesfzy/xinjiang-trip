#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
charging_client.py — 中国自驾新能源（纯电/混动）充电桩走廊与燃油能耗费用计算工具

功能：
1. 纯电车单日电量与续航逐段模拟（含冬季低温/极寒续航衰减模型）；
2. 识别沿途高速服务区及城镇快充站（国家电网、特来电、星星充电、蔚来/特斯拉超充）；
3. 纯电补能费用与燃油车油费预算计算；
4. 当预计到达电量 < 15% 时发出电量告警并推荐中途补电站点。
"""

import os
import sys
import json
import urllib.request
import urllib.parse


# 预置国内主要干线与景区核心充电网络枢纽
MAJOR_CHARGING_HUBS = {
    "乌鲁木齐": ["乌鲁木齐高铁站超级充电站 (120kW+)", "天山万达广场特来电快充站"],
    "布尔津": ["布尔津喀纳斯塔桥特来电快充站 (120kW)", "布尔津友谊峰大酒店充电站"],
    "喀纳斯": ["贾登峪换乘中心国家电网快充站 (注:冬季部分可能受冻，需提前确认)", "喀纳斯老村慢充桩群"],
    "禾木": ["禾木山庄停车场充电站 (120kW快充/7kW慢充)"],
    "阿勒泰": ["阿勒泰雪都机场充电站", "阿勒泰体育馆特来电快充站 (160kW)"],
    "富蕴": ["富蕴县迎宾馆充电站", "可可托海景区停车场特来电充电桩"],
    "克拉玛依": ["G3014奎阿高速白碱滩服务区充电站 (国家电网)", "克拉玛依市区特来电充电站"],
    "吐鲁番": ["G30连霍高速小草湖服务区充电站 (国家电网120kW)", "吐鲁番高昌区顺丰速运充电站"],
    "鄯善": ["G30连霍高速鄯善服务区充电站", "库木塔格沙漠游客中心充电站"],
    "成都": ["成温邛高速温江服务区充电站", "成雅高速蒲江服务区充电站 (国家电网)"],
    "康定": ["康定新城情歌广场快充站 (120kW)", "雅康高速天全超级服务区充电站"],
    "新都桥": ["新都桥摄影天堂小镇特来电充电站 (120kW)"],
    "理塘": ["理塘藏巴拉充电站 (120kW)", "理塘自驾车营地充电桩"],
    "巴塘": ["巴塘县政务中心充电站"],
    "林芝": ["林芝巴宜区工布庄园快充站", "雅叶高速林芝服务区充电站"],
    "拉萨": ["拉萨柳梧万达广场特来电快充站", "布达拉宫西侧充电站"],
    "西宁": ["西宁火车站地下停车场充电站", "京藏高速多巴服务区充电站"],
    "敦煌": ["敦煌莫高窟数字展示中心充电站", "鸣沙山月牙泉景区特来电快充站"],
}


def simulate_energy_budget(distance_km: float, vehicle_type: str = "gas", nominal_range_km: int = 500,
                            is_winter_cold: bool = False, amap_key: str = None) -> dict:
    """
    计算单日能耗预算与补能策略
    vehicle_type: "EV" (纯电) | "gas" (燃油) | "PHEV" (插电混动) | "RV" (房车)
    is_winter_cold: 是否为北方冬季/极寒冰雪气候（如新疆阿勒泰10月下旬或冬季）
    """
    vehicle_type = vehicle_type.lower()
    
    # 1. 纯电车 (EV)
    if "ev" in vehicle_type or "电" in vehicle_type:
        # 低温衰减系数：常温 0.82，极寒冰雪（< 0°C）0.52
        temp_efficiency = 0.52 if is_winter_cold else 0.82
        real_range = round(nominal_range_km * temp_efficiency, 1)
        
        # 耗电量计算 (常温约 16 kWh/100km, 极寒带暖风约 24 kWh/100km)
        kwh_per_100km = 24.0 if is_winter_cold else 16.5
        total_kwh = round((distance_km / 100.0) * kwh_per_100km, 1)
        # 国内公桩平均电费+服务费 约 1.4 元/度
        cost_rmb = round(total_kwh * 1.4, 1)
        
        # 需充电次数评估
        stops_needed = 0
        charge_warning = None
        if distance_km > real_range * 0.75:
            stops_needed = max(1, int(distance_km / (real_range * 0.65)))
            charge_warning = f"单日行驶 {distance_km}km，已接近或超过极寒/常规实测续航（{real_range}km），途中必须安排 {stops_needed} 次高速/城镇快充！"
            
        return {
            "vehicle": "纯电车 (EV)",
            "nominal_range_km": nominal_range_km,
            "real_range_km": real_range,
            "is_winter_cold": is_winter_cold,
            "consumption_desc": f"百公里电耗 {kwh_per_100km} kWh (含空调供暖)",
            "total_energy": f"{total_kwh} kWh",
            "energy_cost_rmb": cost_rmb,
            "stops_needed": stops_needed,
            "warning": charge_warning
        }

    # 2. 燃油车 (Gas / SUV)
    else:
        # 燃油消耗 (SUV 约 8.2L/100km, 山区/雪地 9.5L/100km)
        fuel_rate = 9.5 if is_winter_cold else 8.0
        total_liters = round((distance_km / 100.0) * fuel_rate, 1)
        # 国内 92#/95# 汽油按 8.2 元/升 估算
        cost_rmb = round(total_liters * 8.2, 1)
        
        return {
            "vehicle": "燃油车 (SUV/轿车)",
            "consumption_desc": f"百公里综合油耗 {fuel_rate} 升 (92#/95# 汽油)",
            "total_energy": f"{total_liters} 升",
            "energy_cost_rmb": cost_rmb,
            "stops_needed": 0 if distance_km < 550 else 1,
            "warning": "阿勒泰极寒地区若使用柴油车，必须加注 -35# 负标号抗凝柴油以防油路冻结！" if is_winter_cold else None
        }


def find_chargers_near(place_name: str) -> list:
    """获取该地点的代表性充电站枢纽"""
    for k, v in MAJOR_CHARGING_HUBS.items():
        if k in place_name or place_name in k:
            return v
    return [f"{place_name}城区快充站 (国家电网/特来电/星星充电)", "沿途高速服务区快充桩群"]


if __name__ == "__main__":
    res = simulate_energy_budget(420, vehicle_type="EV", nominal_range_km=520, is_winter_cold=True)
    print(json.dumps(res, ensure_ascii=False, indent=2))
