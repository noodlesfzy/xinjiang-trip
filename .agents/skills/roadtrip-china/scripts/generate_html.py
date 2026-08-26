#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_html.py — 将结构化行程数据渲染为单文件 HTML 交互式路书

纯 Python 标准库实现，零第三方包依赖，无模板标签泄漏。
"""

import os
import sys
import json


def render_day_card(d):
    chips_html = "".join([f'<span class="chip">{h}</span>' for h in d.get("highlights", [])])
    
    warning_html = ""
    warnings = d.get("warnings", [])
    if warnings:
        w_lines = "".join([f'<div>{w}</div>' for w in warnings])
        warning_html = f'<div class="card-warning">{w_lines}</div>'

    from_obj = d.get("from_place") or d.get("from", {})
    to_obj = d.get("to_place") or d.get("to", {})
    route_obj = d.get("route", {})
    elev_obj = d.get("elevation", {})
    weather_obj = d.get("weather", {})

    from_lat = from_obj.get("lat", 0)
    from_lng = from_obj.get("lng", 0)
    from_name = from_obj.get("name", "")
    to_lat = to_obj.get("lat", 0)
    to_lng = to_obj.get("lng", 0)
    to_name = to_obj.get("name", "")

    distance_km = route_obj.get("distance_km") or d.get("distance_km", 0)
    duration_text = route_obj.get("duration_text") or d.get("duration", "")
    tolls_rmb = route_obj.get("tolls_rmb") or d.get("tolls_rmb", 0)
    elevation_m = elev_obj.get("elevation_m") or d.get("elevation_m", 0)
    weather_desc = weather_obj.get("weather") or d.get("weather", "")

    card = f"""
      <div class="day-card" id="day-card-{d['day']}" onclick="focusDay({d['day']})">
        <div class="card-top">
          <span class="day-tag">Day {d['day']} · {d.get('weekday', '')}</span>
          <span class="day-date">{d.get('date', '')}</span>
        </div>
        <div class="card-title">{d.get('title', '')}</div>

        <div class="card-highlights">
          {chips_html}
        </div>

        <div class="card-stats">
          <div>🚗 里程: <span class="stat-val">{distance_km} km</span></div>
          <div>⏱️ 耗时: <span class="stat-val">{duration_text}</span></div>
          <div>🏔️ 海拔: <span class="stat-val">{elevation_m} m</span></div>
          <div>🌤️ 天气: <span class="stat-val">{weather_desc}</span></div>
          <div>💳 高速费: <span class="stat-val">¥{tolls_rmb}</span></div>
        </div>

        <div class="card-details">
          <div class="detail-row">
            <div class="detail-label">上午</div>
            <div class="detail-text">{d.get('morning', '')}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">下午</div>
            <div class="detail-text">{d.get('afternoon', '')}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">傍晚</div>
            <div class="detail-text">{d.get('evening', '')}</div>
          </div>

          {warning_html}
        </div>

        <div class="card-footer">
          <div>🏨 下榻：<span style="color:#f1f5f9; font-weight:600;">{d.get('stay', '')}</span></div>
          <div class="nav-links">
            <a class="btn-nav" href="https://uri.amap.com/navigation?from={from_lng},{from_lat}&to={to_lng},{to_lat}&mode=car" target="_blank">高德导航</a>
            <a class="btn-nav" href="http://api.map.baidu.com/direction?origin=latlng:{from_lat},{from_lng}|name:{from_name}&destination=latlng:{to_lat},{to_lng}|name:{to_name}&mode=driving&output=html" target="_blank">百度地图</a>
          </div>
        </div>
      </div>
    """
    return card


def render_html(trip_data: dict, template_path: str = None, output_path: str = None) -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not output_path:
        output_path = os.path.join(base_dir, "trip.html")

    days_rendered = "\n".join([render_day_card(d) for d in trip_data.get("days", [])])
    rules_rendered = "\n".join([f"<li>{r}</li>" for r in trip_data.get("critical_rules") or trip_data.get("critical_safeties", [])])
    json_dump = json.dumps(trip_data, ensure_ascii=False)

    summary = trip_data.get("summary", {})

    title = trip_data.get("trip_title") or trip_data.get("title", "自驾路书")
    subtitle = trip_data.get("trip_subtitle") or trip_data.get("subtitle", "")
    dates = trip_data.get("dates", "")
    total_days = trip_data.get("total_days", len(trip_data.get("days", [])))
    vehicle = trip_data.get("vehicle_type") or trip_data.get("vehicle", "燃油SUV")
    region = trip_data.get("region", "中国自驾")

    tot_dist = summary.get("total_distance_km", 0)
    tot_time = summary.get("total_driving_hours", 0)
    tot_tolls = summary.get("total_tolls_rmb", 0)
    tot_fuel = summary.get("total_energy_cost_rmb") or summary.get("total_fuel_cost_rmb", 0)
    tot_budget = summary.get("total_estimated_budget_rmb") or summary.get("total_budget_rmb", 0)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title} - 全景交互路书 (trip.html)</title>
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  <!-- Chart.js for Elevation Profile -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    :root {{
      --primary: #96382d;
      --primary-hover: #b04336;
      --accent: #d97706;
      --bg: #090d16;
      --card-bg: #131b2e;
      --card-border: #232f48;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --badge-bg: rgba(150, 56, 45, 0.18);
      --badge-border: rgba(150, 56, 45, 0.4);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; }}
    body {{ background-color: var(--bg); color: var(--text); line-height: 1.6; overflow-x: hidden; }}

    header {{
      background: linear-gradient(135deg, #1c263c 0%, #0d1322 100%);
      border-bottom: 1px solid var(--card-border);
      padding: 20px 24px;
      position: sticky;
      top: 0;
      z-index: 1000;
      backdrop-filter: blur(12px);
    }}
    .header-content {{
      max-width: 1500px;
      margin: 0 auto;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }}
    .header-left h1 {{
      font-size: 22px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .header-left p {{
      font-size: 13px;
      color: #cbd5e1;
      margin-top: 2px;
    }}
    .header-badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .badge {{
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 500;
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }}
    .badge-terracotta {{ background: var(--badge-bg); color: #fca5a5; border: 1px solid var(--badge-border); }}
    .badge-amber {{ background: rgba(217, 119, 6, 0.18); color: #fcd34d; border: 1px solid rgba(217, 119, 6, 0.4); }}
    .badge-blue {{ background: rgba(59, 130, 246, 0.18); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.4); }}

    .metric-bar {{
      max-width: 1500px;
      margin: 16px auto 0;
      padding: 0 20px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
    }}
    .metric-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px 16px;
      text-align: center;
    }}
    .metric-card .label {{ font-size: 11px; color: var(--text-muted); margin-bottom: 2px; }}
    .metric-card .value {{ font-size: 20px; font-weight: 700; color: #60a5fa; }}
    .metric-card .unit {{ font-size: 11px; font-weight: 400; color: var(--text-muted); }}

    .tabs-nav {{
      max-width: 1500px;
      margin: 16px auto 0;
      padding: 0 20px;
      display: flex;
      gap: 8px;
      border-bottom: 1px solid var(--card-border);
    }}
    .tab-btn {{
      padding: 10px 18px;
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .tab-btn:hover {{ color: #fff; }}
    .tab-btn.active {{
      color: #f87171;
      border-bottom-color: #f87171;
    }}

    .main-layout {{
      max-width: 1500px;
      margin: 20px auto;
      padding: 0 20px 40px;
      display: grid;
      grid-template-columns: 1.15fr 1fr;
      gap: 24px;
    }}
    @media (max-width: 1100px) {{
      .main-layout {{ grid-template-columns: 1fr; }}
    }}

    .map-wrapper {{
      position: sticky;
      top: 100px;
      height: calc(100vh - 120px);
      min-height: 550px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 12px 30px rgba(0,0,0,0.5);
    }}
    #map {{ flex: 1; width: 100%; height: 100%; z-index: 1; }}
    .map-footer {{
      background: #0f1626;
      padding: 10px 16px;
      border-top: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 11px;
      color: var(--text-muted);
    }}

    .timeline-wrapper {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .rules-card {{
      background: rgba(150, 56, 45, 0.12);
      border: 1px solid rgba(150, 56, 45, 0.35);
      border-radius: 12px;
      padding: 14px 18px;
    }}
    .rules-card h3 {{
      font-size: 14px;
      font-weight: 700;
      color: #fca5a5;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .rules-card ul {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 12px;
      color: #e2e8f0;
    }}

    .day-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      overflow: hidden;
      transition: all 0.2s ease;
      cursor: pointer;
    }}
    .day-card:hover {{
      border-color: #f87171;
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0,0,0,0.4);
    }}
    .day-card.active {{
      border-color: #f87171;
      box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.35);
    }}

    .card-top {{
      padding: 12px 16px;
      background: rgba(255,255,255,0.02);
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .day-tag {{
      font-size: 13px;
      font-weight: 700;
      color: #fca5a5;
      background: rgba(150, 56, 45, 0.25);
      padding: 3px 8px;
      border-radius: 6px;
      border: 1px solid rgba(150, 56, 45, 0.4);
    }}
    .day-date {{
      font-size: 12px;
      color: var(--text-muted);
    }}

    .card-title {{
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      margin: 12px 16px 8px;
      line-height: 1.4;
    }}

    .card-highlights {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 0 16px 10px;
    }}
    .chip {{
      font-size: 11px;
      padding: 2px 7px;
      border-radius: 4px;
      background: rgba(255,255,255,0.06);
      color: #93c5fd;
      border: 1px solid rgba(147, 197, 253, 0.2);
    }}

    .card-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      padding: 8px 16px;
      background: rgba(0,0,0,0.15);
      border-top: 1px dashed var(--card-border);
      font-size: 12px;
      color: var(--text-muted);
    }}
    .stat-val {{ color: #f1f5f9; font-weight: 600; }}

    .card-details {{
      padding: 14px 16px;
      border-top: 1px dashed var(--card-border);
      display: flex;
      flex-direction: column;
      gap: 10px;
      font-size: 12.5px;
    }}
    .detail-row {{ display: flex; gap: 8px; }}
    .detail-label {{ min-width: 44px; font-weight: 700; color: #94a3b8; font-size: 12px; }}
    .detail-text {{ color: #cbd5e1; flex: 1; line-height: 1.45; }}

    .card-warning {{
      background: rgba(217, 119, 6, 0.12);
      border: 1px solid rgba(217, 119, 6, 0.35);
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      color: #fde68a;
      line-height: 1.4;
    }}

    .card-footer {{
      padding: 10px 16px;
      background: rgba(0,0,0,0.25);
      border-top: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
    }}
    .nav-links {{ display: flex; gap: 6px; }}
    .btn-nav {{
      padding: 4px 8px;
      background: #1e293b;
      border: 1px solid var(--card-border);
      color: #e2e8f0;
      border-radius: 6px;
      text-decoration: none;
      font-size: 11px;
      transition: background 0.2s;
    }}
    .btn-nav:hover {{ background: #334155; color: #fff; }}

    .chart-container {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 20px;
    }}

    @media print {{
      body {{ background: #fff; color: #000; }}
      header {{ position: static; background: #fff; border-bottom: 2px solid #000; color: #000; }}
      .map-wrapper {{ display: none; }}
      .main-layout {{ grid-template-columns: 1fr; }}
      .day-card {{ border: 1px solid #ccc; break-inside: avoid; margin-bottom: 16px; }}
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <div class="header-left">
        <h1>🧭 {title}</h1>
        <p>{subtitle}</p>
      </div>
      <div class="header-badges">
        <div class="badge badge-terracotta">📅 {dates} ({total_days}天)</div>
        <div class="badge badge-amber">🚗 {vehicle}</div>
        <div class="badge badge-blue">📍 {region}</div>
      </div>
    </div>
  </header>

  <div class="metric-bar">
    <div class="metric-card">
      <div class="label">总行驶里程</div>
      <div class="value">{tot_dist} <span class="unit">km</span></div>
    </div>
    <div class="metric-card">
      <div class="label">预估驾驶总耗时</div>
      <div class="value">{tot_time} <span class="unit">小时</span></div>
    </div>
    <div class="metric-card">
      <div class="label">高速过路费预估</div>
      <div class="value">¥{tot_tolls}</div>
    </div>
    <div class="metric-card">
      <div class="label">燃油/能耗预估</div>
      <div class="value">¥{tot_fuel}</div>
    </div>
    <div class="metric-card">
      <div class="label">总预算参考</div>
      <div class="value">¥{tot_budget}</div>
    </div>
  </div>

  <div class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('timeline')">📅 每日详单与地图联动</button>
    <button class="tab-btn" onclick="switchTab('elevation')">🏔️ 地理高程剖面图</button>
    <button class="tab-btn" onclick="switchTab('culture')">🏛️ 吐鲁番四大国保专题</button>
    <button class="tab-btn" onclick="switchTab('gear')">❄️ 极寒冰雪自检清单</button>
  </div>

  <div class="main-layout" id="tab-timeline">
    <div class="map-wrapper">
      <div id="map"></div>
      <div class="map-footer">
        <span>🗺️ 底图：高德地图 AutoNavi (GCJ-02) · 国内秒级直连</span>
        <span>点击右侧任一卡片可平滑定位路线</span>
      </div>
    </div>

    <div class="timeline-wrapper">
      <div class="rules-card">
        <h3>🛡️ 新疆自驾核心安全与规则机制</h3>
        <ul>
          {rules_rendered}
        </ul>
      </div>

      {days_rendered}
    </div>
  </div>

  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-elevation">
    <div class="chart-container">
      <h3 style="font-size:16px; margin-bottom:12px; color:#fff;">🏔️ 全程 14 天地理落脚点海拔曲线变化图（米）</h3>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:16px;">从乌鲁木齐 (918m) 攀升至喀纳斯/禾木 (1124m~1374m) 的冰雪泰加林，再降至吐鲁番盆地 (30m) 的温暖绿洲。</p>
      <div style="height:380px;">
        <canvas id="elevationChart"></canvas>
      </div>
    </div>
  </div>

  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-culture">
    <div class="chart-container">
      <h3 style="font-size:18px; margin-bottom:16px; color:#f87171;">🏛️ 吐鲁番国保集群超深度研学四大专题体系指南</h3>
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:16px;">
        <div style="background:#1e293b; padding:16px; border-radius:10px; border:1px solid #334155;">
          <h4 style="color:#60a5fa; margin-bottom:6px;">1. 石窟寺院专题 (Day 11)</h4>
          <p style="font-size:12px; color:#cbd5e1; line-height:1.5;">
            <b>核心点：</b>柏孜克里克千佛洞、吐峪沟千佛洞<br>
            <b>研学焦点：</b>高昌回鹘王室供养人壁画艺术、汉风与印度/粟特交融的洞窟形制演变。
          </p>
        </div>
        <div style="background:#1e293b; padding:16px; border-radius:10px; border:1px solid #334155;">
          <h4 style="color:#34d399; margin-bottom:6px;">2. 古城防御专题 (Day 12)</h4>
          <p style="font-size:12px; color:#cbd5e1; line-height:1.5;">
            <b>核心点：</b>交河故城（减土法）vs 高昌故城（夯土版筑）<br>
            <b>研学焦点：</b>交河故城自上而下掏土成城的生土力学极限；高昌故城周长 5 公里外城与大佛寺夯土防御体系。
          </p>
        </div>
        <div style="background:#1e293b; padding:16px; border-radius:10px; border:1px solid #334155;">
          <h4 style="color:#fbbf24; margin-bottom:6px;">3. 地下水利专题 (Day 13)</h4>
          <p style="font-size:12px; color:#cbd5e1; line-height:1.5;">
            <b>核心点：</b>吐鲁番坎儿井地下暗渠系统<br>
            <b>研学焦点：</b>竖井开挖、暗渠重力引天山冰雪融水、明渠蓄水涝坝的无动力水力学智慧。
          </p>
        </div>
        <div style="background:#1e293b; padding:16px; border-radius:10px; border:1px solid #334155;">
          <h4 style="color:#f472b6; margin-bottom:6px;">4. 清代砖构与古墓 (Day 12-13)</h4>
          <p style="font-size:12px; color:#cbd5e1; line-height:1.5;">
            <b>核心点：</b>苏公塔（额敏塔）、阿斯塔那古墓群<br>
            <b>研学焦点：</b>苏公塔 44 米圆塔 72 种几何拼砖与受力穹顶；阿斯塔那地下墓室规制与伏羲女娲图。
          </p>
        </div>
      </div>
    </div>
  </div>

  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-gear">
    <div class="chart-container">
      <h3 style="font-size:18px; margin-bottom:16px; color:#f87171;">❄️ 大众高尔夫初冬极寒行车自检与物资装备清单</h3>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; font-size:13px; color:#cbd5e1; line-height:1.6;">
        <div style="background:#1e293b; padding:16px; border-radius:10px;">
          <h4 style="color:#60a5fa; margin-bottom:8px;">🚗 车辆与冰雪硬件</h4>
          • 驱动轮（前轮）在布尔津必须换装深度花纹雪地胎。<br>
          • 随车配备尺寸匹配的金属防滑链（提前试装）。<br>
          • 随车常备便携式搭电宝与拖车绳。<br>
          • 提车加注 -35# 极寒防冻玻璃水，防冻液冰点达标。
        </div>
        <div style="background:#1e293b; padding:16px; border-radius:10px;">
          <h4 style="color:#34d399; margin-bottom:8px;">🥾 个人防寒与摄影</h4>
          • 禾木清晨（-15°C~-18°C）：长款厚羽绒服 + 抓绒内胆 + 保暖内衣。<br>
          • 防滑高帮雪地靴（或简易防滑冰爪）。<br>
          • 相机与手机备用电池贴身存放防骤降电量。<br>
          • 吐鲁番干燥大漠：墨镜、防晒霜、润唇膏、保温壶。
        </div>
      </div>
    </div>
  </div>

  <script>
    const tripData = {json_dump};

    const map = L.map('map', {{ zoomControl: true, attributionControl: false }}).setView([45.5, 87.5], 6);

    L.tileLayer('https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={{x}}&y={{y}}&z={{z}}', {{
      subdomains: ['1', '2', '3', '4'],
      minZoom: 4,
      maxZoom: 18
    }}).addTo(map);

    const markers = [];
    const latlngs = [];

    const daysList = tripData.days || [];
    daysList.forEach(d => {{
      const toObj = d.to_place || d.to || {{}};
      const lat = toObj.lat;
      const lng = toObj.lng;
      if (!lat || !lng) return;

      latlngs.push([lat, lng]);

      const iconHtml = `<div style="background:#96382d; color:#fff; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; border:2px solid #fff; box-shadow:0 3px 8px rgba(0,0,0,0.6); cursor:pointer;">${{d.day}}</div>`;
      const customIcon = L.divIcon({{ className: 'custom-day-marker', html: iconHtml, iconSize: [26, 26], iconAnchor: [13, 13] }});

      const marker = L.marker([lat, lng], {{ icon: customIcon }}).addTo(map);
      marker.bindPopup(`
        <div style="font-size:13px; line-height:1.5; color:#0f172a; min-width:200px;">
          <b style="color:#96382d;">Day ${{d.day}}: ${{d.title}}</b><br/>
          📍 终点: ${{toObj.name}}<br/>
          🏔️ 海拔: ${{d.elevation_m || (d.elevation && d.elevation.elevation_m) || 0}}m<br/>
          🚗 里程: ${{d.distance_km || (d.route && d.route.distance_km) || 0}} km<br/>
          <hr style="margin:6px 0; border:0; border-top:1px solid #e2e8f0;"/>
          🏨 下榻: ${{d.stay}}
        </div>
      `);

      markers.push({{ day: d.day, marker, lat, lng }});
    }});

    const polyline = L.polyline(latlngs, {{
      color: '#f87171',
      weight: 3.5,
      opacity: 0.85,
      dashArray: '6, 6'
    }}).addTo(map);

    if (latlngs.length > 0) {{
      map.fitBounds(polyline.getBounds(), {{ padding: [40, 40] }});
    }}

    function focusDay(dayNumber) {{
      document.querySelectorAll('.day-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('day-card-' + dayNumber);
      if (activeCard) activeCard.classList.add('active');

      const target = markers.find(m => m.day === dayNumber);
      if (target) {{
        map.flyTo([target.lat, target.lng], 9, {{ duration: 1.2 }});
        target.marker.openPopup();
      }}
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');

      document.getElementById('tab-timeline').style.display = (tabId === 'timeline') ? 'grid' : 'none';
      document.getElementById('tab-elevation').style.display = (tabId === 'elevation') ? 'block' : 'none';
      document.getElementById('tab-culture').style.display = (tabId === 'culture') ? 'block' : 'none';
      document.getElementById('tab-gear').style.display = (tabId === 'gear') ? 'block' : 'none';

      if (tabId === 'timeline') {{
        setTimeout(() => {{ map.invalidateSize(); }}, 200);
      }}
      if (tabId === 'elevation') {{
        renderElevationChart();
      }}
    }}

    let chartInstance = null;
    function renderElevationChart() {{
      if (chartInstance) return;
      const ctx = document.getElementById('elevationChart').getContext('2d');
      const labels = daysList.map(d => `Day ${{d.day}} (${{(d.to_place || d.to || {{}}).name || ''}})`);
      const elevations = daysList.map(d => d.elevation_m || (d.elevation && d.elevation.elevation_m) || 0);

      chartInstance = new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [{{
            label: '海拔高度 (米)',
            data: elevations,
            borderColor: '#f87171',
            backgroundColor: 'rgba(248, 113, 113, 0.15)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#96382d',
            pointRadius: 5
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            y: {{
              beginAtZero: true,
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8' }}
            }},
            x: {{
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
            }}
          }},
          plugins: {{
            legend: {{ labels: {{ color: '#f1f5f9' }} }}
          }}
        }}
      }});
    }}
  </script>
</body>
</html>
"""

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


if __name__ == "__main__":
    from planner import build_xinjiang_14d_itinerary
    data = build_xinjiang_14d_itinerary()
    out = render_html(data)
    print(f"✅ 单文件交互式路书生成成功: {out}")
