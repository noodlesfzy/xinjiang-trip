#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_xinjiang_demo.py — 针对用户 2025.10.25 - 11.07 新疆阿勒泰 + 吐鲁番 14 天自驾的专属路书生成与演示脚本
"""

import os
import sys
import json

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from scripts.planner import build_xinjiang_14d_itinerary
from scripts.generate_html import render_html


def generate_user_demo():
    print("🚀 正在规划 2025.10.25 - 11.07 新疆阿勒泰 + 吐鲁番 14 天自驾行程...")
    trip_data = build_xinjiang_14d_itinerary(start_date_str="2025-10-25", vehicle_type="燃油四驱SUV (配备雪地胎)")

    # 导出 JSON 数据
    project_root = "/Users/Noodles/Documents/AG_Project"
    json_path = os.path.join(project_root, "xinjiang_14d_itinerary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(trip_data, f, ensure_ascii=False, indent=2)
    print(f"📊 已生成完整结构化行程数据: {json_path}")

    # 渲染单文件 HTML
    html_path = os.path.join(project_root, "xinjiang_14d_itinerary.html")
    render_html(trip_data, output_path=html_path)
    print(f"🎉 已成功生成全景交互式路书网页: {html_path}")
    print("\n行程亮点与关键指标汇总：")
    print(f"  - 总天数: {trip_data['total_days']} 天 ({trip_data['dates']})")
    print(f"  - 覆盖区域: {trip_data['region']}")
    print(f"  - 总行驶里程: {trip_data['summary']['total_distance_km']} km")
    print(f"  - 预估驾驶总耗时: {trip_data['summary']['total_driving_hours']} 小时")
    print(f"  - 预估高速过路费: ¥{trip_data['summary']['total_tolls_rmb']}")
    print(f"  - 预估油耗费用: ¥{trip_data['summary']['total_energy_cost_rmb']}")
    print(f"  - 核心安全规则: {len(trip_data['critical_rules'])} 项 (已注入路书首屏)")


if __name__ == "__main__":
    generate_user_demo()
