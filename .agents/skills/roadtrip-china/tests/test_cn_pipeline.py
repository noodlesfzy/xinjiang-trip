#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_cn_pipeline.py — 中国自驾技能各工具模块与完整流水线自动化测试
"""

import os
import sys
import unittest

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)

from tools.places_client import validate_place
from tools.routing_client import get_route
from tools.elevation_client import evaluate_altitude_safety
from tools.charging_client import simulate_energy_budget
from tools.weather_client import get_weather_forecast
from tools.parks_client import get_park_info
from scripts.helper import parse_slots
from scripts.planner import build_xinjiang_14d_itinerary
from scripts.generate_html import render_html


class TestRoadTripChina(unittest.TestCase):

    def test_places_validation(self):
        # 1. 正常匹配
        res = validate_place("喀纳斯")
        self.assertEqual(res["verdict"], "match")
        self.assertAlmostEqual(res["lat"], 48.718, places=2)

        # 2. 边防证检测
        res_border = validate_place("白哈巴")
        self.assertTrue(res_border.get("needs_border_pass"))

        # 3. 纠错推荐
        res_didyoumean = validate_place("克拉玛")
        self.assertIn(res_didyoumean["verdict"], ["match", "did-you-mean"])

    def test_routing_and_tolls(self):
        # 乌鲁木齐 -> 布尔津
        route = get_route(43.825592, 87.616848, 47.700686, 86.862453)
        self.assertGreater(route["distance_km"], 400)
        self.assertGreater(route["duration_hours"], 4.0)
        self.assertGreater(route["tolls_rmb"], 50.0)

    def test_altitude_evaluation(self):
        # 理塘 (4014m) 应该触发极高风险预警
        litang = evaluate_altitude_safety("理塘", previous_elevation=500, is_overnight=True)
        self.assertEqual(litang["risk_level"], "severe")

        # 吐鲁番 (30m) 应该为安全
        turpan = evaluate_altitude_safety("吐鲁番", previous_elevation=918, is_overnight=True)
        self.assertEqual(turpan["risk_level"], "safe")

    def test_energy_simulation(self):
        # 纯电车冬季极寒衰减测试
        ev_res = simulate_energy_budget(400, vehicle_type="EV", nominal_range_km=500, is_winter_cold=True)
        self.assertLess(ev_res["real_range_km"], 300) # 低温下实测小于 300km

    def test_weather_and_parks(self):
        w = get_weather_forecast("喀纳斯")
        self.assertIn("雪", w["weather"])
        p = get_park_info("白哈巴")
        self.assertTrue(p["needs_border_pass"])

    def test_slots_parser(self):
        text = "我下一个行程会在2025.10.25到11.07去新疆的阿勒泰和吐鲁番地区，14天自驾游"
        slots = parse_slots(text)
        self.assertEqual(slots["days"], 14)
        self.assertEqual(slots["region"], "xinjiang")
        self.assertEqual(slots["date"], "2025-10-25")

    def test_full_pipeline_html_generation(self):
        data = build_xinjiang_14d_itinerary()
        self.assertEqual(len(data["days"]), 14)
        out_file = os.path.join(base_dir, "tests", "test_output_trip.html")
        render_html(data, output_path=out_file)
        self.assertTrue(os.path.exists(out_file))
        self.assertGreater(os.path.getsize(out_file), 5000)


if __name__ == "__main__":
    unittest.main()
