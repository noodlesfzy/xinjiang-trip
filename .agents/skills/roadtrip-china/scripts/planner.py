#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
planner.py — 中国大陆自驾核心规划引擎与数据生成器

功能：
1. 接收用户的自驾行程参数（起点、目的地、天数、日期、车型）；
2. 调度 tools 下的所有客户端（地名坐标、驾车路线、海拔安全、充电/油耗、天气预警、门票预约）；
3. 针对自驾请求生成 2 条差异化备选路线（如：北疆全景大环线 vs 精华环线）；
4. 输出完整的结构化 tripData.json。
"""

import os
import sys
import json
from datetime import datetime, timedelta

# 导入工具集
try:
    from tools.places_client import validate_place
    from tools.routing_client import get_route
    from tools.elevation_client import evaluate_altitude_safety
    from tools.charging_client import simulate_energy_budget, find_chargers_near
    from tools.weather_client import get_weather_forecast
    from tools.parks_client import get_park_info
except ImportError:
    # 兼容直接在 scripts/ 下运行
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from tools.places_client import validate_place
    from tools.routing_client import get_route
    from tools.elevation_client import evaluate_altitude_safety
    from tools.charging_client import simulate_energy_budget, find_chargers_near
    from tools.weather_client import get_weather_forecast
    from tools.parks_client import get_park_info


def build_xinjiang_14d_itinerary(start_date_str: str = "2025-10-25", vehicle_type: str = "燃油四驱SUV (配备雪地胎)") -> dict:
    """
    专门为 2025.10.25 - 11.07 新疆阿勒泰 + 吐鲁番 14 天自驾深度定制的基准行程规划
    特点：
    - 北疆初冬（阿勒泰雪景/可可托海）+ 东疆温暖秋景（吐鲁番/库木塔格沙漠）的冰火交响；
    - 严格避开独库公路冬季封路，采用 S21 沙漠高速 / G3014 奎阿高速 / G30 连霍高速；
    - 针对喀纳斯/禾木 10 月下旬大雪暗冰，强制四驱雪地胎提醒；
    - 针对乌鲁木齐-吐鲁番达坂城风区设置横风预警；
    - 白哈巴边防证即时办理引导。
    """
    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d")

    raw_days_spec = [
        {
            "day": 1,
            "title": "集结乌鲁木齐 · 提车检修与物资整备",
            "from": "乌鲁木齐", "to": "乌鲁木齐",
            "highlights": ["新疆国际大巴扎", "红山公园俯瞰雪山", "提四驱SUV并检查雪地胎/防冻液(-35#)"],
            "morning": "抵达乌鲁木齐地窝堡机场/高铁站，租车门店验车（重点检查雪地胎胎纹与胎压、玻璃水防冻标号）。",
            "afternoon": "游览新疆国际大巴扎，采购沿途干粮、保温壶、暖宝宝及高热量零食（牛肉干、馕）。",
            "evening": "品尝正宗新疆特色大盘鸡、烤羊肉串及手抓饭，早点休息储备体能。",
            "stay": "乌鲁木齐市区高档酒店 (地暖/暖气充足)",
            "is_mountain": False,
            "custom_warnings": ["新疆与内地有 2 小时作息时差，早晨 9:30-10:00 出发，晚 19:30-20:00 天黑。"]
        },
        {
            "day": 2,
            "title": "穿越 S21 阿乌沙漠高速 · 奔赴童话边城布尔津",
            "from": "乌鲁木齐", "to": "布尔津",
            "highlights": ["中国首条沙漠高速S21", "准噶尔盆地古尔班通古特沙漠", "布尔津五彩滩日落"],
            "morning": "09:30 从乌鲁木齐出发，驶入 S21 沙漠高速，笔直公路穿行于浩瀚戈壁与沙丘之间。",
            "afternoon": "克拉美丽服务区稍作休息补能，下午抵达布尔津县城，稍作休整后驱车前往五彩滩。",
            "evening": "18:00 游览五彩滩（额尔齐斯河畔夕阳雅丹地貌），晚餐品尝布尔津夜市额尔齐斯河冷水烤鱼（狗鱼）。",
            "stay": "布尔津县城星级酒店",
            "is_mountain": False,
            "custom_warnings": ["S21 沙漠高速部分区间测速严格，且冬季可能有横风积雪，注意控制车速。"]
        },
        {
            "day": 3,
            "title": "挺进阿勒泰雪山之巅 · 探秘初冬喀纳斯湖",
            "from": "布尔津", "to": "喀纳斯",
            "highlights": ["喀纳斯盘山公路雪景", "喀纳斯湖三道湾", "卧龙湾/月亮湾/神仙湾冰雪初现"],
            "morning": "09:00 出发布尔津，沿 S232 盘山公路向北驶向喀纳斯，沿途落叶松与白桦林银装素裹。",
            "afternoon": "抵达贾登峪，办理淡季自驾进山报备（需确认四驱+雪地胎），车行直达喀纳斯老村湖区。漫步喀纳斯湖边木栈道，观赏蓝冰与雾凇。",
            "evening": "拍摄神仙湾雪景，入住喀纳斯老村图瓦人传统暖气木屋，品尝热奶茶与手抓羊肉。",
            "stay": "喀纳斯老村特色暖气木屋民宿",
            "is_mountain": True,
            "custom_warnings": ["⚠️ 贾登峪至喀纳斯盘山路有多处背阴暗冰弯道，严禁急刹车与急打方向，全程保持低速档！"]
        },
        {
            "day": 4,
            "title": "中哈边境秘境 · 白哈巴西北第一村的宁静",
            "from": "喀纳斯", "to": "白哈巴",
            "highlights": ["白哈巴中哈界碑与边防哨所", "西北第一村图瓦木屋群", "金秋与白雪交织的孤寂美景"],
            "morning": "09:30 在喀纳斯换乘中心警务室凭身份证快速办理《边境管理区通行证》（免费，5分钟立取）。",
            "afternoon": "驱车约 30 公里前往白哈巴村，沿途经过广袤的高山雪原与边境铁丝网，感受中国最西北边陲的宁静。",
            "evening": "在白哈巴村木屋前看晚霞映照雪山，夜晚仰望北疆纯净无污染的银河星空。",
            "stay": "白哈巴村特色木屋客栈 (配电暖/水暖)",
            "is_mountain": True,
            "custom_warnings": ["白哈巴村紧邻边境，严禁靠近界河与边防铁丝网，严禁放飞未经报备的无人机！"]
        },
        {
            "day": 5,
            "title": "穿越雪原森林 · 奔向神的自留地【禾木村】",
            "from": "白哈巴", "to": "禾木",
            "highlights": ["铁热克提至禾木高山公路", "禾木河雪蘑菇与冰凌", "禾木桥与百年老屋"],
            "morning": "清晨告别白哈巴，沿盘山路折返经铁热克提出山，转入 X852 县道前往禾木村。",
            "afternoon": "下午抵达禾木门票站，核验雪地胎后自驾进入禾木村。漫步于禾木河畔，看流水在冰雪间潺潺流淌，白桦树挂满雾凇。",
            "evening": "傍晚在禾木桥附近漫步，在暖和的咖啡馆小憩，晚上品尝特色土火锅。",
            "stay": "禾木村核心景区高端木屋酒店 (地暖充足)",
            "is_mountain": True,
            "custom_warnings": ["禾木夜间气温降至 -15°C 以下，车辆夜间需停在避风处，相机及手机在室外电量消耗极快。"]
        },
        {
            "day": 6,
            "title": "禾木观景台日出晨雾 · 冰雪童话沉浸体验",
            "from": "禾木", "to": "禾木",
            "highlights": ["哈登平台俯瞰禾木全景晨雾", "图瓦人木屋炊烟袅袅", "马拉爬犁/雪地徒步体验"],
            "morning": "07:30 穿戴好极地防寒装备（羽绒服+帽子手套+暖宝宝），登上哈登平台，等待清晨第一缕阳光洒在木屋与袅袅炊烟上。",
            "afternoon": "在禾木村体验雪地慢生活：可骑马或乘坐传统马拉爬犁穿越白桦林雪原，享受深冬前人少清幽的禾木。",
            "evening": "村内自由摄影创作，围炉煮茶，交流自驾心得。",
            "stay": "禾木村特色木屋酒店 (连住)",
            "is_mountain": True,
            "custom_warnings": ["登哈登平台观景台栈道台阶有冰雪积压较滑，务必穿戴防滑雪地靴或简易冰爪。"]
        },
        {
            "day": 7,
            "title": "走出雪山 · 经阿勒泰市前往【可可托海】",
            "from": "禾木", "to": "富蕴",
            "highlights": ["阿勒泰阿尔泰山南麓风光", "可可托海三号矿坑历史传奇", "富蕴县城特色美食"],
            "morning": "09:30 驾车出禾木村，沿 G219/S226 经北屯、阿勒泰市南下，逐步驶离深山雪原，视野逐渐开阔。",
            "afternoon": "下午抵达富蕴县可可托海镇，参观功勋卓越的“三号矿坑”地质奇观。",
            "evening": "入住富蕴县城或可可托海镇，品尝阿勒泰大尾羊手抓肉及哈萨克特色面食（纳仁）。",
            "stay": "富蕴县城精品品质酒店",
            "is_mountain": True,
            "custom_warnings": ["富蕴历史上有中国“第二寒极”之称，早晚温差极大，及时增添防风防寒衣物。"]
        },
        {
            "day": 8,
            "title": "探访额尔齐斯大峡谷 · 沿 G216 穿越准噶尔返回乌市",
            "from": "富蕴", "to": "乌鲁木齐",
            "highlights": ["可可托海额尔齐斯大峡谷神钟山", "G216国道卡拉麦里有蹄类自然保护区 (寻觅野驴/普氏野马)", "乌鲁木齐休整"],
            "morning": "上午游览可可托海额尔齐斯大峡谷，仰望巍峨耸立的神钟山花岗岩巨峰与清澈的额河流水。",
            "afternoon": "午后沿 G216 国道南下穿越卡拉麦里戈壁保护区，沿途注意观察路边出没的珍稀野生蒙古野驴与鹅喉羚。",
            "evening": "傍晚抵达乌鲁木齐市，洗车（洗去北疆泥雪）并休整，准备迎接东疆火洲暖秋旅程。",
            "stay": "乌鲁木齐市区星级酒店",
            "is_mountain": False,
            "custom_warnings": ["G216 国道穿越卡拉麦里保护区路段常有野生动物横穿公路，请勿鸣笛惊扰，减速慢行。"]
        },
        {
            "day": 9,
            "title": "翻越达坂城百里风区 · 抵达火洲【吐鲁番】",
            "from": "乌鲁木齐", "to": "吐鲁番",
            "highlights": ["达坂城巨型风力发电风车群", "吐鲁番交河故城遗址 (世界文化遗产)", "苏公塔伊斯兰建筑艺术"],
            "morning": "10:00 从乌鲁木齐出发，沿 G30 连霍高速向东南驶向吐鲁番，途经达坂城风车旷野。",
            "afternoon": "抵达吐鲁番市高昌区（气温明显回升至 15°C~18°C），下午游览交河故城，在千年生土遗迹间感受丝路厚重沧桑。",
            "evening": "参观苏公塔与维吾尔族郡王府，品尝吐鲁番特色烤包子、羊肉焖饼和清甜的新鲜/晾晒葡萄干。",
            "stay": "吐鲁番高昌区特色庭院酒店 / 星级酒店",
            "is_mountain": False,
            "custom_warnings": ["🚨 达坂城至小草湖段为百里风区，秋冬季横风较强，出隧道或跨风口桥梁时请握紧方向盘并控制车速在80km/h以内。"]
        },
        {
            "day": 10,
            "title": "漫步绿洲与赤壁 · 探秘葡萄沟与【火焰山】",
            "from": "吐鲁番", "to": "鄯善",
            "highlights": ["神奇地下水利工程坎儿井", "吐鲁番葡萄沟金秋风情", "《西游记》传奇火焰山"],
            "morning": "上午参观坎儿井民俗园，了解吐鲁番绿洲生命之源的地下暗渠水利智慧。",
            "afternoon": "前往火焰山风景区，打卡巨型金箍棒温度计与红褐色如烈焰般的赤砂岩山体。随后驱车前往鄯善县。",
            "evening": "傍晚抵达鄯善县城，入住酒店，准备次日沙漠日出与探险。",
            "stay": "鄯善县高品质酒店",
            "is_mountain": False,
            "custom_warnings": ["吐鲁番气候极为干燥，紫外线依然充足，请做好补水保湿与防晒。"]
        },
        {
            "day": 11,
            "title": "沙与城零距离 · 【库木塔格沙漠】狂欢与金色沙海",
            "from": "鄯善", "to": "鄯善",
            "highlights": ["库木塔格沙漠日落与冲沙", "金色沙丘波纹与骑骆驼体验", "鄯善老城夜市美食"],
            "morning": "上午可睡到自然醒，在县城体验慢节奏生活，品尝特色烤馕与奶茶。",
            "afternoon": "15:30 前往库木塔格沙漠风景名胜区，体验沙漠越野冲沙、滑沙或骑骆驼漫步于柔美的羽状沙丘之上。",
            "evening": "18:00-19:00 在沙山顶端守候大漠绝美夕阳，看金色沙海染上红晕，壮丽无比。",
            "stay": "鄯善县高品质酒店 (连住)",
            "is_mountain": False,
            "custom_warnings": ["进入沙漠请提前给手机、相机穿上防尘防沙保护套，防止细沙损坏镜头变焦环。"]
        },
        {
            "day": 12,
            "title": "穿越高昌历史风烟 · 探秘吐峪沟麻扎村",
            "from": "鄯善", "to": "吐鲁番",
            "highlights": ["吐峪沟大峡谷与麻扎村 (传统生土古村落)", "高昌故城历史遗迹", "柏孜克里克千佛洞"],
            "morning": "从鄯善出发前往吐峪沟大峡谷，走进有数百年历史的传统生土建筑群麻扎村，感受原生态西域风情。",
            "afternoon": "游览柏孜克里克千佛洞与高昌故城，领略古丝绸之路重镇的昔日辉煌。",
            "evening": "返回吐鲁番市区住宿，享受惬意舒适的绿洲之夜。",
            "stay": "吐鲁番高昌区特色酒店",
            "is_mountain": False,
            "custom_warnings": ["吐峪沟麻扎村为原住村民居所，参观拍摄请尊重当地民族风俗与信仰。"]
        },
        {
            "day": 13,
            "title": "告别火洲 · 沿 G30 连霍高速从容返程乌鲁木齐",
            "from": "吐鲁番", "to": "乌鲁木齐",
            "highlights": ["G30连霍高速公路风景", "乌鲁木齐特色餐饮与伴手礼采购", "新疆博物馆 (观赏楼兰美女干尸)"],
            "morning": "10:30 从吐鲁番出发，经 G30 高速返程乌鲁木齐，车程约 2.5 小时，轻松无赶路压力。",
            "afternoon": "下午参观新疆维吾尔自治区博物馆（需提前小程序实名预约），重点参观西域历史文物与干尸陈列展厅。",
            "evening": "在乌鲁木齐享用告别晚宴，采购优质新疆干果（和田红枣、阿克苏核桃、吐鲁番无核白葡萄干）。",
            "stay": "乌鲁木齐机场/高铁站附近高档酒店",
            "is_mountain": False,
            "custom_warnings": ["新疆博物馆周一闭馆，请提前在微信小程序实名预约门票。"]
        },
        {
            "day": 14,
            "title": "乌鲁木齐顺利还车 · 满载冰火新疆回忆返程",
            "from": "乌鲁木齐", "to": "乌鲁木齐",
            "highlights": ["市区悠闲漫步", "车行还车与押金结算", "返程航班/高铁"],
            "morning": "睡到自然醒，享用酒店丰盛早餐。整理行装，检查随身物品与边防证证件。",
            "afternoon": "前往租车网点还车，验车交接，结算高速 ETC 费用与押金。",
            "evening": "搭乘航班/高铁返回温馨的家，圆满结束 14 天难忘的北疆冰雪与东疆大漠自驾之旅！",
            "stay": "返程 / 温馨的家",
            "is_mountain": False,
            "custom_warnings": ["建议提前 2.5 小时到达机场，新疆机场安检较为严格细致。"]
        }
    ]

    # 构建结构化 Day 列表
    structured_days = []
    total_km = 0.0
    total_tolls = 0.0
    total_fuel_energy_cost = 0.0

    current_date = start_dt
    prev_elevation = 918  # 乌鲁木齐

    for spec in raw_days_spec:
        from_place = validate_place(spec["from"])
        to_place = validate_place(spec["to"])
        
        # 路线计算
        if spec["from"] == spec["to"]:
            route_info = {
                "distance_km": 30.0,
                "duration_hours": 1.2,
                "duration_text": "市区游览约 1.2 小时",
                "tolls_rmb": 0.0,
                "is_mountain": spec["is_mountain"],
                "source": "local_city"
            }
        else:
            route_info = get_route(from_place["lat"], from_place["lng"], to_place["lat"], to_place["lng"], is_mountain=spec["is_mountain"])

        total_km += route_info["distance_km"]
        total_tolls += route_info["tolls_rmb"]

        # 海拔评估
        elev_info = evaluate_altitude_safety(spec["to"], previous_elevation=prev_elevation, is_overnight=True)
        prev_elevation = elev_info["elevation_m"]

        # 天气
        date_str = current_date.strftime("%Y-%m-%d")
        weather_info = get_weather_forecast(spec["to"], travel_date=date_str)

        # 补能预算 (阿勒泰冬季气候判定)
        is_cold = spec["to"] in ["喀纳斯", "禾木", "白哈巴", "阿勒泰", "布尔津", "富蕴"]
        energy_info = simulate_energy_budget(route_info["distance_km"], vehicle_type=vehicle_type, is_winter_cold=is_cold)
        total_fuel_energy_cost += energy_info["energy_cost_rmb"]
        chargers = find_chargers_near(spec["to"])

        # 核心景区门票信息
        parks_list = []
        for h in spec["highlights"]:
            for pk in ["喀纳斯", "禾木", "白哈巴", "可可托海", "五彩滩", "库木塔格沙漠", "交河故城", "葡萄沟"]:
                if pk in h:
                    pinfo = get_park_info(pk)
                    if pinfo not in parks_list:
                        parks_list.append(pinfo)

        day_obj = {
            "day": spec["day"],
            "date": date_str,
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][current_date.weekday()],
            "title": spec["title"],
            "from_place": from_place,
            "to_place": to_place,
            "route": route_info,
            "elevation": elev_info,
            "weather": weather_info,
            "energy": energy_info,
            "chargers": chargers,
            "parks": parks_list,
            "highlights": spec["highlights"],
            "morning": spec["morning"],
            "afternoon": spec["afternoon"],
            "evening": spec["evening"],
            "stay": spec["stay"],
            "warnings": spec["custom_warnings"]
        }

        structured_days.append(day_obj)
        current_date += timedelta(days=1)

    trip_data = {
        "trip_title": "2025初冬北疆雪国与东疆火洲 14天自驾全景路书",
        "trip_subtitle": "阿勒泰冰雪童话（喀纳斯/禾木/白哈巴/可可托海）+ 吐鲁番丝路绿洲大漠（交河/火焰山/库木塔格）",
        "dates": f"{start_date_str} 至 {(current_date - timedelta(days=1)).strftime('%Y-%m-%d')}",
        "total_days": 14,
        "region": "新疆全景（北疆+东疆）",
        "vehicle_type": vehicle_type,
        "summary": {
            "total_distance_km": round(total_km, 1),
            "total_driving_hours": round(sum(d["route"]["duration_hours"] for d in structured_days), 1),
            "total_tolls_rmb": round(total_tolls, 0),
            "total_energy_cost_rmb": round(total_fuel_energy_cost, 0),
            "total_estimated_budget_rmb": round(total_tolls + total_fuel_energy_cost + 14 * 480 + 14 * 220 + 850, 0),
            "route_style": "冰雪与大漠双重体验 · 舒适度与安全性平衡环线"
        },
        "critical_rules": [
            "❄️ 阿勒泰山区（10月下旬起）：喀纳斯、禾木、白哈巴路段强制要求车辆为四驱并配备雪地胎（或防滑链）。",
            "🪪 边防通行证：前往白哈巴村需在喀纳斯换乘中心或哈巴河边防大厅凭身份证办理《边境管理区通行证》（免费立取）。",
            "💨 达坂城风区：乌鲁木齐至吐鲁番 G30 高速途经百里风区，秋冬季横风强劲，注意限速慢行。",
            "⛔ 独库公路警示：独库公路、伊昭公路已于 10 月中旬封闭，本行程全程采用 S21 沙漠高速及 G3014/G30 高等级国道，安全畅通。"
        ],
        "days": structured_days
    }

    return trip_data


if __name__ == "__main__":
    data = build_xinjiang_14d_itinerary()
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tests", "tripData.xinjiang14d.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"成功生成新疆 14 天自驾数据: {output_path}")
