#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_rich_trip_html.py — 全景自驾路书（支持桌面双栏 + 移动端自适应 + 14天每餐5选1口碑老店 + 每日观鸟动物 + 斯飞级国保超深度研学 + 提醒整合）
"""

import os
import json
from generate_mobile_trip_html import TRIP_DATA, render_dining_html_5_options
from birding_data_14d import render_birding_html
from heritage_data_14d import HERITAGE_14D_DATA, HERITAGE_DAY_ROUTES, render_heritage_html

TRIP_DATA["heritage_routes"] = HERITAGE_DAY_ROUTES


def render_day_card(d):
    chips_html = "".join([f'<span class="chip">{h}</span>' for h in d["highlights"]])
    
    warning_html = ""
    if d.get("warnings"):
        w_lines = "".join([f'<div>{w}</div>' for w in d["warnings"]])
        warning_html = f'<div class="card-warning">{w_lines}</div>'

    heritage_days = {h["day"] for h in HERITAGE_14D_DATA}
    herit_btn = ""
    day_num = d["day"]
    if day_num in heritage_days:
        herit_btn = f'<button onclick="event.stopPropagation(); jumpToHeritageTab({day_num})" class="btn-nav" style="background:rgba(147,51,234,0.25); color:#d8b4fe; border-color:rgba(147,51,234,0.5); font-weight:700; cursor:pointer;">🏛️ 国保研学</button>'

    card = f"""
      <div class="day-card" id="day-card-{d['day']}" onclick="focusDay({d['day']})">
        <div class="card-top">
          <span class="day-tag">Day {d['day']} · {d['weekday']}</span>
          <span class="day-date">{d['date']}</span>
        </div>
        <div class="card-title">{d['title']}</div>

        <div class="card-highlights">
          {chips_html}
        </div>

        <div class="card-stats">
          <div>🚗 里程: <span class="stat-val">{d['distance_km']} km</span></div>
          <div>⏱️ 耗时: <span class="stat-val">{d['duration']}</span></div>
          <div>🏔️ 海拔: <span class="stat-val">{d['elevation_m']} m</span></div>
          <div>🌤️ 天气: <span class="stat-val">{d['weather']}</span></div>
          <div>💳 高速费: <span class="stat-val">¥{d['tolls_rmb']}</span></div>
        </div>

        <div class="card-details">
          <div class="detail-row">
            <div class="detail-label">上午</div>
            <div class="detail-text">{d['morning']}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">下午</div>
            <div class="detail-text">{d['afternoon']}</div>
          </div>
          <div class="detail-row">
            <div class="detail-label">傍晚</div>
            <div class="detail-text">{d['evening']}</div>
          </div>

          {warning_html}
        </div>

        <div class="card-footer">
          <div>🏨 下榻：<span style="color:#f1f5f9; font-weight:600;">{d['stay']}</span></div>
          <div class="nav-links">
            <button onclick="event.stopPropagation(); jumpToDiningTab({d['day']})" class="btn-nav" style="background:rgba(245,158,11,0.25); color:#fcd34d; border-color:rgba(245,158,11,0.5); font-weight:700; cursor:pointer;">🍴 美食 (5选1)</button>
            <button onclick="event.stopPropagation(); jumpToBirdingTab({d['day']})" class="btn-nav" style="background:rgba(16,185,129,0.25); color:#6ee7b7; border-color:rgba(16,185,129,0.5); font-weight:700; cursor:pointer;">🦉 观鸟/动物</button>
            {herit_btn}
            <a class="btn-nav" href="https://uri.amap.com/navigation?from={d['from']['lng']},{d['from']['lat']}&to={d['to']['lng']},{d['to']['lat']}&mode=car" target="_blank">高德导航</a>
          </div>
        </div>
      </div>
    """
    return card


def build_full_html():
    days_rendered = "\n".join([render_day_card(d) for d in TRIP_DATA["days"]])
    rules_rendered = "\n".join([f"<li>{r}</li>" for r in TRIP_DATA["critical_safeties"]])
    dining_rendered = render_dining_html_5_options()
    birding_rendered = render_birding_html()
    heritage_rendered = render_heritage_html()
    json_dump = json.dumps(TRIP_DATA, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{TRIP_DATA['title']} - 全景交互路书 (trip.html)</title>
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  <!-- Leaflet PolylineDecorator for Directional Arrows -->
  <script src="https://cdn.jsdelivr.net/npm/leaflet-polylinedecorator@1.6.0/dist/leaflet.polylineDecorator.min.js"></script>
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
    @media (max-width: 1024px) {{
      .main-layout {{ display: flex; flex-direction: column; padding: 0 12px 40px; }}
      .map-wrapper {{ position: relative; top: 0; height: 260px; min-height: 260px; margin-bottom: 8px; box-shadow: none; }}
      .metric-bar {{ grid-template-columns: repeat(2, 1fr); padding: 0 12px; }}
      .tabs-nav {{ overflow-x: auto; scrollbar-width: none; }}
      .header-content {{ flex-direction: column; align-items: flex-start; }}
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
      background: linear-gradient(145deg, #3d1414 0%, #1f0b0b 100%) !important;
      border: 1.5px solid #f87171 !important;
      box-shadow: 0 8px 24px rgba(248, 113, 113, 0.35) !important;
      transform: translateY(-2px);
    }}
    .day-card.active .card-top {{
      background: rgba(248, 113, 113, 0.18) !important;
      border-bottom-color: rgba(248, 113, 113, 0.4) !important;
    }}
    .day-card.active .card-title {{
      color: #fff !important;
    }}
    .day-card.active .card-footer {{
      background: rgba(0,0,0,0.4) !important;
      border-top-color: rgba(248, 113, 113, 0.3) !important;
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
    .day-date {{ font-size: 12px; color: var(--text-muted); }}

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

    /* Custom markers */
    .custom-day-marker {{
      background: #96382d;
      color: #fff;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 12px;
      border: 2px solid #fff;
      box-shadow: 0 3px 8px rgba(0,0,0,0.6);
      cursor: pointer;
    }}
    .custom-dine-pin {{
      background: #1e293b;
      border: 1.5px solid #f59e0b;
      border-radius: 12px;
      padding: 3px 8px;
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 4px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    }}
    .custom-bird-pin {{
      background: #064e3b;
      border: 1.5px solid #34d399;
      border-radius: 12px;
      padding: 3px 8px;
      color: #fff;
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    }}
    .custom-herit-pin {{
      background: #581c87;
      border: 1.5px solid #c084fc;
      border-radius: 12px;
      padding: 3px 8px;
      color: #fff;
      font-size: 11.5px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 4px 10px rgba(0,0,0,0.6);
    }}
    .custom-herit-leg-badge {{
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid #c084fc;
      border-radius: 10px;
      padding: 2px 7px;
      color: #fde68a;
      font-size: 10px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }}

    /* Dining 5-options interactive styles in Desktop */
    .m-dining-day-group {{ background: #151d30; border: 1px solid var(--card-border); border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .m-dining-day-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid var(--card-border); }}
    .m-dine-day-badge {{ font-size: 15px; font-weight: 700; color: #fca5a5; }}
    .m-dine-city-badge {{ font-size: 12px; color: #60a5fa; background: rgba(37,99,235,0.15); padding: 3px 8px; border-radius: 4px; font-weight: 600; }}

    .m-meal-section-box {{ background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 10px; padding: 12px; margin-bottom: 12px; }}
    .m-meal-sec-header {{ font-size: 13.5px; font-weight: 700; color: #f87171; margin-bottom: 8px; }}

    .m-dine-pills-bar {{ display: flex; overflow-x: auto; gap: 8px; padding-bottom: 8px; scrollbar-width: none; }}
    .m-dine-pills-bar::-webkit-scrollbar {{ display: none; }}
    .m-dine-pill {{
      flex: 0 0 auto;
      background: #1e293b;
      border: 1px solid #334155;
      color: #94a3b8;
      font-size: 12px;
      padding: 5px 12px;
      border-radius: 16px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}
    .m-dine-pill .pill-num {{
      display: inline-block;
      width: 16px;
      height: 16px;
      line-height: 16px;
      text-align: center;
      background: rgba(255,255,255,0.1);
      border-radius: 50%;
      font-size: 10px;
      font-weight: 700;
    }}
    .m-dine-pill.active {{
      background: #96382d;
      border-color: #f87171;
      color: #fff;
      font-weight: 600;
    }}
    .m-dine-pill.active .pill-num {{ background: #fff; color: #96382d; }}

    .m-meal-option-detail {{ background: rgba(0,0,0,0.25); border: 1px solid var(--card-border); border-radius: 8px; padding: 12px 14px; margin-top: 6px; }}
    .m-meal-card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
    .m-meal-name {{ font-size: 14px; color: #f8fafc; }}
    .m-badge-years {{ font-size: 11px; font-weight: 600; color: #fca5a5; background: rgba(150, 56, 45, 0.3); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(150, 56, 45, 0.4); }}
    .m-meal-meta-row {{ display: flex; gap: 8px; margin-bottom: 6px; font-size: 11px; }}
    .m-tag-source {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 2px 6px; border-radius: 3px; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .m-tag-price {{ background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 2px 6px; border-radius: 3px; }}
    .m-must-orders-box {{ font-size: 12.5px; color: #f1f5f9; margin-bottom: 6px; line-height: 1.4; }}
    .m-order-lbl {{ color: #fbbf24; font-weight: 700; }}
    .m-meal-desc-box {{ font-size: 12px; color: #cbd5e1; line-height: 1.5; margin-bottom: 8px; }}
    .m-dine-nav-btn {{ display: inline-block; background: #2563eb; color: #fff; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 11.5px; font-weight: 600; }}

    /* Birding Styles in Desktop */
    .m-birding-card {{ background: #151d30; border: 1px solid var(--card-border); border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .m-bird-card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
    .m-bird-day-tag {{ font-size: 13px; font-weight: 700; color: #fca5a5; background: rgba(150, 56, 45, 0.25); padding: 2px 7px; border-radius: 5px; }}
    .m-bird-city-tag {{ font-size: 11.5px; color: #34d399; background: rgba(16, 185, 129, 0.15); padding: 2px 7px; border-radius: 4px; font-weight: 600; }}
    .m-bird-loc-name {{ font-size: 14.5px; color: #fff; margin-bottom: 6px; }}
    .m-bird-lbl {{ font-weight: 700; color: #94a3b8; font-size: 12px; }}
    .m-bird-time-box {{ font-size: 12.5px; color: #fde68a; background: rgba(217, 119, 6, 0.15); padding: 5px 10px; border-radius: 6px; margin-bottom: 6px; }}
    .m-bird-habitat-box {{ font-size: 12px; color: #cbd5e1; margin-bottom: 6px; }}
    .m-bird-chips-container {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }}
    .m-bird-species-chip {{ font-size: 11.5px; padding: 3px 8px; border-radius: 5px; background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.35); font-weight: 600; }}
    .m-bird-notes-box {{ font-size: 12px; color: #cbd5e1; line-height: 1.5; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 6px; margin-bottom: 10px; }}
    .m-bird-nav-btn {{ display: inline-block; background: #059669; color: #fff; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-size: 11.5px; font-weight: 600; }}

    /* Heritage Styles in Desktop */
    .m-herit-card {{ background: #181d33; border: 1px solid var(--card-border); border-radius: 14px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.4); transition: all 0.25s ease; }}
    .m-herit-card.active {{ background: linear-gradient(145deg, #340c4e 0%, #1b042b 100%) !important; border: 1.5px solid #c084fc !important; box-shadow: 0 8px 24px rgba(192, 132, 252, 0.4) !important; transform: translateY(-2px); }}
    .m-dining-day-group {{ background: #181d33; border: 1px solid var(--card-border); border-radius: 14px; padding: 14px; margin-bottom: 20px; transition: all 0.25s ease; }}
    .m-dining-day-group.active {{ background: linear-gradient(145deg, #3b2003 0%, #1c0e00 100%) !important; border: 1.5px solid #f59e0b !important; box-shadow: 0 8px 24px rgba(245, 158, 11, 0.35) !important; transform: translateY(-2px); }}
    .m-birding-card {{ background: #181d33; border: 1px solid var(--card-border); border-radius: 14px; padding: 16px; margin-bottom: 18px; transition: all 0.25s ease; }}
    .m-birding-card.active {{ background: linear-gradient(145deg, #052e1f 0%, #021a11 100%) !important; border: 1.5px solid #10b981 !important; box-shadow: 0 8px 24px rgba(16, 185, 129, 0.35) !important; transform: translateY(-2px); }}
    .m-herit-photo-wrapper {{ width: 100%; aspect-ratio: 16 / 9; position: relative; background: #0b101c; overflow: hidden; }}
    .m-herit-photo-img {{ width: 100%; height: 100%; object-fit: cover; object-position: center; display: block; }}
    .m-herit-photo-overlay {{ position: absolute; inset: 0; background: linear-gradient(to top, rgba(9, 13, 22, 0.95) 0%, rgba(9, 13, 22, 0.2) 50%, rgba(0, 0, 0, 0.4) 100%); display: flex; flex-direction: column; justify-content: space-between; padding: 12px 16px; pointer-events: none; }}
    .m-herit-img-badge {{ align-self: flex-start; background: rgba(126, 34, 206, 0.85); backdrop-filter: blur(4px); color: #fff; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 4px; border: 1px solid rgba(192, 132, 252, 0.5); }}
    .m-herit-photo-caption {{ color: #f1f5f9; font-size: 13px; font-weight: 600; line-height: 1.4; text-shadow: 0 2px 8px rgba(0,0,0,0.9); }}
    .m-herit-body-inner {{ padding: 18px 20px 20px; }}
    .m-herit-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
    .m-herit-day-tag {{ font-size: 13px; font-weight: 700; color: #fca5a5; background: rgba(150, 56, 45, 0.25); padding: 2px 7px; border-radius: 5px; }}
    .m-herit-city-tag {{ font-size: 11.5px; color: #c084fc; background: rgba(147, 51, 234, 0.15); padding: 2px 7px; border-radius: 4px; font-weight: 600; }}
    .m-herit-title {{ font-size: 17px; color: #fff; margin-bottom: 4px; }}
    .m-herit-batch {{ font-size: 12px; color: #fbbf24; font-weight: 600; margin-bottom: 4px; }}
    .m-herit-sifei {{ font-size: 11px; color: #94a3b8; margin-bottom: 10px; padding-bottom: 6px; border-bottom: 1px dashed var(--card-border); }}
    .m-herit-schedule-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; background: rgba(0,0,0,0.25); border-radius: 8px; padding: 10px 12px; font-size: 12px; margin-bottom: 12px; }}
    .m-herit-sched-item b {{ color: #60a5fa; }}
    .m-herit-chips-box {{ margin-bottom: 12px; }}
    .m-herit-chips-flow {{ display: flex; flex-direction: column; gap: 6px; }}
    .m-herit-chip {{ font-size: 12px; color: #cbd5e1; background: rgba(255,255,255,0.03); padding: 4px 8px; border-radius: 4px; border-left: 3px solid #a855f7; }}
    .m-herit-notes-box {{ background: rgba(147, 51, 234, 0.08); border: 1px solid rgba(147, 51, 234, 0.25); border-radius: 8px; padding: 12px 14px; margin-bottom: 12px; }}
    .m-herit-notes-title {{ font-size: 12.5px; font-weight: 700; color: #d8b4fe; margin-bottom: 6px; }}
    .m-herit-notes-body {{ font-size: 12px; color: #cbd5e1; line-height: 1.6; }}
    .m-herit-photo-box {{ background: rgba(217, 119, 6, 0.12); border: 1px solid rgba(217, 119, 6, 0.3); border-radius: 8px; padding: 10px 12px; font-size: 12px; color: #fde68a; line-height: 1.5; margin-bottom: 12px; }}
    .m-herit-nav-btn {{ display: inline-block; background: #7e22ce; color: #fff; padding: 7px 16px; border-radius: 6px; text-decoration: none; font-size: 12px; font-weight: 600; }}

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
        <h1>🧭 {TRIP_DATA['title']}</h1>
        <p>{TRIP_DATA['subtitle']}</p>
      </div>
      <div class="header-badges">
        <div class="badge badge-terracotta">📅 {TRIP_DATA['dates']} ({TRIP_DATA['total_days']}天)</div>
        <div class="badge badge-amber">🚗 {TRIP_DATA['vehicle']}</div>
        <div class="badge badge-blue">📍 新疆（阿勒泰+准噶尔+吐鲁番）</div>
      </div>
    </div>
  </header>

  <div class="metric-bar">
    <div class="metric-card">
      <div class="label">总行驶里程</div>
      <div class="value">{TRIP_DATA['summary']['total_distance_km']} <span class="unit">km</span></div>
    </div>
    <div class="metric-card">
      <div class="label">预估驾驶总耗时</div>
      <div class="value">{TRIP_DATA['summary']['total_driving_hours']} <span class="unit">小时</span></div>
    </div>
    <div class="metric-card">
      <div class="label">高速过路费预估</div>
      <div class="value">¥{TRIP_DATA['summary']['total_tolls_rmb']}</div>
    </div>
    <div class="metric-card">
      <div class="label">燃油费用预估</div>
      <div class="value">¥{TRIP_DATA['summary']['total_fuel_cost_rmb']}</div>
    </div>
    <div class="metric-card">
      <div class="label">总预算参考</div>
      <div class="value">¥{TRIP_DATA['summary']['total_budget_rmb']}</div>
    </div>
  </div>

  <div class="tabs-nav">
    <button class="tab-btn active" onclick="switchTab('timeline')">📅 每日详单与地图联动</button>
    <button class="tab-btn" onclick="switchTab('dining')">🍽️ 每日三餐口碑老店 (每餐5选1)</button>
    <button class="tab-btn" onclick="switchTab('birding')">🦉 每日观鸟与野生动物观测</button>
    <button class="tab-btn" onclick="switchTab('culture')">🏛️ 全国重点文保 (国保超深度研学)</button>
    <button class="tab-btn" onclick="switchTab('tips')">🔔 提醒 (海拔+极寒自检+安全)</button>
  </div>

  <div class="main-layout" id="tab-timeline">
    <div class="map-wrapper">
      <div id="map"></div>
      <div class="map-footer">
        <span>🗺️ 底图：高德地图 (带前进方向指示箭头)</span>
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

  <!-- Dining Tab in Desktop -->
  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-dining">
    <div class="chart-container">
      <h3 style="font-size:18px; margin-bottom:12px; color:#f87171;">🍽️ 210家多年老店 ✕ 本地人扎堆老号深度美食指南 (每餐5选1)</h3>
      <p style="font-size:12px; color:#fcd34d; margin-bottom:16px; background:rgba(245,158,11,0.15); padding:10px 14px; border-radius:8px; border:1px solid rgba(245,158,11,0.3);">
        严格遵循「多年老店」与「本地人推荐」双重标准，每日早、中、晚三餐均配备 5 家地道口碑老号。点击横向选项卡胶囊即可自由切换各家菜单特色与一键高德导航。
      </p>
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap:16px;">
        {dining_rendered}
      </div>
    </div>
  </div>

  <!-- Birding Tab in Desktop -->
  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-birding">
    <div class="chart-container">
      <h3 style="font-size:18px; margin-bottom:12px; color:#34d399;">🦉 14天每日观鸟与野生动物观测指南 (结合小红书/中国观鸟记录中心实战纪录)</h3>
      <p style="font-size:12px; color:#6ee7b7; margin-bottom:16px; background:rgba(16,185,129,0.15); padding:10px 14px; border-radius:8px; border:1px solid rgba(16,185,129,0.3);">
        涵盖乌伦古湖初冬大天鹅群、阿尔泰泰加林黑琴鸡与星鸦、喀纳斯鸭泽湖不冻泉河乌潜水、神仙湾白尾海雕巡猎、额河大峡谷高山兀鹫、卡拉麦里<b>普氏野马与蒙古野驴</b>野化群、吐峪沟石鸡与交河古城纵纹腹小鸮。
      </p>
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap:16px;">
        {birding_rendered}
      </div>
    </div>
  </div>

  <!-- Heritage Tab in Desktop -->
  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-culture">
    <div class="chart-container">
      <h3 style="font-size:18px; margin-bottom:12px; color:#c084fc;">🏛️ 14天自驾沿线全国重点文物保护单位（国保）超深度研学指南</h3>
      <p style="font-size:12px; color:#d8b4fe; margin-bottom:16px; background:rgba(147,51,234,0.15); padding:10px 14px; border-radius:8px; border:1px solid rgba(147,51,234,0.3);">
        参考<b>斯飞坐标（Sifei）与华夏古迹图</b>实战田野数据：涵盖乌鲁木齐文庙、可可托海三号功勋矿、北庭故城（世遗）、疏勒城（石城子）、柏孜克里克千佛洞、吐峪沟麻扎村、高昌故城（世遗）、阿斯塔那古墓群、交河故城（世遗）与清代苏公塔。
      </p>
      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap:16px;">
        {heritage_rendered}
      </div>
    </div>
  </div>

  <!-- Merged Tips Tab in Desktop -->
  <div style="max-width:1500px; margin:20px auto; padding:0 20px; display:none;" id="tab-tips">
    <div class="chart-container">
      <h3 style="font-size:16px; margin-bottom:12px; color:#fff;">🏔️ 全程 14 天地理落脚点海拔曲线变化图（米）</h3>
      <p style="font-size:12px; color:var(--text-muted); margin-bottom:16px;">从乌鲁木齐 (918m) 攀升至喀纳斯/禾木 (1124m~1374m) 的冰雪泰加林，再降至吐鲁番盆地 (30m) 的温暖绿洲。</p>
      <div style="height:350px; margin-bottom:24px;">
        <canvas id="elevationChart"></canvas>
      </div>

      <h3 style="font-size:16px; margin-bottom:12px; color:#f87171;">❄️ 大众高尔夫初冬极寒行车自检与物资装备清单</h3>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px; font-size:13px; color:#cbd5e1; line-height:1.6; margin-bottom:20px;">
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

      <h3 style="font-size:16px; margin-bottom:12px; color:#fcd34d;">🛡️ 核心安全与关键规则机制</h3>
      <div style="background:rgba(150,56,45,0.15); border:1px solid rgba(150,56,45,0.4); padding:16px; border-radius:10px; font-size:13px; color:#fde68a;">
        • <b>喀纳斯/禾木暗冰防滑：</b>弯道低速慢行，严禁猛打方向与急踩刹车。<br>
        • <b>闭馆时间窗口把控：</b>可可托海 08:30 出发；北庭故城 14:30 抵达避开冬季提前闭馆。<br>
        • <b>达坂城横风缓冲：</b>返程预留百里风区车速控制与安检时间。
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

    tripData.days.forEach(d => {{
      const lat = d.to.lat;
      const lng = d.to.lng;
      latlngs.push([lat, lng]);

      const iconHtml = `<div class="custom-day-marker">${{d.day}}</div>`;
      const customIcon = L.divIcon({{ className: 'custom-day-div', html: iconHtml, iconSize: [26, 26], iconAnchor: [13, 13] }});

      const marker = L.marker([lat, lng], {{ icon: customIcon }}).addTo(map);
      marker.bindPopup(`
        <div style="font-size:13px; line-height:1.5; color:#0f172a; min-width:200px;">
          <b style="color:#96382d;">Day ${{d.day}}: ${{d.title}}</b><br/>
          📍 终点: ${{d.to.name}}<br/>
          🏔️ 海拔: ${{d.elevation_m}}m ｜ 🌤️ 天气: ${{d.weather}}<br/>
          🚗 里程: ${{d.distance_km}} km (耗时约 ${{d.duration}})<br/>
          💳 高速费: ¥${{d.tolls_rmb}}<br/>
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

    if (window.L && L.polylineDecorator) {{
      try {{
        L.polylineDecorator(polyline, {{
          patterns: [
            {{
              offset: 25,
              repeat: 60,
              symbol: L.Symbol.arrowHead({{
                pixelSize: 10,
                polygon: false,
                pathOptions: {{ stroke: true, color: '#fca5a5', weight: 3, opacity: 0.95 }}
              }})
            }}
          ]
        }}).addTo(map);
      }} catch(e) {{
        console.warn("Decorator error", e);
      }}
    }}

    if (latlngs.length > 0) {{
      map.fitBounds(polyline.getBounds(), {{ padding: [40, 40] }});
    }}

    function focusDay(dayNumber) {{
      document.querySelectorAll('.day-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('day-card-' + dayNumber);
      if (activeCard) activeCard.classList.add('active');

      const target = markers.find(m => m.day === dayNumber);
      if (target) {{
        map.flyTo([target.lat, target.lng], 9, {{ duration: 1.0 }});
        target.marker.openPopup();
      }}
    }}

    function switchMealOption(dayNum, mealKey, optIdx) {{
      const parentSection = event.target.closest('.m-meal-section-box');
      if (!parentSection) return;

      parentSection.querySelectorAll('.m-dine-pill').forEach((pill, idx) => {{
        if (idx === optIdx) {{
          pill.classList.add('active');
        }} else {{
          pill.classList.remove('active');
        }}
      }});

      parentSection.querySelectorAll('.m-meal-option-detail').forEach((detail, idx) => {{
        if (idx === optIdx) {{
          detail.style.display = 'block';
        }} else {{
          detail.style.display = 'none';
        }}
      }});
    }}

    function jumpToDiningTab(dayNum) {{
      const btn = document.querySelectorAll('.tab-btn')[1];
      switchTab('dining');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      setTimeout(() => {{
        const el = document.getElementById('dine-day-' + dayNum);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function jumpToBirdingTab(dayNum) {{
      const btn = document.querySelectorAll('.tab-btn')[2];
      switchTab('birding');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      setTimeout(() => {{
        const el = document.getElementById('bird-day-' + dayNum);
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function jumpToHeritageTab(dayNum) {{
      const btn = document.querySelectorAll('.tab-btn')[3];
      switchTab('culture');
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      setTimeout(() => {{
        const el = document.getElementById('herit-day-' + dayNum + '-1') || document.querySelector('[id^="herit-day-' + dayNum + '"]');
        if (el) el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function switchTab(tabId) {{
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      if (event && event.target && event.target.classList) {{
        event.target.classList.add('active');
      }}

      document.getElementById('tab-timeline').style.display = (tabId === 'timeline') ? 'grid' : 'none';
      document.getElementById('tab-dining').style.display = (tabId === 'dining') ? 'block' : 'none';
      document.getElementById('tab-birding').style.display = (tabId === 'birding') ? 'block' : 'none';
      document.getElementById('tab-culture').style.display = (tabId === 'culture') ? 'block' : 'none';
      document.getElementById('tab-tips').style.display = (tabId === 'tips') ? 'block' : 'none';

      if (tabId === 'timeline') {{
        setTimeout(() => {{ map.invalidateSize(); }}, 200);
      }}
      if (tabId === 'tips') {{
        renderElevationChart();
      }}
    }}

    let chartInstance = null;
    function renderElevationChart() {{
      if (chartInstance) return;
      const ctx = document.getElementById('elevationChart').getContext('2d');
      const labels = tripData.days.map(d => `Day ${{d.day}} (${{d.to.name.split('/')[0]}})`);
      const elevations = tripData.days.map(d => d.elevation_m);
      const minTemps = tripData.days.map(d => d.temp_min);
      const maxTemps = tripData.days.map(d => d.temp_max);

      chartInstance = new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [
            {{
              label: '海拔高度 (米)',
              data: elevations,
              borderColor: '#38bdf8',
              backgroundColor: 'rgba(56, 189, 248, 0.12)',
              fill: true,
              tension: 0.35,
              pointBackgroundColor: '#0284c7',
              pointRadius: 4,
              yAxisID: 'yElevation'
            }},
            {{
              label: '最高气温 (°C)',
              data: maxTemps,
              borderColor: '#f87171',
              backgroundColor: 'transparent',
              borderWidth: 2,
              pointBackgroundColor: '#ef4444',
              pointRadius: 4,
              tension: 0.35,
              yAxisID: 'yTemp'
            }},
            {{
              label: '最低气温 (°C)',
              data: minTemps,
              borderColor: '#818cf8',
              backgroundColor: 'transparent',
              borderWidth: 2,
              borderDash: [4, 4],
              pointBackgroundColor: '#6366f1',
              pointRadius: 4,
              tension: 0.35,
              yAxisID: 'yTemp'
            }}
          ]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          interaction: {{
            mode: 'index',
            intersect: false
          }},
          scales: {{
            yElevation: {{
              type: 'linear',
              display: true,
              position: 'left',
              title: {{
                display: true,
                text: '海拔 (m)',
                color: '#38bdf8',
                font: {{ weight: 'bold' }}
              }},
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8' }}
            }},
            yTemp: {{
              type: 'linear',
              display: true,
              position: 'right',
              title: {{
                display: true,
                text: '气温 (°C)',
                color: '#f87171',
                font: {{ weight: 'bold' }}
              }},
              grid: {{ drawOnChartArea: false }},
              ticks: {{ color: '#fca5a5' }}
            }},
            x: {{
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
            }}
          }},
          plugins: {{
            legend: {{ labels: {{ color: '#f1f5f9' }} }},
            tooltip: {{
              callbacks: {{
                label: function(context) {{
                  if (context.dataset.yAxisID === 'yElevation') {{
                    return `🏔️ 海拔: ${{context.parsed.y}} 米`;
                  }} else if (context.datasetIndex === 1) {{
                    return `☀️ 最高温: ${{context.parsed.y}} °C`;
                  }} else if (context.datasetIndex === 2) {{
                    return `❄️ 最低温: ${{context.parsed.y}} °C`;
                  }}
                  return '';
                }}
              }}
            }}
          }}
        }}
      }});
    }}
  </script>
</body>
</html>
"""
    return html


def main():
    project_root = "/Users/Noodles/Documents/AG_Project"
    out_path = os.path.join(project_root, "trip.html")
    html_content = build_full_html()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"🎉 包含方向箭头与国保/观鸟/餐饮的通用版路书已重新编译: {out_path}")


if __name__ == "__main__":
    main()
