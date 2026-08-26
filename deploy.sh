#!/usr/bin/env bash
set -e

echo "🚀 [1/4] 正在编译最新的手机版与通用版自驾路书..."
python3 generate_mobile_trip_html.py
python3 generate_rich_trip_html.py

echo "💎 [2/4] 正在生成 Liquid Glass 原生 iOS Xcode 工程..."
python3 create_ios_app.py

echo "🔨 [3/4] 正在编译原生独立 App 安装包..."
python3 build_mac_app.py

echo "📱 [4/4] 正在自动调用 Xcode 并启动原生 App..."
open ios/XinjiangTrip.xcodeproj
open "build/新疆自驾路书.app"

echo "🎉 自动部署与编译全部完成！Xcode 已自动打开，原生 App 已在桌面启动！"
