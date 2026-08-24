#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_mobile_trip_html.py — 专为手机端打造的自驾全景路书 (trip_mobile.html)
集成：
1. 国保地图对应点位增加代表性小照片（带序号圆形微缩图 + 点名 + 到达时刻）
2. 国保卡片增加斯飞坐标实景照片 Header
3. 餐饮 210 家老店街道坐标联动与高亮聚焦
4. 观鸟精简地标
5. 大地图底部面板防遮挡
"""

import os
import json

from dining_data_210 import TRIP_DATA, DINING_210_DATA
from birding_data_14d import BIRDING_14D_DATA, render_birding_html
from heritage_data_14d import HERITAGE_14D_DATA, HERITAGE_DAY_ROUTES, render_heritage_html

TRIP_DATA["dining_guide"] = DINING_210_DATA
TRIP_DATA["birding_guide"] = BIRDING_14D_DATA
TRIP_DATA["heritage_guide"] = HERITAGE_14D_DATA
TRIP_DATA["heritage_routes"] = HERITAGE_DAY_ROUTES


def render_dining_html_5_options():
    days_dining = []
    for d in DINING_210_DATA:
        day_num = d["day"]
        date_str = d["date"]
        city_str = d["city"]
        meals = d["meals"]

        meal_types = [
            ("breakfast", "🌅 早餐 (5选1)", meals["breakfast"]),
            ("lunch", "☀️ 午餐 (5选1)", meals["lunch"]),
            ("dinner", "🌙 晚餐 (5选1)", meals["dinner"])
        ]

        meals_html_blocks = []

        for m_key, m_title, m_options in meal_types:
            tabs_html = []
            cards_html = []

            for idx, opt in enumerate(m_options):
                opt_id = f"opt-{day_num}-{m_key}-{idx}"
                active_tab_cls = "active" if idx == 0 else ""
                active_card_cls = "style='display:block;'" if idx == 0 else "style='display:none;'"

                short_name = opt["restaurant"].split("(")[0].strip()
                if len(short_name) > 8:
                    short_name = short_name[:8] + "…"

                tab_btn = f"""
                <button class="m-dine-pill {active_tab_cls}" onclick="switchMealOption({day_num}, '{m_key}', {idx}, this)">
                  <span class="pill-num">{idx+1}</span> {short_name}
                </button>
                """
                tabs_html.append(tab_btn)

                orders_str = " · ".join(opt["must_orders"])
                card_content = f"""
                <div class="m-meal-option-detail" id="{opt_id}" {active_card_cls}>
                  <div class="m-meal-card-top">
                    <div class="m-meal-name"><b>{opt['restaurant']}</b></div>
                    <span class="m-badge-years">🏆 {opt['heritage_years']}</span>
                  </div>
                  <div class="m-meal-meta-row">
                    <span class="m-tag-source">{opt['source']}</span>
                    <span class="m-tag-price">{opt['price_per_person']}</span>
                  </div>
                  <div class="m-must-orders-box">
                    <span class="m-order-lbl">🍲 必点招牌：</span>{orders_str}
                  </div>
                  <div class="m-meal-desc-box">{opt['highlight']}</div>
                  <div style="display:flex; gap:6px; margin-top:8px;">
                    <button onclick="focusDineMapMarker({day_num}, '{m_key}', {idx})" class="m-dine-locate-btn">
                      📍 在上方地图查看位置
                    </button>
                    <a href="https://uri.amap.com/navigation?to={opt['lng']},{opt['lat']}&mode=car" class="m-dine-nav-btn" target="_blank">
                      🚗 高德导航
                    </a>
                  </div>
                </div>
                """
                cards_html.append(card_content)

            meal_section = f"""
            <div class="m-meal-section-box" id="meal-sec-{day_num}-{m_key}">
              <div class="m-meal-sec-header">{m_title}</div>
              <div class="m-dine-pills-bar">
                {"".join(tabs_html)}
              </div>
              <div class="m-dine-cards-wrapper">
                {"".join(cards_html)}
              </div>
            </div>
            """
            meals_html_blocks.append(meal_section)

        day_group = f"""
        <div class="m-dining-day-group" id="dine-day-{day_num}">
          <div class="m-dining-day-header" onclick="showDiningDayOnMap({day_num}, 'lunch', 0)">
            <span class="m-dine-day-badge">Day {day_num} · {date_str}</span>
            <span class="m-dine-city-badge">📍 {city_str} (点我看地图)</span>
          </div>
          {"".join(meals_html_blocks)}
        </div>
        """
        days_dining.append(day_group)

    return "\n".join(days_dining)


def build_mobile_split_screen_html():
    days_cards_html = []
    heritage_days = {h["day"] for h in HERITAGE_14D_DATA}

    for d in TRIP_DATA["days"]:
        chips = "".join([f'<span class="m-chip">{h}</span>' for h in d["highlights"]])
        
        warn = ""
        if d.get("warnings"):
            w_text = "<br>".join(d["warnings"])
            warn = f'<div class="m-warn">⚠️ {w_text}</div>'

        herit_btn = ""
        day_num = d["day"]
        if day_num in heritage_days:
            herit_btn = f'<button onclick="event.stopPropagation(); jumpToHeritage({day_num})" class="m-btn-herit">🏛️ 国保</button>'

        card = f"""
        <div class="m-card" id="m-day-{d['day']}" onclick="mFocusDay({d['day']})">
          <div class="m-card-header">
            <span class="m-day-badge">Day {d['day']} · {d['weekday']}</span>
            <span class="m-day-date">{d['date']}</span>
          </div>
          <div class="m-card-title">{d['title']}</div>
          
          <div class="m-chips-row">{chips}</div>

          <div class="m-stats-grid">
            <div class="m-stat">🚗 <b>{d['distance_km']}</b> km</div>
            <div class="m-stat">⏱️ <b>{d['duration']}</b></div>
            <div class="m-stat">🏔️ <b>{d['elevation_m']}</b> m</div>
            <div class="m-stat">💳 ¥<b>{d['tolls_rmb']}</b></div>
          </div>

          <div class="m-card-body">
            <div class="m-step"><span class="m-time">上午</span><span class="m-desc">{d['morning']}</span></div>
            <div class="m-step"><span class="m-time">下午</span><span class="m-desc">{d['afternoon']}</span></div>
            <div class="m-step"><span class="m-time">傍晚</span><span class="m-desc">{d['evening']}</span></div>
            {warn}
          </div>

          <div class="m-card-footer">
            <div class="m-stay">🏨 <b>{d['stay']}</b></div>
            <div class="m-nav-btns">
              <button onclick="event.stopPropagation(); jumpToDining({d['day']})" class="m-btn-dine">🍴 美食</button>
              <button onclick="event.stopPropagation(); jumpToBirding({d['day']})" class="m-btn-bird">🦉 观鸟</button>
              {herit_btn}
              <a href="https://uri.amap.com/navigation?from={d['from']['lng']},{d['from']['lat']}&to={d['to']['lng']},{d['to']['lat']}&mode=car" class="m-btn amap" target="_blank">导航</a>
            </div>
          </div>
        </div>
        """
        days_cards_html.append(card)

    all_days = "\n".join(days_cards_html)
    rules_html = "".join([f"<li>{r}</li>" for r in TRIP_DATA["critical_safeties"]])
    dining_html = render_dining_html_5_options()
    birding_html = render_birding_html()
    heritage_html = render_heritage_html()
    json_dump = json.dumps(TRIP_DATA, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <title>新疆14天自驾路书 (国保照片预览 + 观鸟 + 美食地图)</title>
  <!-- Leaflet CSS & JS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
  <!-- Leaflet PolylineDecorator -->
  <script src="https://cdn.jsdelivr.net/npm/leaflet-polylinedecorator@1.6.0/dist/leaflet.polylineDecorator.min.js"></script>
  <!-- Chart.js -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

  <style>
    :root {{
      --primary: #96382d;
      --bg: #090d16;
      --card-bg: #121a2c;
      --card-border: #1e2a44;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      -webkit-tap-highlight-color: transparent;
    }}
    html, body {{
      height: 100%;
      height: 100dvh;
      overflow: hidden;
      background-color: var(--bg);
      color: var(--text);
    }}

    .m-app-shell {{
      display: flex;
      flex-direction: column;
      height: 100%;
      height: 100dvh;
      width: 100%;
      position: relative;
    }}

    /* Compact Top Header */
    .m-header {{
      flex: 0 0 auto;
      background: linear-gradient(135deg, #1b2438 0%, #0d1322 100%);
      padding: 9px 12px 7px;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 100;
    }}
    .m-title-box h1 {{
      font-size: 14.5px;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .m-title-box p {{
      font-size: 10px;
      color: #cbd5e1;
    }}
    .m-header-badges {{
      display: flex;
      gap: 4px;
    }}
    .m-mini-badge {{
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(150, 56, 45, 0.25);
      color: #fca5a5;
      border: 1px solid rgba(150, 56, 45, 0.4);
    }}

    /* ========================================================
       TOP PINNED MAP ZONE
       ======================================================== */
    .m-map-pinned-zone {{
      flex: 0 0 35vh;
      min-height: 180px;
      max-height: 48vh;
      width: 100%;
      background: #0f172a;
      position: relative;
      border-bottom: 2px solid var(--card-border);
      box-shadow: 0 4px 16px rgba(0,0,0,0.5);
      z-index: 50;
      transition: flex-basis 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .m-map-pinned-zone.mode-compact {{
      flex-basis: 18vh;
      min-height: 120px;
    }}
    .m-map-pinned-zone.mode-hidden {{
      display: none !important;
    }}

    #m-map {{ width: 100%; height: 100%; }}

    .m-map-pill {{
      position: absolute;
      bottom: 8px;
      right: 8px;
      z-index: 500;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      border: 1px solid var(--card-border);
      color: #f1f5f9;
      font-size: 10px;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: 14px;
      display: flex;
      align-items: center;
      gap: 3px;
      box-shadow: 0 3px 8px rgba(0,0,0,0.6);
      cursor: pointer;
    }}

    .m-map-hint {{
      position: absolute;
      top: 6px;
      left: 8px;
      z-index: 500;
      background: rgba(13, 19, 34, 0.85);
      backdrop-filter: blur(6px);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 10.5px;
      color: #f8fafc;
      border-left: 2px solid #f87171;
      pointer-events: none;
      max-width: 80%;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }}

    /* Custom Map Markers */
    .custom-m-marker {{
      background: #96382d;
      color: #fff;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 10.5px;
      border: 1.5px solid #fff;
      box-shadow: 0 2px 5px rgba(0,0,0,0.5);
    }}
    .custom-dine-pin {{
      background: #1e293b;
      border: 1.5px solid #f59e0b;
      border-radius: 12px;
      padding: 2px 6px;
      color: #fff;
      font-size: 10px;
      font-weight: 700;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 3px;
      box-shadow: 0 3px 8px rgba(0,0,0,0.6);
    }}
    .custom-dine-pin.active {{
      background: #96382d;
      border-color: #f87171;
      box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.6);
      transform: scale(1.08);
    }}
    .custom-bird-pin {{
      background: #064e3b;
      border: 1.5px solid #34d399;
      border-radius: 12px;
      padding: 2px 7px;
      color: #fff;
      font-size: 10.5px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 3px 8px rgba(0,0,0,0.6);
    }}

    /* 国保带照片微缩图的地标样式 */
    .custom-herit-photo-marker {{
      display: flex;
      align-items: center;
      gap: 5px;
      background: rgba(24, 29, 51, 0.95);
      border: 1.5px solid #c084fc;
      border-radius: 18px;
      padding: 2px 8px 2px 2px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.6);
      cursor: pointer;
      white-space: nowrap;
    }}
    .herit-marker-thumb {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background-size: cover;
      background-position: center;
      border: 1.5px solid #fff;
      position: relative;
      flex-shrink: 0;
      box-shadow: 0 2px 5px rgba(0,0,0,0.4);
    }}
    .herit-marker-order {{
      position: absolute;
      top: -3px;
      left: -3px;
      background: #7e22ce;
      color: #fff;
      font-size: 8px;
      font-weight: 700;
      width: 13px;
      height: 13px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      border: 1px solid #fff;
    }}
    .herit-marker-info {{
      display: flex;
      flex-direction: column;
      line-height: 1.15;
    }}
    .herit-marker-name {{
      font-size: 10.5px;
      font-weight: 700;
      color: #fff;
    }}
    .herit-marker-time {{
      font-size: 9px;
      color: #fde68a;
      font-weight: 600;
    }}

    .custom-herit-leg-badge {{
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid #c084fc;
      border-radius: 10px;
      padding: 2px 6px;
      color: #fde68a;
      font-size: 9.5px;
      font-weight: 700;
      white-space: nowrap;
      box-shadow: 0 2px 6px rgba(0,0,0,0.6);
    }}

    /* ========================================================
       CONTENT VIEWS
       ======================================================== */
    .m-content-container {{
      flex: 1 1 auto;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      position: relative;
    }}

    .m-scroll-body {{
      padding: 10px 12px calc(65px + env(safe-area-inset-bottom));
    }}

    .m-metrics-strip {{
      display: flex;
      overflow-x: auto;
      gap: 6px;
      padding-bottom: 10px;
      scrollbar-width: none;
    }}
    .m-metrics-strip::-webkit-scrollbar {{ display: none; }}
    .m-m-box {{
      flex: 0 0 auto;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 6px 10px;
      text-align: center;
      min-width: 75px;
    }}
    .m-m-box .m-lbl {{ font-size: 9.5px; color: var(--text-muted); }}
    .m-m-box .m-val {{ font-size: 13.5px; font-weight: 700; color: #60a5fa; }}

    .m-rules-banner {{
      background: rgba(150, 56, 45, 0.15);
      border: 1px solid rgba(150, 56, 45, 0.4);
      border-radius: 10px;
      padding: 10px 12px;
      margin-bottom: 10px;
      font-size: 11.5px;
    }}
    .m-rules-banner h4 {{ color: #fca5a5; font-size: 12px; margin-bottom: 4px; }}
    .m-rules-banner ul {{ list-style: none; display: flex; flex-direction: column; gap: 4px; color: #e2e8f0; }}

    /* Timeline Day Card */
    .m-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      margin-bottom: 12px;
      overflow: hidden;
      box-shadow: 0 3px 10px rgba(0,0,0,0.35);
      transition: border-color 0.2s, transform 0.15s;
    }}
    .m-card:active {{ transform: scale(0.99); }}
    .m-card.active {{
      border-color: #f87171;
      box-shadow: 0 0 0 2px rgba(248, 113, 113, 0.45);
    }}
    .m-card-header {{
      padding: 9px 12px;
      background: rgba(255,255,255,0.02);
      border-bottom: 1px solid var(--card-border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .m-day-badge {{
      font-size: 12px;
      font-weight: 700;
      color: #fca5a5;
      background: rgba(150, 56, 45, 0.3);
      padding: 2px 7px;
      border-radius: 5px;
    }}
    .m-day-date {{ font-size: 11px; color: var(--text-muted); }}
    .m-card-title {{ font-size: 13.5px; font-weight: 700; color: #fff; padding: 9px 12px 6px; line-height: 1.35; }}
    .m-chips-row {{ display: flex; flex-wrap: wrap; gap: 4px; padding: 0 12px 8px; }}
    .m-chip {{ font-size: 10px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.05); color: #93c5fd; border: 1px solid rgba(147, 197, 253, 0.2); }}

    .m-stats-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      background: rgba(0,0,0,0.22);
      border-top: 1px dashed var(--card-border);
      padding: 6px 8px;
      font-size: 10.5px;
      color: var(--text-muted);
      text-align: center;
    }}
    .m-stat b {{ color: #f1f5f9; }}

    .m-card-body {{
      padding: 9px 12px;
      border-top: 1px dashed var(--card-border);
      display: flex;
      flex-direction: column;
      gap: 6px;
      font-size: 11.5px;
    }}
    .m-step {{ display: flex; gap: 6px; line-height: 1.4; }}
    .m-time {{ font-weight: 700; color: #94a3b8; min-width: 26px; font-size: 10.5px; }}
    .m-desc {{ color: #cbd5e1; flex: 1; }}
    .m-warn {{
      background: rgba(217, 119, 6, 0.15);
      border: 1px solid rgba(217, 119, 6, 0.4);
      border-radius: 6px;
      padding: 6px 9px;
      font-size: 11px;
      color: #fde68a;
      margin-top: 3px;
      line-height: 1.35;
    }}

    .m-card-footer {{
      padding: 9px 12px;
      background: rgba(0,0,0,0.3);
      border-top: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
      gap: 7px;
    }}
    .m-stay {{ font-size: 11.5px; color: var(--text-muted); }}
    .m-stay b {{ color: #f8fafc; font-weight: 500; }}
    
    .m-nav-btns {{ display: flex; gap: 4px; }}
    .m-btn-dine {{
      flex: 1;
      text-align: center;
      padding: 6px 0;
      border-radius: 6px;
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fcd34d;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .m-btn-bird {{
      flex: 1;
      text-align: center;
      padding: 6px 0;
      border-radius: 6px;
      background: rgba(16, 185, 129, 0.2);
      border: 1px solid rgba(16, 185, 129, 0.4);
      color: #6ee7b7;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .m-btn-herit {{
      flex: 1;
      text-align: center;
      padding: 6px 0;
      border-radius: 6px;
      background: rgba(147, 51, 234, 0.2);
      border: 1px solid rgba(147, 51, 234, 0.4);
      color: #c084fc;
      font-size: 10.5px;
      font-weight: 700;
      cursor: pointer;
    }}
    .m-btn {{
      flex: 0.85;
      text-align: center;
      padding: 6px 0;
      border-radius: 6px;
      text-decoration: none;
      font-size: 10.5px;
      font-weight: 600;
    }}
    .m-btn.amap {{ background: #2563eb; color: #fff; }}

    /* ========================================================
       TAB 2: DEDICATED FULLSCREEN MAP EXPLORER
       ======================================================== */
    .m-dedicated-map-view {{
      display: none;
      width: 100%;
      height: 100%;
      position: relative;
      background: #0f172a;
    }}
    #m-dedicated-map {{
      width: 100%;
      height: 100%;
      z-index: 1;
    }}

    .m-map-days-nav {{
      position: absolute;
      top: 10px;
      left: 10px;
      right: 10px;
      z-index: 500;
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding: 4px 6px;
      background: rgba(13, 19, 34, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 20px;
      scrollbar-width: none;
    }}
    .m-map-days-nav::-webkit-scrollbar {{ display: none; }}
    .m-map-day-pill {{
      flex: 0 0 auto;
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .m-map-day-pill.active {{
      background: #96382d;
      color: #fff;
    }}

    .m-layer-toggle-btn {{
      position: absolute;
      top: 55px;
      right: 12px;
      z-index: 500;
      background: rgba(15, 23, 42, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid var(--card-border);
      color: #f1f5f9;
      font-size: 10.5px;
      font-weight: 600;
      padding: 5px 9px;
      border-radius: 16px;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }}

    .m-map-info-sheet {{
      position: absolute;
      bottom: calc(64px + env(safe-area-inset-bottom));
      left: 12px;
      right: 12px;
      z-index: 500;
      background: rgba(19, 27, 46, 0.95);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 12px 14px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.6);
    }}
    .m-map-info-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }}
    .m-map-info-title {{ font-size: 13.5px; font-weight: 700; color: #fff; }}
    .m-map-info-stats {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      background: rgba(0,0,0,0.25);
      padding: 6px 8px;
      border-radius: 8px;
      font-size: 10.5px;
      color: var(--text-muted);
      text-align: center;
      margin-bottom: 8px;
    }}
    .m-map-info-stats b {{ color: #60a5fa; }}
    .m-map-info-actions {{
      display: flex;
      gap: 8px;
    }}
    .m-map-info-btn {{
      flex: 1;
      text-align: center;
      padding: 8px 0;
      border-radius: 6px;
      font-size: 11.5px;
      font-weight: 700;
      text-decoration: none;
      cursor: pointer;
    }}
    .m-map-info-btn.nav {{ background: #2563eb; color: #fff; border: none; }}
    .m-map-info-btn.dine {{ background: rgba(245,158,11,0.25); border: 1px solid rgba(245,158,11,0.5); color: #fcd34d; }}

    /* ========================================================
       TAB 3: DINING 5-OPTIONS
       ======================================================== */
    .m-dining-view {{
      display: none;
      padding: 12px 12px calc(65px + env(safe-area-inset-bottom));
    }}
    .m-dining-intro {{
      background: linear-gradient(135deg, rgba(217, 119, 6, 0.18) 0%, rgba(150, 56, 45, 0.18) 100%);
      border: 1px solid rgba(245, 158, 11, 0.4);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 14px;
      font-size: 11.5px;
      color: #fde68a;
      line-height: 1.45;
    }}

    .m-dining-day-group {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 12px;
      margin-bottom: 16px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .m-dining-day-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--card-border);
      cursor: pointer;
    }}
    .m-dine-day-badge {{ font-size: 14px; font-weight: 700; color: #fca5a5; }}
    .m-dine-city-badge {{ font-size: 11px; color: #60a5fa; background: rgba(37,99,235,0.15); padding: 2px 7px; border-radius: 4px; font-weight: 600; }}

    .m-meal-section-box {{
      background: rgba(255,255,255,0.015);
      border: 1px solid rgba(255,255,255,0.05);
      border-radius: 10px;
      padding: 10px 10px 12px;
      margin-bottom: 12px;
    }}
    .m-meal-sec-header {{ font-size: 12.5px; font-weight: 700; color: #f87171; margin-bottom: 8px; }}

    .m-dine-pills-bar {{
      display: flex;
      overflow-x: auto;
      gap: 6px;
      padding-bottom: 8px;
      scrollbar-width: none;
      -webkit-overflow-scrolling: touch;
    }}
    .m-dine-pills-bar::-webkit-scrollbar {{ display: none; }}
    .m-dine-pill {{
      flex: 0 0 auto;
      background: #1a2336;
      border: 1px solid #2a3754;
      color: #94a3b8;
      font-size: 11px;
      padding: 4px 9px;
      border-radius: 14px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.2s;
    }}
    .m-dine-pill .pill-num {{
      display: inline-block;
      width: 15px;
      height: 15px;
      line-height: 15px;
      text-align: center;
      background: rgba(255,255,255,0.1);
      border-radius: 50%;
      font-size: 9px;
      font-weight: 700;
    }}
    .m-dine-pill.active {{
      background: #96382d;
      border-color: #f87171;
      color: #fff;
      font-weight: 600;
    }}
    .m-dine-pill.active .pill-num {{ background: #fff; color: #96382d; }}

    .m-meal-option-detail {{
      background: rgba(0,0,0,0.25);
      border: 1px solid var(--card-border);
      border-radius: 8px;
      padding: 10px 12px;
      margin-top: 4px;
    }}
    .m-meal-card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }}
    .m-meal-name {{ font-size: 13.5px; color: #f8fafc; }}
    .m-badge-years {{ font-size: 10.5px; font-weight: 600; color: #fca5a5; background: rgba(150, 56, 45, 0.3); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(150, 56, 45, 0.4); }}
    .m-meal-meta-row {{ display: flex; gap: 6px; margin-bottom: 6px; font-size: 10px; }}
    .m-tag-source {{ background: rgba(245, 158, 11, 0.15); color: #fbbf24; padding: 1px 5px; border-radius: 3px; border: 1px solid rgba(245, 158, 11, 0.3); }}
    .m-tag-price {{ background: rgba(16, 185, 129, 0.15); color: #34d399; padding: 1px 5px; border-radius: 3px; }}

    .m-must-orders-box {{ font-size: 11.5px; color: #f1f5f9; margin-bottom: 5px; line-height: 1.35; }}
    .m-order-lbl {{ color: #fbbf24; font-weight: 700; }}
    .m-meal-desc-box {{ font-size: 11px; color: #94a3b8; line-height: 1.4; margin-bottom: 8px; }}
    
    .m-dine-locate-btn {{
      flex: 1;
      text-align: center;
      background: rgba(245, 158, 11, 0.22);
      border: 1px solid rgba(245, 158, 11, 0.6);
      color: #fcd34d;
      padding: 7px 0;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
    }}
    .m-dine-locate-btn:active {{ background: #96382d; color: #fff; border-color: #f87171; }}
    .m-dine-nav-btn {{
      flex: 1;
      text-align: center;
      background: #1e293b;
      border: 1px solid #334155;
      color: #60a5fa;
      padding: 7px 0;
      border-radius: 6px;
      text-decoration: none;
      font-size: 11px;
      font-weight: 600;
    }}
    .m-dine-nav-btn:active {{ background: #2563eb; color: #fff; }}

    /* ========================================================
       TAB 4: BIRDING & WILDLIFE
       ======================================================== */
    .m-birding-view {{
      display: none;
      padding: 12px 12px calc(65px + env(safe-area-inset-bottom));
    }}
    .m-birding-intro {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.18) 0%, rgba(59, 130, 246, 0.18) 100%);
      border: 1px solid rgba(16, 185, 129, 0.4);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 14px;
      font-size: 11.5px;
      color: #6ee7b7;
      line-height: 1.45;
    }}
    .m-birding-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 14px;
      margin-bottom: 14px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      cursor: pointer;
    }}
    .m-bird-card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .m-bird-day-tag {{
      font-size: 13px;
      font-weight: 700;
      color: #fca5a5;
      background: rgba(150, 56, 45, 0.25);
      padding: 2px 7px;
      border-radius: 5px;
    }}
    .m-bird-city-tag {{
      font-size: 11px;
      color: #34d399;
      background: rgba(16, 185, 129, 0.15);
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
    }}
    .m-bird-loc-name {{
      font-size: 14px;
      color: #fff;
      margin-bottom: 6px;
    }}
    .m-bird-lbl {{
      font-weight: 700;
      color: #94a3b8;
      font-size: 11px;
    }}
    .m-bird-time-box {{
      font-size: 12px;
      color: #fde68a;
      background: rgba(217, 119, 6, 0.15);
      padding: 4px 8px;
      border-radius: 6px;
      margin-bottom: 6px;
    }}
    .m-bird-habitat-box {{
      font-size: 11.5px;
      color: #cbd5e1;
      margin-bottom: 6px;
    }}
    .m-bird-chips-container {{
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
      margin-bottom: 8px;
    }}
    .m-bird-species-chip {{
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 5px;
      background: rgba(16, 185, 129, 0.15);
      color: #6ee7b7;
      border: 1px solid rgba(16, 185, 129, 0.35);
      font-weight: 600;
    }}
    .m-bird-notes-box {{
      font-size: 11.5px;
      color: #94a3b8;
      line-height: 1.45;
      background: rgba(0,0,0,0.2);
      padding: 8px 10px;
      border-radius: 6px;
      margin-bottom: 10px;
    }}
    .m-bird-nav-btn {{
      display: block;
      width: 100%;
      text-align: center;
      background: #059669;
      color: #fff;
      padding: 6px 0;
      border-radius: 6px;
      text-decoration: none;
      font-size: 11px;
      font-weight: 600;
    }}

    /* ========================================================
       TAB 5: CULTURE (国保超深度研学 + 实景大图卡片)
       ======================================================== */
    .m-culture-view {{
      display: none;
      padding: 12px 12px calc(65px + env(safe-area-inset-bottom));
    }}
    .m-culture-intro {{
      background: linear-gradient(135deg, rgba(147, 51, 234, 0.18) 0%, rgba(217, 119, 6, 0.18) 100%);
      border: 1px solid rgba(147, 51, 234, 0.4);
      border-radius: 12px;
      padding: 12px 14px;
      margin-bottom: 14px;
      font-size: 11.5px;
      color: #e9d5ff;
      line-height: 1.5;
    }}
    .m-herit-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      margin-bottom: 16px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.35);
      cursor: pointer;
      overflow: hidden;
    }}
    .m-herit-img-header {{
      height: 130px;
      background-size: cover;
      background-position: center;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 10px 12px;
    }}
    .m-herit-img-badge {{
      align-self: flex-start;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(4px);
      color: #e9d5ff;
      font-size: 9.5px;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid rgba(192, 132, 252, 0.4);
    }}
    .m-herit-img-title {{
      color: #fff;
      font-size: 15.5px;
      font-weight: 700;
      text-shadow: 0 2px 6px rgba(0,0,0,0.85);
    }}
    .m-herit-body-inner {{
      padding: 12px 14px 14px;
    }}

    .m-herit-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }}
    .m-herit-day-tag {{
      font-size: 13px;
      font-weight: 700;
      color: #fca5a5;
      background: rgba(150, 56, 45, 0.25);
      padding: 2px 7px;
      border-radius: 5px;
    }}
    .m-herit-city-tag {{
      font-size: 11px;
      color: #c084fc;
      background: rgba(147, 51, 234, 0.15);
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
    }}
    .m-herit-batch {{
      font-size: 11px;
      color: #fbbf24;
      font-weight: 600;
      margin-bottom: 4px;
    }}
    .m-herit-sifei {{
      font-size: 10.5px;
      color: #94a3b8;
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 1px dashed var(--card-border);
    }}
    .m-herit-schedule-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px;
      background: rgba(0,0,0,0.25);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 11px;
      margin-bottom: 10px;
    }}
    .m-herit-sched-item b {{ color: #60a5fa; }}
    .m-herit-lbl {{ font-weight: 700; color: #94a3b8; font-size: 11px; }}

    .m-herit-chips-box {{
      margin-bottom: 10px;
    }}
    .m-herit-chips-flow {{
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .m-herit-chip {{
      font-size: 11px;
      color: #cbd5e1;
      background: rgba(255,255,255,0.03);
      padding: 3px 6px;
      border-radius: 4px;
      border-left: 2px solid #a855f7;
    }}

    .m-herit-notes-box {{
      background: rgba(147, 51, 234, 0.08);
      border: 1px solid rgba(147, 51, 234, 0.25);
      border-radius: 8px;
      padding: 10px 12px;
      margin-bottom: 10px;
    }}
    .m-herit-notes-title {{
      font-size: 11.5px;
      font-weight: 700;
      color: #d8b4fe;
      margin-bottom: 6px;
    }}
    .m-herit-notes-body {{
      font-size: 11.5px;
      color: #cbd5e1;
      line-height: 1.55;
    }}

    .m-herit-photo-box {{
      background: rgba(217, 119, 6, 0.12);
      border: 1px solid rgba(217, 119, 6, 0.3);
      border-radius: 8px;
      padding: 8px 10px;
      font-size: 11.5px;
      color: #fde68a;
      line-height: 1.45;
      margin-bottom: 10px;
    }}

    .m-herit-nav-btn {{
      display: block;
      width: 100%;
      text-align: center;
      background: #7e22ce;
      color: #fff;
      padding: 7px 0;
      border-radius: 6px;
      text-decoration: none;
      font-size: 11px;
      font-weight: 600;
    }}

    /* ========================================================
       TAB 6: TIPS
       ======================================================== */
    .m-tips-view {{
      display: none;
      padding: 12px 12px calc(65px + env(safe-area-inset-bottom));
    }}

    .m-sub-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      padding: 14px;
      margin-bottom: 12px;
    }}
    .m-sub-card h3 {{ font-size: 14px; color: #f87171; margin-bottom: 8px; }}

    /* Bottom App Dock */
    .m-bottom-dock {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      height: calc(52px + env(safe-area-inset-bottom));
      padding-bottom: env(safe-area-inset-bottom);
      background: rgba(13, 19, 34, 0.96);
      backdrop-filter: blur(16px);
      border-top: 1px solid var(--card-border);
      display: flex;
      justify-content: space-around;
      align-items: center;
      z-index: 1000;
    }}
    .m-dock-item {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: var(--text-muted);
      font-size: 10px;
      cursor: pointer;
      width: 16.6%;
      height: 100%;
    }}
    .m-dock-item .m-dock-icon {{ font-size: 16px; margin-bottom: 1px; }}
    .m-dock-item.active {{
      color: #f87171;
      font-weight: 700;
    }}
  </style>
</head>
<body>

  <div class="m-app-shell">

    <!-- 顶部紧凑标题栏 -->
    <div class="m-header">
      <div class="m-title-box">
        <h1>🧭 {TRIP_DATA['title']}</h1>
        <p>{TRIP_DATA['subtitle']}</p>
      </div>
      <div class="m-header-badges">
        <span class="m-mini-badge">📅 {TRIP_DATA['dates']}</span>
      </div>
    </div>

    <!-- 顶部自适应联动常驻小地图 -->
    <div class="m-map-pinned-zone" id="m-map-zone">
      <div id="m-map"></div>
      <div class="m-map-hint" id="m-top-map-hint">🗺️ 行程路线 · 点下方卡片联动</div>
      <button class="m-map-pill" onclick="cycleTimelineMapHeight()">
        <span id="pill-icon">↕️</span> <span id="pill-text">高度 35%</span>
      </button>
    </div>

    <!-- 可滚动主体内容区域 -->
    <div class="m-content-container" id="m-content-container">

      <!-- ==================== 1. 行程页 ==================== -->
      <div class="m-scroll-body" id="m-view-timeline">
        <div class="m-metrics-strip">
          <div class="m-m-box"><div class="m-lbl">总里程</div><div class="m-val">{TRIP_DATA['summary']['total_distance_km']} <small style="font-size:9px;">km</small></div></div>
          <div class="m-m-box"><div class="m-lbl">总耗时</div><div class="m-val">{TRIP_DATA['summary']['total_driving_hours']} <small style="font-size:9px;">h</small></div></div>
          <div class="m-m-box"><div class="m-lbl">高速费</div><div class="m-val">¥{TRIP_DATA['summary']['total_tolls_rmb']}</div></div>
          <div class="m-m-box"><div class="m-lbl">燃油费</div><div class="m-val">¥{TRIP_DATA['summary']['total_fuel_cost_rmb']}</div></div>
          <div class="m-m-box"><div class="m-lbl">总预算</div><div class="m-val">¥{TRIP_DATA['summary']['total_budget_rmb']}</div></div>
        </div>

        <div class="m-rules-banner">
          <h4>🛡️ 核心安全与关键规则</h4>
          <ul>{rules_html}</ul>
        </div>

        {all_days}
      </div>

      <!-- ==================== 3. 餐饮页 (每餐5选1) ==================== -->
      <div class="m-dining-view" id="m-view-dining">
        <div class="m-dining-intro">
          🏆 <b>210家多年老店 ✕ 本地人扎堆老号地图：</b><br>
          已在上方地图实时标记出当前日的备选餐馆位置与店名！点击餐馆或切换餐别，地图将精准聚焦！
        </div>
        {dining_html}
      </div>

      <!-- ==================== 4. 观鸟与野生动物页 ==================== -->
      <div class="m-birding-view" id="m-view-birding">
        <div class="m-birding-intro">
          🦉 <b>小红书 ✕ 中国观鸟记录中心实战纪录：</b><br>
          上方地图已实时标出当天最佳观鸟点！点击任一天即可在地图上查看位置与一键导航。
        </div>
        {birding_html}
      </div>

      <!-- ==================== 5. 国保超深度研学专区 (斯飞坐标/华夏古迹图) ==================== -->
      <div class="m-culture-view" id="m-view-culture">
        <div class="m-culture-intro">
          🏛️ <b>全国重点文物保护单位 ✕ 斯飞坐标收录实景：</b><br>
          上方地图已标出各处国保的<b>代表性实景微缩照片、行进路线、前进方向箭头与点对点距离/耗时标牌</b>！
        </div>
        {heritage_html}
      </div>

      <!-- ==================== 6. 提醒页 (海拔剖面 + 极寒装备 + 安全整合) ==================== -->
      <div class="m-tips-view" id="m-view-tips">
        <!-- 海拔变化曲线 -->
        <div class="m-sub-card">
          <h3>🏔️ 14天自驾落脚点海拔变化曲线 (米)</h3>
          <p style="font-size:11px; color:var(--text-muted); margin-bottom:10px;">乌鲁木齐 (918m) ➔ 喀纳斯湖 (1374m) ➔ 吐鲁番盆地 (30m)</p>
          <div style="height: 240px;">
            <canvas id="mChart"></canvas>
          </div>
        </div>

        <!-- 极寒冰雪装备 -->
        <div class="m-sub-card">
          <h3>❄️ 高尔夫极寒冰雪行车自检清单</h3>
          <div style="font-size:11.5px; color:#cbd5e1; line-height:1.6;">
            • <b>雪地胎：</b>驱动轮在布尔津必须换装深度花纹雪地胎。<br>
            • <b>防滑链：</b>后备箱常备匹配高尔夫尺寸的金属防滑链（提前试装）。<br>
            • <b>应急物资：</b>折叠雪铲、搭电宝、拖车绳、-35#极寒防冻玻璃水。<br>
            • <b>极寒防寒：</b>禾木清晨（-15°C~-18°C）穿长款厚羽绒服 + 防滑雪地靴。
          </div>
        </div>

        <!-- 安全规则机制 -->
        <div class="m-sub-card">
          <h3>🛡️ 新疆自驾核心安全与避坑守则</h3>
          <div style="font-size:11.5px; color:#fde68a; line-height:1.6;">
            • <b>防暗冰：</b>喀纳斯/禾木盘山公路背阴弯道易结暗冰，使用低速挡平稳减速，严禁猛打方向。<br>
            • <b>闭馆时间：</b>可可托海 08:30 启程避开极寒；北庭故城 14:30 抵达避开冬季提前闭馆。<br>
            • <b>达坂城横风缓冲：</b>返程预留百里风区车速控制与安检时间。
          </div>
        </div>
      </div>

    </div>

    <!-- ==================== 2. 独立全屏大地图探索台 ==================== -->
    <div class="m-dedicated-map-view" id="m-view-map">
      <div id="m-dedicated-map"></div>

      <div class="m-map-days-nav" id="m-map-pills-bar">
        <button class="m-map-day-pill active" onclick="focusDedicatedDay(0, this)">🗺️ 全程总览</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(1, this)">Day 1 乌市</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(2, this)">Day 2 福海</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(3, this)">Day 3 布尔津</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(4, this)">Day 4 禾木</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(5, this)">Day 5 禾木</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(6, this)">Day 6 喀纳斯</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(7, this)">Day 7 喀纳斯</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(8, this)">Day 8 富蕴</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(9, this)">Day 9 奇台</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(10, this)">Day 10 吐鲁番</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(11, this)">Day 11 东郊</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(12, this)">Day 12 故城</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(13, this)">Day 13 水利</button>
        <button class="m-map-day-pill" onclick="focusDedicatedDay(14, this)">Day 14 归途</button>
      </div>

      <button class="m-layer-toggle-btn" onclick="toggleMapLayer()">🗺️ 切换标准路网</button>

      <div class="m-map-info-sheet" id="m-map-info-box">
        <div class="m-map-info-top">
          <div class="m-map-info-title" id="m-info-title">新疆14天自驾全景路线</div>
          <span class="m-mini-badge" id="m-info-badge">总览 2380km</span>
        </div>
        <div class="m-map-info-stats">
          <div>🚗 里程: <b id="m-info-dist">2380 km</b></div>
          <div>⏱️ 耗时: <b id="m-info-time">37.5 h</b></div>
          <div>🏔️ 海拔: <b id="m-info-elev">918m</b></div>
          <div>💳 高速: <b id="m-info-tolls">¥820</b></div>
        </div>
        <div class="m-map-info-actions">
          <button class="m-map-info-btn dine" id="m-info-btn-dine" onclick="jumpToDining(1)">🍴 当天美食 (5选1)</button>
          <a class="m-map-info-btn nav" id="m-info-btn-nav" href="https://uri.amap.com/navigation?to=87.616848,43.825592&mode=car" target="_blank">🚗 高德路线导航</a>
        </div>
      </div>
    </div>

    <!-- 底部 6 位 Dock 导航栏 -->
    <div class="m-bottom-dock">
      <div class="m-dock-item active" onclick="mSwitch('timeline', this)">
        <div class="m-dock-icon">📅</div>
        <span>行程</span>
      </div>
      <div class="m-dock-item" onclick="mSwitch('map', this)">
        <div class="m-dock-icon">🗺️</div>
        <span>大地图</span>
      </div>
      <div class="m-dock-item" onclick="mSwitch('dining', this)">
        <div class="m-dock-icon">🍽️</div>
        <span>餐饮</span>
      </div>
      <div class="m-dock-item" onclick="mSwitch('birding', this)">
        <div class="m-dock-icon">🦉</div>
        <span>观鸟</span>
      </div>
      <div class="m-dock-item" onclick="mSwitch('culture', this)">
        <div class="m-dock-icon">🏛️</div>
        <span>国保</span>
      </div>
      <div class="m-dock-item" onclick="mSwitch('tips', this)">
        <div class="m-dock-icon">🔔</div>
        <span>提醒</span>
      </div>
    </div>

  </div>

  <script>
    const mTripData = {json_dump};

    // ==========================================
    // 1. 初始化顶部全局自适应小地图
    // ==========================================
    const mMap = L.map('m-map', {{
      zoomControl: false,
      attributionControl: false
    }}).setView([45.5, 87.5], 6);

    L.tileLayer('https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={{x}}&y={{y}}&z={{z}}', {{
      subdomains: ['1', '2', '3', '4'],
      minZoom: 4,
      maxZoom: 18
    }}).addTo(mMap);

    const dynamicLayers = L.layerGroup().addTo(mMap);

    const mMarkers = [];
    const mLatLngs = [];

    mTripData.days.forEach(d => {{
      const lat = d.to.lat;
      const lng = d.to.lng;
      mLatLngs.push([lat, lng]);

      const iconHtml = `<div class="custom-m-marker">${{d.day}}</div>`;
      const cIcon = L.divIcon({{ className: 'm-div-icon', html: iconHtml, iconSize: [20, 20], iconAnchor: [10, 10] }});

      const mk = L.marker([lat, lng], {{ icon: cIcon }});
      mk.bindPopup(`
        <div style="font-size:12px; color:#0f172a; line-height:1.4;">
          <b style="color:#96382d;">Day ${{d.day}}: ${{d.title}}</b><br/>
          🏔️ 海拔: ${{d.elevation_m}}m ｜ 🚗 ${{d.distance_km}}km<br/>
          🏨 ${{d.stay}}
        </div>
      `);
      mk.on('click', () => {{ mHighlightAndScrollCard(d.day); }});
      mMarkers.push({{ day: d.day, mk, lat, lng }});
    }});

    const mPolyline = L.polyline(mLatLngs, {{
      color: '#f87171',
      weight: 2.5,
      opacity: 0.85,
      dashArray: '5, 5'
    }});

    function setupRouteWithArrows() {{
      dynamicLayers.clearLayers();
      mPolyline.addTo(dynamicLayers);
      mMarkers.forEach(m => m.mk.addTo(dynamicLayers));

      if (window.L && L.polylineDecorator) {{
        try {{
          L.polylineDecorator(mPolyline, {{
            patterns: [
              {{
                offset: 20,
                repeat: 55,
                symbol: L.Symbol.arrowHead({{
                  pixelSize: 8,
                  polygon: false,
                  pathOptions: {{ stroke: true, color: '#fca5a5', weight: 2.5, opacity: 0.95 }}
                }})
              }}
            ]
          }}).addTo(dynamicLayers);
        }} catch(e) {{
          console.warn("Decorator error", e);
        }}
      }}
    }}

    setupRouteWithArrows();

    if (mLatLngs.length > 0) {{
      mMap.fitBounds(mPolyline.getBounds(), {{ padding: [15, 15] }});
    }}

    function mFocusDay(dayNum) {{
      document.querySelectorAll('.m-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('m-day-' + dayNum);
      if (activeCard) activeCard.classList.add('active');

      const target = mMarkers.find(m => m.day === dayNum);
      if (target) {{
        mMap.flyTo([target.lat, target.lng], 8, {{ duration: 0.6 }});
        target.mk.openPopup();
      }}
    }}

    function mHighlightAndScrollCard(dayNum) {{
      document.querySelectorAll('.m-card').forEach(c => c.classList.remove('active'));
      const activeCard = document.getElementById('m-day-' + dayNum);
      if (activeCard) {{
        activeCard.classList.add('active');
        activeCard.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}

    let timelineMapMode = 0;
    function cycleTimelineMapHeight() {{
      const zone = document.getElementById('m-map-zone');
      const text = document.getElementById('pill-text');
      timelineMapMode = (timelineMapMode + 1) % 2;
      if (timelineMapMode === 0) {{
        zone.classList.remove('mode-compact');
        text.innerText = "高度 35%";
      }} else {{
        zone.classList.add('mode-compact');
        text.innerText = "小窗 18%";
      }}
      setTimeout(() => {{ mMap.invalidateSize(); }}, 250);
    }}

    // ==========================================
    // 2. 餐饮专区 (地图精准标记餐馆街道坐标与高亮)
    // ==========================================
    let currentDineMarkers = [];
    function showDiningDayOnMap(dayNum, targetMealKey = 'lunch', activeIdx = 0) {{
      const dayData = mTripData.dining_guide.find(d => d.day === dayNum);
      if (!dayData) return;

      dynamicLayers.clearLayers();
      currentDineMarkers = [];
      const pts = [];

      const hint = document.getElementById('m-top-map-hint');
      hint.innerText = `🍽️ Day ${{dayNum}} · ${{dayData.city.split('(')[0]}} 候选餐馆地图`;

      const meals = dayData.meals;
      const mealList = [
        {{ key: 'breakfast', label: '早', items: meals.breakfast }},
        {{ key: 'lunch', label: '午', items: meals.lunch }},
        {{ key: 'dinner', label: '晚', items: meals.dinner }}
      ];

      const curMealObj = mealList.find(m => m.key === targetMealKey) || mealList[1];

      curMealObj.items.forEach((opt, idx) => {{
        const lat = opt.lat;
        const lng = opt.lng;
        pts.push([lat, lng]);

        const isAct = (idx === activeIdx);
        const actCls = isAct ? 'active' : '';
        const shortName = opt.restaurant.split('(')[0].trim();

        const html = `<div class="custom-dine-pin ${{actCls}}"><span>${{idx+1}}</span> <b>${{shortName}}</b></div>`;
        const icon = L.divIcon({{ className: 'dine-div-icon', html: html, iconSize: null, iconAnchor: [15, 12] }});

        const mk = L.marker([lat, lng], {{ icon: icon }}).addTo(dynamicLayers);
        mk.bindPopup(`
          <div style="font-size:12px; line-height:1.4; color:#0f172a;">
            <b style="color:#96382d;">${{opt.restaurant}}</b> (${{opt.heritage_years}})<br/>
            💰 人均: ${{opt.price_per_person}}<br/>
            🍲 招牌: ${{opt.must_orders.slice(0,3).join('、')}}<br/>
            <a href="https://uri.amap.com/navigation?to=${{lng}},${{lat}}&mode=car" target="_blank" style="display:inline-block; margin-top:4px; color:#2563eb; font-weight:700;">🚗 高德一键导航</a>
          </div>
        `);
        if (isAct) {{
          mk.openPopup();
        }}
        currentDineMarkers.push({{ idx, mk, lat, lng, opt }});
      }});

      if (pts.length > 0) {{
        if (activeIdx >= 0 && activeIdx < pts.length) {{
          mMap.flyTo(pts[activeIdx], 14, {{ duration: 0.5 }});
        }} else {{
          const bounds = L.latLngBounds(pts);
          mMap.fitBounds(bounds, {{ padding: [35, 35], maxZoom: 15, duration: 0.5 }});
        }}
      }}
    }}

    function switchMealOption(dayNum, mealKey, optIdx, btnEl) {{
      const section = btnEl ? btnEl.closest('.m-meal-section-box') : document.getElementById(`meal-sec-${{dayNum}}-${{mealKey}}`);
      if (section) {{
        section.querySelectorAll('.m-dine-pill').forEach((pill, idx) => {{
          if (idx === optIdx) pill.classList.add('active');
          else pill.classList.remove('active');
        }});

        section.querySelectorAll('.m-meal-option-detail').forEach((detail, idx) => {{
          if (idx === optIdx) detail.style.display = 'block';
          else detail.style.display = 'none';
        }});
      }}

      showDiningDayOnMap(dayNum, mealKey, optIdx);
    }}

    function focusDineMapMarker(dayNum, mealKey, idx) {{
      showDiningDayOnMap(dayNum, mealKey, idx);
      const target = currentDineMarkers.find(m => m.idx === idx);
      if (target) {{
        mMap.flyTo([target.lat, target.lng], 15, {{ duration: 0.5 }});
        target.mk.openPopup();
      }}
    }}

    // ==========================================
    // 3. 观鸟专区 (地图精简仅显示名称)
    // ==========================================
    function showBirdingDayOnMap(dayNum) {{
      const b = mTripData.birding_guide.find(item => item.day === dayNum);
      if (!b) return;

      dynamicLayers.clearLayers();

      const hint = document.getElementById('m-top-map-hint');
      hint.innerText = `🦉 Day ${{dayNum}} · ${{b.city}} 观鸟点: ${{b.location}}`;

      const html = `<div class="custom-bird-pin">🦉 <b>${{b.location}}</b></div>`;
      const icon = L.divIcon({{ className: 'bird-div-icon', html: html, iconSize: null, iconAnchor: [20, 12] }});

      const mk = L.marker([b.lat, b.lng], {{ icon: icon }}).addTo(dynamicLayers);
      
      L.circle([b.lat, b.lng], {{
        radius: 1200,
        color: '#10b981',
        fillColor: '#10b981',
        fillOpacity: 0.15,
        weight: 1.5,
        dashArray: '3, 3'
      }}).addTo(dynamicLayers);

      mk.bindPopup(`
        <div style="font-size:12px; font-weight:700; color:#059669; padding:2px;">
          🦉 ${{b.location}}
        </div>
      `).openPopup();

      mMap.flyTo([b.lat, b.lng], 13, {{ duration: 0.6 }});
    }}

    // ==========================================
    // 4. 国保专区 (带代表性小照片的预览标牌与时间路线)
    // ==========================================
    function showHeritageDayOnMap(dayNum) {{
      const routeInfo = mTripData.heritage_routes[dayNum];
      if (!routeInfo) return;

      dynamicLayers.clearLayers();
      const hint = document.getElementById('m-top-map-hint');
      hint.innerText = `🏛️ Day ${{dayNum}} · 国保实景照片与行进路线`;

      const pts = [];

      routeInfo.stops.forEach((s, idx) => {{
        pts.push([s.lat, s.lng]);
        
        // 代表性小照片预览标牌
        const html = `
          <div class="custom-herit-photo-marker">
            <div class="herit-marker-thumb" style="background-image: url('${{s.img}}');">
              <span class="herit-marker-order">${{s.order}}</span>
            </div>
            <div class="herit-marker-info">
              <div class="herit-marker-name">${{s.name}}</div>
              <div class="herit-marker-time">⏰ ${{s.time}}</div>
            </div>
          </div>
        `;
        const icon = L.divIcon({{ className: 'herit-photo-div-icon', html: html, iconSize: null, iconAnchor: [35, 18] }});

        const mk = L.marker([s.lat, s.lng], {{ icon: icon }}).addTo(dynamicLayers);
        mk.bindPopup(`
          <div style="font-size:12px; line-height:1.45; color:#0f172a; min-width:200px;">
            <img src="${{s.img}}" style="width:100%; height:95px; object-fit:cover; border-radius:6px; margin-bottom:6px; display:block;" onerror="this.style.display='none';" />
            <b style="color:#7e22ce;">第${{s.order}}站：${{s.name}}</b><br/>
            <small style="color:#64748b;">📷 ${{s.caption || ''}}</small><br/>
            ⏰ 计划到达: <b>${{s.time}}</b><br/>
            <a href="https://uri.amap.com/navigation?to=${{s.lng}},${{s.lat}}&mode=car" target="_blank" style="display:inline-block; margin-top:6px; color:#7e22ce; font-weight:700;">🚗 高德一键导航</a>
          </div>
        `);
      }});

      if (pts.length > 1) {{
        const heritPolyline = L.polyline(pts, {{
          color: '#c084fc',
          weight: 3.5,
          opacity: 0.9,
          dashArray: '6, 6'
        }}).addTo(dynamicLayers);

        if (window.L && L.polylineDecorator) {{
          try {{
            L.polylineDecorator(heritPolyline, {{
              patterns: [
                {{
                  offset: '25%',
                  repeat: '50%',
                  symbol: L.Symbol.arrowHead({{
                    pixelSize: 10,
                    polygon: false,
                    pathOptions: {{ stroke: true, color: '#fde68a', weight: 3, opacity: 1 }}
                  }})
                }}
              ]
            }}).addTo(dynamicLayers);
          }} catch(e) {{
            console.warn("Decorator error", e);
          }}
        }}

        if (routeInfo.legs && routeInfo.legs.length > 0) {{
          routeInfo.legs.forEach((leg, i) => {{
            const p1 = pts[i];
            const p2 = pts[i+1];
            if (p1 && p2) {{
              const midLat = (p1[0] + p2[0]) / 2;
              const midLng = (p1[1] + p2[1]) / 2;

              const badgeHtml = `<div class="custom-herit-leg-badge">🚗 ${{leg.distance_km}}km · ${{leg.duration_min}}分</div>`;
              const badgeIcon = L.divIcon({{ className: 'leg-badge-icon', html: badgeHtml, iconSize: null, iconAnchor: [35, 10] }});
              L.marker([midLat, midLng], {{ icon: badgeIcon }}).addTo(dynamicLayers);
            }}
          }});
        }}

        mMap.fitBounds(heritPolyline.getBounds(), {{ padding: [35, 35], duration: 0.6 }});
      }} else if (pts.length === 1) {{
        mMap.flyTo(pts[0], 13, {{ duration: 0.6 }});
      }}
    }}

    // ==========================================
    // 5. 初始化独立全屏大地图探索台
    // ==========================================
    let dedicatedMap = null;
    let transitLayer = null;
    let standardLayer = null;
    let isStandardMode = false;
    const dedicatedMarkers = [];
    let dedicatedPolyline = null;

    function initDedicatedMap() {{
      if (dedicatedMap) return;

      dedicatedMap = L.map('m-dedicated-map', {{
        zoomControl: false,
        attributionControl: false
      }}).setView([45.5, 87.5], 6);

      transitLayer = L.tileLayer('https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={{x}}&y={{y}}&z={{z}}', {{
        subdomains: ['1', '2', '3', '4'],
        minZoom: 4,
        maxZoom: 18
      }}).addTo(dedicatedMap);

      standardLayer = L.tileLayer('https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={{x}}&y={{y}}&z={{z}}', {{
        subdomains: ['1', '2', '3', '4'],
        minZoom: 4,
        maxZoom: 18
      }});

      mTripData.days.forEach(d => {{
        const lat = d.to.lat;
        const lng = d.to.lng;

        const iconHtml = `<div style="background:#96382d; color:#fff; width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:12px; border:2px solid #fff; box-shadow:0 3px 8px rgba(0,0,0,0.6); cursor:pointer;">${{d.day}}</div>`;
        const cIcon = L.divIcon({{ className: 'custom-d-marker', html: iconHtml, iconSize: [26, 26], iconAnchor: [13, 13] }});

        const mk = L.marker([lat, lng], {{ icon: cIcon }}).addTo(dedicatedMap);
        mk.on('click', () => {{
          focusDedicatedDay(d.day, document.querySelectorAll('.m-map-day-pill')[d.day]);
        }});
        dedicatedMarkers.push({{ day: d.day, mk, lat, lng, data: d }});
      }});

      dedicatedPolyline = L.polyline(mLatLngs, {{
        color: '#f87171',
        weight: 3.5,
        opacity: 0.9,
        dashArray: '5, 5'
      }}).addTo(dedicatedMap);

      if (window.L && L.polylineDecorator) {{
        try {{
          L.polylineDecorator(dedicatedPolyline, {{
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
          }}).addTo(dedicatedMap);
        }} catch(e) {{
          console.warn("Decorator error", e);
        }}
      }}

      if (mLatLngs.length > 0) {{
        dedicatedMap.fitBounds(dedicatedPolyline.getBounds(), {{ padding: [30, 30] }});
      }}
    }}

    function toggleMapLayer() {{
      if (!dedicatedMap) return;
      isStandardMode = !isStandardMode;
      const btn = document.querySelector('.m-layer-toggle-btn');
      if (isStandardMode) {{
        dedicatedMap.removeLayer(transitLayer);
        dedicatedMap.addLayer(standardLayer);
        btn.innerText = "🚌 切换公共交通";
      }} else {{
        dedicatedMap.removeLayer(standardLayer);
        dedicatedMap.addLayer(transitLayer);
        btn.innerText = "🗺️ 切换标准路网";
      }}
    }}

    function focusDedicatedDay(dayNum, btn) {{
      document.querySelectorAll('.m-map-day-pill').forEach(p => p.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const infoTitle = document.getElementById('m-info-title');
      const infoBadge = document.getElementById('m-info-badge');
      const infoDist = document.getElementById('m-info-dist');
      const infoTime = document.getElementById('m-info-time');
      const infoElev = document.getElementById('m-info-elev');
      const infoTolls = document.getElementById('m-info-tolls');
      const infoBtnDine = document.getElementById('m-info-btn-dine');
      const infoBtnNav = document.getElementById('m-info-btn-nav');

      if (dayNum === 0) {{
        dedicatedMap.flyToBounds(dedicatedPolyline.getBounds(), {{ padding: [30, 30], duration: 0.8 }});
        infoTitle.innerText = "新疆14天自驾全景路线";
        infoBadge.innerText = "总览 2380km";
        infoDist.innerText = "2380 km";
        infoTime.innerText = "37.5 h";
        infoElev.innerText = "30~1374m";
        infoTolls.innerText = "¥820";
        infoBtnDine.onclick = () => {{ jumpToDining(1); }};
        infoBtnNav.href = "https://uri.amap.com/navigation?to=87.616848,43.825592&mode=car";
      }} else {{
        const dayItem = mTripData.days.find(d => d.day === dayNum);
        if (dayItem) {{
          dedicatedMap.flyTo([dayItem.to.lat, dayItem.to.lng], 9, {{ duration: 0.8 }});
          infoTitle.innerText = `Day ${{dayItem.day}}: ${{dayItem.title.split('·')[0]}}`;
          infoBadge.innerText = `${{dayItem.date}} · ${{dayItem.weekday}}`;
          infoDist.innerText = `${{dayItem.distance_km}} km`;
          infoTime.innerText = `${{dayItem.duration}}`;
          infoElev.innerText = `${{dayItem.elevation_m}} m`;
          infoTolls.innerText = `¥${{dayItem.tolls_rmb}}`;
          infoBtnDine.onclick = () => {{ jumpToDining(dayItem.day); }};
          infoBtnNav.href = `https://uri.amap.com/navigation?from=${{dayItem.from.lng}},${{dayItem.from.lat}}&to=${{dayItem.to.lng}},${{dayItem.to.lat}}&mode=car`;
        }}
      }}
    }}

    // ==========================================
    // 6. 通用 Tab 切换引擎
    // ==========================================
    function mSwitch(viewId, el) {{
      if (el) {{
        document.querySelectorAll('.m-dock-item').forEach(i => i.classList.remove('active'));
        el.classList.add('active');
      }}

      const mapZone = document.getElementById('m-map-zone');
      const contentContainer = document.getElementById('m-content-container');
      const dedicatedMapView = document.getElementById('m-view-map');

      if (viewId === 'map') {{
        mapZone.classList.add('mode-hidden');
        contentContainer.style.display = 'none';
        dedicatedMapView.style.display = 'block';
        initDedicatedMap();
        setTimeout(() => {{ dedicatedMap.invalidateSize(); }}, 200);
        return;
      }} else {{
        dedicatedMapView.style.display = 'none';
        contentContainer.style.display = 'block';
      }}

      if (viewId === 'tips') {{
        mapZone.classList.add('mode-hidden');
      }} else {{
        mapZone.classList.remove('mode-hidden');
      }}

      document.getElementById('m-view-timeline').style.display = (viewId === 'timeline') ? 'block' : 'none';
      document.getElementById('m-view-dining').style.display = (viewId === 'dining') ? 'block' : 'none';
      document.getElementById('m-view-birding').style.display = (viewId === 'birding') ? 'block' : 'none';
      document.getElementById('m-view-culture').style.display = (viewId === 'culture') ? 'block' : 'none';
      document.getElementById('m-view-tips').style.display = (viewId === 'tips') ? 'block' : 'none';

      setTimeout(() => {{ mMap.invalidateSize(); }}, 200);

      if (viewId === 'timeline') {{
        document.getElementById('m-top-map-hint').innerText = "🗺️ 行程路线 · 点下方卡片联动";
        setupRouteWithArrows();
        mMap.fitBounds(mPolyline.getBounds(), {{ padding: [15, 15] }});
      }} else if (viewId === 'dining') {{
        showDiningDayOnMap(1, 'lunch', 0);
      }} else if (viewId === 'birding') {{
        showBirdingDayOnMap(1);
      }} else if (viewId === 'culture') {{
        showHeritageDayOnMap(1);
      }} else if (viewId === 'tips') {{
        renderMChart();
      }}
    }}

    function jumpToDining(dayNum) {{
      const diningDock = document.querySelectorAll('.m-dock-item')[2];
      mSwitch('dining', diningDock);
      showDiningDayOnMap(dayNum, 'lunch', 0);
      setTimeout(() => {{
        const targetDine = document.getElementById('dine-day-' + dayNum);
        if (targetDine) targetDine.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function jumpToBirding(dayNum) {{
      const birdingDock = document.querySelectorAll('.m-dock-item')[3];
      mSwitch('birding', birdingDock);
      showBirdingDayOnMap(dayNum);
      setTimeout(() => {{
        const targetBird = document.getElementById('bird-day-' + dayNum);
        if (targetBird) targetBird.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    function jumpToHeritage(dayNum) {{
      const cultureDock = document.querySelectorAll('.m-dock-item')[4];
      mSwitch('culture', cultureDock);
      showHeritageDayOnMap(dayNum);
      setTimeout(() => {{
        const targetHerit = document.getElementById('herit-day-' + dayNum + '-1') || document.querySelector('[id^="herit-day-' + dayNum + '"]');
        if (targetHerit) targetHerit.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }}, 100);
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      mTripData.birding_guide.forEach(b => {{
        const card = document.getElementById('bird-day-' + b.day);
        if (card) {{
          card.addEventListener('click', () => {{ showBirdingDayOnMap(b.day); }});
        }}
      }});

      mTripData.heritage_guide.forEach(h => {{
        const card = document.getElementById('herit-day-' + h.day + '-' + (h.order_in_day || 1));
        if (card) {{
          card.addEventListener('click', () => {{ showHeritageDayOnMap(h.day); }});
        }}
      }});
    }});

    let mChartInstance = null;
    function renderMChart() {{
      if (mChartInstance) return;
      const ctx = document.getElementById('mChart').getContext('2d');
      const labels = mTripData.days.map(d => `D${{d.day}}`);
      const elevations = mTripData.days.map(d => d.elevation_m);

      mChartInstance = new Chart(ctx, {{
        type: 'line',
        data: {{
          labels: labels,
          datasets: [{{
            label: '海拔高度 (米)',
            data: elevations,
            borderColor: '#f87171',
            backgroundColor: 'rgba(248, 113, 113, 0.18)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: '#96382d',
            pointRadius: 4
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          scales: {{
            y: {{
              beginAtZero: true,
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
            }},
            x: {{
              grid: {{ color: '#1e293b' }},
              ticks: {{ color: '#94a3b8', font: {{ size: 10 }} }}
            }}
          }},
          plugins: {{
            legend: {{ display: false }}
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
    out_path = os.path.join(project_root, "trip_mobile.html")
    content = build_mobile_split_screen_html()
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"🎉 包含国保实景照片标牌的手机版路书已生成: {out_path}")


if __name__ == "__main__":
    main()
