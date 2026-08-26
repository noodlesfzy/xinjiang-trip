import os
import json
from PIL import Image

PROJECT_DIR = "/Users/Noodles/Documents/AG_Project"
IOS_APPICON_DIR = os.path.join(PROJECT_DIR, "ios", "XinjiangTrip", "Assets.xcassets", "AppIcon.appiconset")
MAC_BUILD_RES_DIR = os.path.join(PROJECT_DIR, "build", "辣鸡喵.app", "Contents", "Resources")

os.makedirs(IOS_APPICON_DIR, exist_ok=True)
os.makedirs(MAC_BUILD_RES_DIR, exist_ok=True)

master_icon_path = os.path.join(PROJECT_DIR, "app_icon_1024.png")
master_img = Image.open(master_icon_path).convert("RGBA")

# 1. 清理并生成标准 iOS 单图通用 AppIcon (Xcode 官方最佳实践，彻底消除 unassigned children 警告)
for item in os.listdir(IOS_APPICON_DIR):
    item_path = os.path.join(IOS_APPICON_DIR, item)
    if os.path.isfile(item_path):
        os.remove(item_path)

master_img.save(os.path.join(IOS_APPICON_DIR, "icon_1024x1024.png"), "PNG")

contents_json = {
    "images": [
        {
            "filename": "icon_1024x1024.png",
            "idiom": "universal",
            "platform": "ios",
            "size": "1024x1024"
        }
    ],
    "info": {
        "author": "xcode",
        "version": 1
    }
}

with open(os.path.join(IOS_APPICON_DIR, "Contents.json"), "w", encoding="utf-8") as f:
    json.dump(contents_json, f, indent=2)

# 3. 根目录 Assets.xcassets 的 Contents.json
xcassets_root = os.path.join(PROJECT_DIR, "ios", "XinjiangTrip", "Assets.xcassets")
with open(os.path.join(xcassets_root, "Contents.json"), "w", encoding="utf-8") as f:
    json.dump({"info": {"author": "xcode", "version": 1}}, f, indent=2)

# 4. 生成 Web PWA 与 Safari Apple Touch Icons
pwa_sizes = [
    (192, "icon-192.png"),
    (512, "icon-512.png"),
    (180, "apple-touch-icon.png"),
]
for size, filename in pwa_sizes:
    resized = master_img.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(os.path.join(PROJECT_DIR, filename), "PNG")

# 5. 生成 macOS App 图标
master_img.save(os.path.join(MAC_BUILD_RES_DIR, "AppIcon.png"), "PNG")

print("🎉 已成功生成全套 iOS Liquid Glass AppIcon 与 Web PWA 图标！")
