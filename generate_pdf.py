#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_pdf.py — 生成升级版《新疆自然风光与国保人文十四天自驾路书（优化定稿版）》PDF
"""

import os
import subprocess

HTML_CONTENT = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>新疆自然风光与国保人文十四天自驾路书（优化定稿版）</title>
  <style>
    @page {
      size: A4 portrait;
      margin: 14mm 12mm 14mm 12mm;
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
    body {
      background: #fff;
      color: #222;
      font-size: 11.5px;
      line-height: 1.45;
    }

    /* Page container */
    .page {
      width: 100%;
      page-break-after: always;
      position: relative;
    }
    .page:last-child {
      page-break-after: avoid;
    }

    /* Header Banner */
    .header-banner {
      background: linear-gradient(135deg, #8a2e22 0%, #9c3b2f 100%);
      color: #fff;
      padding: 16px 20px;
      border-radius: 6px;
      margin-bottom: 12px;
      box-shadow: 0 2px 6px rgba(138, 46, 34, 0.2);
    }
    .header-banner h1 {
      font-size: 20px;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
      color: #ffffff;
    }
    .header-banner .subtitle {
      font-size: 11px;
      color: #fbd9d5;
      font-weight: 400;
    }

    /* Highlights Section */
    .highlights-box {
      background: #faf8f5;
      border: 1px solid #e8e2d8;
      border-radius: 6px;
      padding: 10px 14px;
      margin-bottom: 12px;
      font-size: 10.5px;
      color: #444;
    }
    .highlights-title {
      font-weight: 700;
      color: #8a2e22;
      font-size: 11px;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 4px;
    }
    .highlights-box ul {
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .highlights-box li {
      position: relative;
      padding-left: 12px;
      line-height: 1.4;
    }
    .highlights-box li::before {
      content: "•";
      position: absolute;
      left: 0;
      color: #8a2e22;
      font-weight: bold;
    }
    .highlights-box b {
      color: #1f2937;
    }

    /* Section Title */
    .section-title {
      font-size: 12.5px;
      font-weight: 700;
      color: #1f2937;
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .section-bar {
      width: 4px;
      height: 14px;
      background: #8a2e22;
      border-radius: 2px;
      display: inline-block;
    }

    /* Table Styling */
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 10px;
      margin-bottom: 6px;
    }
    th {
      background: #475569;
      color: #fff;
      font-weight: 600;
      text-align: left;
      padding: 6px 8px;
      border: 1px solid #334155;
    }
    td {
      padding: 6px 8px;
      border: 1px solid #e2e8f0;
      vertical-align: middle;
      line-height: 1.38;
    }
    tr:nth-child(even) {
      background: #f8fafc;
    }

    .col-date { width: 9%; font-weight: 700; text-align: center; color: #334155; }
    .col-route { width: 17%; font-weight: 600; color: #1e293b; }
    .col-content { width: 56%; }
    .col-distance { width: 9%; text-align: center; color: #475569; font-weight: 500; }
    .col-time { width: 9%; text-align: center; color: #475569; font-weight: 500; }

    /* Tag Chips */
    .tag {
      display: inline-block;
      font-size: 9px;
      font-weight: 600;
      padding: 1px 4px;
      border-radius: 3px;
      margin-right: 4px;
      margin-bottom: 2px;
      vertical-align: middle;
    }
    .tag-red { background: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .tag-green { background: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .tag-blue { background: #e0f2fe; color: #075985; border: 1px solid #bae6fd; }
    .tag-orange { background: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }
    .tag-yellow { background: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
    .tag-purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }

    .opt-highlight {
      color: #991b1b;
      font-weight: 600;
    }

    /* Footer / Page Number */
    .page-footer {
      position: absolute;
      bottom: 0;
      right: 0;
      font-size: 9.5px;
      color: #94a3b8;
    }
  </style>
</head>
<body>

  <!-- ==================== PAGE 1 ==================== -->
  <div class="page">
    
    <div class="header-banner">
      <h1>新疆自然风光与国保人文十四天自驾路书</h1>
      <div class="subtitle">规划周期：2026年10月25日 - 11月7日 ｜ 车型设定：大众8代高尔夫 (1.4T/两厢) ｜ <b>全案已融入极寒冰雪、时间窗与安全优化</b></div>
    </div>

    <div class="highlights-box">
      <div class="highlights-title">🧭 路线定稿亮点与安全保障机制 (喀纳斯冰雪防滑 + 吐鲁番国保集群超深度研学)：</div>
      <ul>
        <li><b>阿勒泰轻装快走 & 极寒保障</b>：喀纳斯保留最精华湖区与三湾，避免严冬过度滞留；布尔津落实前驱雪地胎与防滑链整备，跟车防滑防托底。</li>
        <li><b>可可托海与北庭故城时间窗把控</b>：Day 8 提前直奔额尔齐斯大峡谷避免日落极寒；Day 9 抢先于 14:30 抵达北庭故城应对冬季提前闭馆。</li>
        <li><b>吐鲁番国保全覆盖深度研学</b>：拆分为石窟寺院、古城防御（交河减土法 vs 高昌夯土）、地下水利、古墓丧葬四大专题，从容考究生土与力学结构。</li>
        <li><b>原产地直发与无缝直达</b>：在吐鲁番原产地干果大采购并顺丰包邮；第14天达坂城风区预留缓冲，走G30直达地窝堡机场（不进市区），从容搭乘 16:45 航班。</li>
      </ul>
    </div>

    <div class="section-title">
      <span class="section-bar"></span> 自驾全景每日详单 (14天优化定稿版 · 上篇)
    </div>

    <table>
      <thead>
        <tr>
          <th class="col-date">日期</th>
          <th class="col-route">路线 (起讫点)</th>
          <th class="col-content">沿途景点、国保单位与生态考察重点 (含优化执行要点)</th>
          <th class="col-distance">路程</th>
          <th class="col-time">预计用时</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="col-date"><b>Day 1</b><br><span style="color:#64748b;">10/25</span></td>
          <td class="col-route">乌鲁木齐机场<br>➔ 市区</td>
          <td class="col-content">
            <span class="tag tag-red">国保单位</span> <b>乌鲁木齐文庙</b>。市区大型超市采购物资与干粮，<span class="opt-highlight">提车时重点落实 -35# 极寒防冻玻璃水与车辆保温装备</span>。
          </td>
          <td class="col-distance">30 km</td>
          <td class="col-time">2.5 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 2</b><br><span style="color:#64748b;">10/26</span></td>
          <td class="col-route">乌鲁木齐<br>➔ S21高速 ➔ 福海</td>
          <td class="col-content">
            <span class="tag tag-green">观鸟圣地</span> <b>青格达湖湿地观鸟</b>。<br>
            <span class="tag tag-orange">沙漠生态</span> <b>S21沙漠高速</b>穿越古尔班通古特沙漠。<br>
            <span class="tag tag-green">黄金观鸟</span> <b>乌伦古湖</b>傍晚观赏冰水交界大天鹅集结。
          </td>
          <td class="col-distance">400 km</td>
          <td class="col-time">6.0 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 3</b><br><span style="color:#64748b;">10/27</span></td>
          <td class="col-route">福海<br>➔ 布尔津</td>
          <td class="col-content">
            <span class="tag tag-green">黄金观鸟</span> <b>科克苏湿地</b>深入戈壁沼泽生态。<br>
            <span class="tag tag-yellow">⚠️ 极寒整备</span> 下午在布尔津<span class="opt-highlight">全面安装前驱深度花纹雪地胎，试装金属防滑链，配备折叠雪铲、搭电宝与拖车绳</span>。
          </td>
          <td class="col-distance">250 km</td>
          <td class="col-time">6.5 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 4</b><br><span style="color:#64748b;">10/28</span></td>
          <td class="col-route">布尔津<br>➔ 禾木</td>
          <td class="col-content">
            驶入阿尔泰山脉 S232/X852 冰雪盘山公路。<span class="opt-highlight">【极寒驾驶】全程低速挡慢行，紧跟前车轮辙防托底</span>。下午抵达禾木景区（核验雪胎自驾报备），拍摄图瓦人木屋与初冬雪景。
          </td>
          <td class="col-distance">170 km</td>
          <td class="col-time">7.0 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 5</b><br><span style="color:#64748b;">10/29</span></td>
          <td class="col-route">禾木村内停留</td>
          <td class="col-content">
            <span class="tag tag-blue">冬季限定</span> <b>禾木观景台与白桦林</b>：清晨穿戴极地防寒装备（-15°C）徒步哈登平台观晨雾日出，全天雪景摄影与村落生土木结构考究。
          </td>
          <td class="col-distance">0 km</td>
          <td class="col-time">全天</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 6</b><br><span style="color:#64748b;">10/30</span></td>
          <td class="col-route">禾木<br>➔ 喀纳斯</td>
          <td class="col-content">
            经铁热克提出山转入喀纳斯，下午抵达喀纳斯老村入住，沿木栈道考察积雪覆盖的西伯利亚泰加林与河道冰雪奇观“雪蘑菇”。
          </td>
          <td class="col-distance">100 km</td>
          <td class="col-time">4.5 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 7</b><br><span style="color:#64748b;">10/31</span></td>
          <td class="col-route">喀纳斯<br>➔ 布尔津</td>
          <td class="col-content">
            <span class="tag tag-blue">自然奇观</span> 清晨守候<b>神仙湾、月亮湾</b>绝美水汽晨雾。中午平稳驾驶下山返回布尔津。傍晚游览<b>五彩滩</b>夕阳雅丹地貌，夜市品尝额河烤冷水鱼。
          </td>
          <td class="col-distance">150 km</td>
          <td class="col-time">6.0 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 8</b><br><span style="color:#64748b;">11/1</span></td>
          <td class="col-route">布尔津<br>➔ 富蕴 (可可托海)</td>
          <td class="col-content">
            <span class="tag tag-blue">地质奇观</span> <span class="tag tag-yellow">⚠️ 动线优化</span> <span class="opt-highlight">早 08:30 布尔津出发直奔可可托海</span>，13:30-16:30 探访<b>冰封河谷与神钟山花岗岩绝壁</b>（避开17点后骤降至-10°C严寒），傍晚返回富蕴县城住宿。
          </td>
          <td class="col-distance">350 km</td>
          <td class="col-time">8.0 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 9</b><br><span style="color:#64748b;">11/2</span></td>
          <td class="col-route">富蕴<br>➔ 吉木萨尔 ➔ 奇台</td>
          <td class="col-content">
            <span class="tag tag-green">生态保护</span> <b>卡拉麦里保护区</b>沿 G216 国道搜寻普氏野马。<br>
            <span class="tag tag-red">国保前置</span> <span class="tag tag-yellow">⚠️ 闭馆把控</span> <span class="opt-highlight">08:30 出发确保 14:30 前抵达【北庭故城遗址】</span>，避开冬季提前闭馆，留足 2.5 小时深度研学高昌回鹘大寺与生土防御体系。下榻奇台。
          </td>
          <td class="col-distance">390 km</td>
          <td class="col-time">8.0 h</td>
        </tr>
      </tbody>
    </table>

    <div class="page-footer">第 1 页</div>
  </div>

  <!-- ==================== PAGE 2 ==================== -->
  <div class="page">

    <div class="section-title" style="margin-top: 4px;">
      <span class="section-bar"></span> 自驾全景每日详单 (14天优化定稿版 · 下篇)
    </div>

    <table>
      <thead>
        <tr>
          <th class="col-date">日期</th>
          <th class="col-route">路线 (起讫点)</th>
          <th class="col-content">沿途景点、国保单位与生态考察重点 (含优化执行要点)</th>
          <th class="col-distance">路程</th>
          <th class="col-time">预计用时</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="col-date"><b>Day 10</b><br><span style="color:#64748b;">11/3</span></td>
          <td class="col-route">奇台<br>➔ 吐鲁番</td>
          <td class="col-content">
            <span class="tag tag-orange">人文替补</span> 上午参观<b>奇台县博物馆</b>。<br>
            <span class="tag tag-yellow">⚠️ 选路优化</span> <span class="opt-highlight">走 G335 + G30 高等级干线平缓翻越天山</span>进入火洲吐鲁番（避开暗冰险弯省道），入住智选假日酒店，老城品尝地道烤肉。
          </td>
          <td class="col-distance">290 km</td>
          <td class="col-time">5.5 h</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 11</b><br><span style="color:#64748b;">11/4</span></td>
          <td class="col-route">吐鲁番<br>(东郊石窟线)</td>
          <td class="col-content">
            <span class="tag tag-red">国保深度</span> 上午<b>柏孜克里克千佛洞</b>高昌回鹘石窟剖析。<br>
            下午深入<b>吐峪沟石窟与麻扎村</b>生土民居建筑实测与穹顶券顶考究。晚尝托克逊拌面。
          </td>
          <td class="col-distance">90 km</td>
          <td class="col-time">全天</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 12</b><br><span style="color:#64748b;">11/5</span></td>
          <td class="col-route">吐鲁番<br>(名城与古墓线)</td>
          <td class="col-content">
            <span class="tag tag-red">国保深度</span> 全天聚焦<b>高昌故城</b>（大佛寺与生土夯筑外城）、<b>阿斯塔那古墓群</b>（地下墓室规制与壁画）。<br>
            <span class="opt-highlight">傍晚 17:30 黄金斜阳光线直奔【交河故城】实测“减土法”生土废墟金色夕阳</span>。
          </td>
          <td class="col-distance">80 km</td>
          <td class="col-time">全天</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 13</b><br><span style="color:#64748b;">11/6</span></td>
          <td class="col-route">吐鲁番<br>(水利与清代工法)</td>
          <td class="col-content">
            <span class="tag tag-orange">水利与砖构</span> 上午<b>坎儿井地下暗渠</b>水力工法剖析，<span class="opt-highlight">顺光实测【苏公塔】44米清代砌砖穹顶与72种几何拼砖力学细部</span>。<br>
            下午<b>吐鲁番博物馆</b>沉浸式观展，原产地干果批发市场大采购并顺丰包邮。
          </td>
          <td class="col-distance">40 km</td>
          <td class="col-time">全天</td>
        </tr>
        <tr>
          <td class="col-date"><b>Day 14</b><br><span style="color:#64748b;">11/7</span></td>
          <td class="col-route">吐鲁番<br>➔ 达坂城 ➔ 乌市机场</td>
          <td class="col-content">
            <span class="tag tag-yellow">⚠️ 返程倒推与风区缓冲</span> <span class="opt-highlight">早 09:30 退房出发</span>，途经<b>达坂城风区与柴窝堡湖</b>（预留横风减速缓冲），12:30 柴窝堡午餐，<span class="opt-highlight">13:45 走 G30 直达地窝堡机场还车</span>（不进市区），从容搭乘 <b>16:45 航班圆满收官</b>。
          </td>
          <td class="col-distance">200 km</td>
          <td class="col-time">3.0 h</td>
        </tr>
      </tbody>
    </table>

    <!-- 底部重点注意事项总结卡片 -->
    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:10px 14px; margin-top:14px; font-size:10px; color:#334155;">
      <div style="font-weight:700; color:#8a2e22; margin-bottom:4px; font-size:10.5px;">📋 关键行前自检与物资清单：</div>
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; line-height:1.4;">
        <div>
          <b>❄️ 车辆与轮胎：</b><br>
          • 乌鲁木齐提车必须锁定前驱雪地胎 + 金属防滑链。<br>
          • 随车配备：折叠雪铲、搭电线/搭电宝、防冻玻璃水(-35#)。
        </div>
        <div>
          <b>🏛️ 门票与证件：</b><br>
          • 喀纳斯/禾木：淡季提前关注「喀纳斯零距离」自驾报备。<br>
          • 新疆博物馆/北庭故城：提前在微信小程序实名预约。
        </div>
      </div>
    </div>

    <div class="page-footer">第 2 页</div>
  </div>

</body>
</html>
"""

def generate_pdf():
    project_root = "/Users/Noodles/Documents/AG_Project"
    html_path = os.path.join(project_root, "itinerary_pdf_template.html")
    pdf_path = os.path.join(project_root, "新疆自然风光与国保人文十四天自驾路书_优化定稿版.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(HTML_CONTENT)

    print(f"📄 HTML 模板已准备: {html_path}")

    # 使用 macOS 上的 Google Chrome 进行 Headless PDF 渲染
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]

    print("🖨️ 正在通过 Chrome Headless 引擎编译高清双页 PDF...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024.0
        print(f"🎉 PDF 渲染成功！")
        print(f"📁 文件保存路径: {pdf_path} ({size_kb:.1f} KB)")
        return pdf_path
    else:
        print(f"❌ 渲染失败: {res.stderr}")
        return None

if __name__ == "__main__":
    generate_pdf()
