# -*- coding: utf-8 -*-
"""
shop_id_map.py — 仅保留 100% 经实测完全一致的大众点评官方商户 shop_id
未逐一核实的店铺严禁盲填默认 ID，而是统一自动回退到带【城市名+精确店名+真实CityID】的精准定向搜索直达，杜绝任何“喀什一把抓跳转到楼兰烧烤”的串店错乱！
"""

# 仅收录 100% 经实际测试页面标题与本店严格完全一致的 Shop ID
VERIFIED_EXACT_SHOP_IDS = {
    "楼兰秘烤": "l9ujsXF2SQrpbyAM",
    "阔希玛克拉烤包子": "j4zOVc2CLsooVXPe",
    "明优利特色拌面抓饭": "G8hc2VV3dvYmW13g",
    "老街冷水鱼烧烤": "H8dnRzzwfy99v71F",
    "老东门过油肉拌面馆": "k1xE8zQupp3cyrlV",
    "柴窝堡22号传承新疆菜·新疆辣子鸡": "l62wLW4QKiFuU6Zz"
}

def get_shop_id(name):
    # 严格精确匹配，绝不模糊猜填！
    return VERIFIED_EXACT_SHOP_IDS.get(name, "")
