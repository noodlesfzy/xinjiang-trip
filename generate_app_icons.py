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

# 1. 生成 iOS 各尺寸图标
ios_sizes = [
    (1024, "icon_1024x1024.png"),
    (180, "icon_60x60@3x.png"),
    (120, "icon_60x60@2x.png"),
    (167, "icon_83.5x83.5@2x.png"),
    (152, "icon_76x76@2x.png"),
    (87, "icon_29x29@3x.png"),
    (80, "icon_40x40@2x.png"),
    (60, "icon_20x20@3x.png"),
    (58, "icon_29x29@2x.png"),
    (40, "icon_20x20@2x.png"),
]

for size, filename in ios_sizes:
    resized = master_img.resize((size, size), Image.Resampling.LANCZOS)
    out_path = os.path.join(IOS_APPICON_DIR, filename)
    resized.save(out_path, "PNG")

# 2. 生成 Xcode AppIcon Contents.json (同时兼容现代 1024 统一格式与传统尺寸)
contents_json = {
    "images": [
        {
            "filename": "icon_1024x1024.png",
            "idiom": "universal",
            "platform": "ios",
            "size": "1024x1024"
        },
        {
            "filename": "icon_60x60@2x.png",
            "idiom": "iphone",
            "scale": "2x",
            "size": "60x60"
        },
        {
            "filename": "icon_60x60@3x.png",
            "idiom": "iphone",
            "scale": "3x",
            "size": "60x60"
        },
        {
            "filename": "icon_76x76@2x.png",
            "idiom": "ipad",
            "scale": "2x",
            "size": "76x76"
        },
        {
            "filename": "icon_83.5x83.5@2x.png",
            "idiom": "ipad",
            "scale": "2x",
            "size": "83.5x83.5"
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
