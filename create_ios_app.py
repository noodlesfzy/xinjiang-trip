#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_ios_app.py — 一键构建原生 iOS Xcode 工程 (XinjiangTrip)
将 trip_mobile.html 深度打包为 100% 离线运行、支持大众点评/小红书原生 Scheme 唤起的 iOS 原生 App。
"""

import os
import re
import shutil
import subprocess
import uuid

IOS_DIR = "/Users/Noodles/Documents/AG_Project/ios"
APP_DIR = os.path.join(IOS_DIR, "XinjiangTrip")
PBX_DIR = os.path.join(IOS_DIR, "XinjiangTrip.xcodeproj")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(PBX_DIR, exist_ok=True)

# 1. 复制最新编译的手机版路书到 App Bundle 资源目录
shutil.copy2("/Users/Noodles/Documents/AG_Project/trip_mobile.html", os.path.join(APP_DIR, "index.html"))

# 2. 生成原生 Swift 入口文件
swift_code = '''//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  100% Apple Native MapKit + Liquid Glass Hybrid Architecture
//

import SwiftUI
import WebKit
import MapKit

@main
struct XinjiangTripApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - 自定义地图标记
class TripAnnotation: NSObject, MKAnnotation {
    let coordinate: CLLocationCoordinate2D
    let title: String?
    let subtitle: String?
    let type: String // "day", "dine", "bird", "culture"
    let dayNum: Int
    
    init(coordinate: CLLocationCoordinate2D, title: String?, subtitle: String?, type: String, dayNum: Int) {
        self.coordinate = coordinate
        self.title = title
        self.subtitle = subtitle
        self.type = type
        self.dayNum = dayNum
        super.init()
    }
}

// MARK: - 地图状态协调中心
class MapStateManager: ObservableObject {
    @Published var isFullScreenMap: Bool = false
    @Published var currentDay: Int = 1
    @Published var routeCoordinates: [CLLocationCoordinate2D] = []
    
    weak var mapView: MKMapView?
    
    func updateRegion(center: CLLocationCoordinate2D, latSpan: Double = 0.8, lonSpan: Double = 0.8, animated: Bool = true) {
        let span = MKCoordinateSpan(latitudeDelta: latSpan, longitudeDelta: lonSpan)
        let region = MKCoordinateRegion(center: center, span: span)
        mapView?.setRegion(region, animated: animated)
    }
    
    func fitCoordinates(_ coords: [CLLocationCoordinate2D], animated: Bool = true) {
        guard !coords.isEmpty else { return }
        var minLat = coords[0].latitude
        var maxLat = coords[0].latitude
        var minLon = coords[0].longitude
        var maxLon = coords[0].longitude
        
        for c in coords {
            minLat = min(minLat, c.latitude)
            maxLat = max(maxLat, c.latitude)
            minLon = min(minLon, c.longitude)
            maxLon = max(maxLon, c.longitude)
        }
        
        let center = CLLocationCoordinate2D(latitude: (minLat + maxLat) / 2.0, longitude: (minLon + maxLon) / 2.0)
        let latDelta = max(0.1, (maxLat - minLat) * 1.35)
        let lonDelta = max(0.1, (maxLon - minLon) * 1.35)
        let region = MKCoordinateRegion(center: center, span: MKCoordinateSpan(latitudeDelta: latDelta, longitudeDelta: lonDelta))
        mapView?.setRegion(region, animated: animated)
    }
}

// MARK: - 主界面视图
struct ContentView: View {
    @StateObject private var mapState = MapStateManager()
    
    var body: some View {
        ZStack {
            Color(hex: "#0f172a").ignoresSafeArea()
            
            VStack(spacing: 0) {
                // 顶部：Apple 原生 MapKit（硬件加速、高德数据源、永不白屏、毫秒级响应）
                if !mapState.isFullScreenMap {
                    NativeMapKitView(mapState: mapState)
                        .frame(height: UIScreen.main.bounds.height * 0.36)
                        .clipped()
                        .shadow(color: Color.black.opacity(0.4), radius: 8, x: 0, y: 4)
                        .transition(.move(edge: .top).combined(with: .opacity))
                } else {
                    NativeMapKitView(mapState: mapState)
                        .edgesIgnoringSafeArea(.all)
                        .transition(.opacity)
                }
                
                // 下部：路书卡片与 Liquid Glass Dock 混合视图
                if !mapState.isFullScreenMap {
                    HybridTripWebView(mapState: mapState)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .ignoresSafeArea(edges: mapState.isFullScreenMap ? .all : .top)
        }
    }
}

// MARK: - Native MapKit 视图包装器
struct NativeMapKitView: UIViewRepresentable {
    @ObservedObject var mapState: MapStateManager
    
    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        mapView.showsUserLocation = true
        mapView.showsCompass = true
        mapView.showsScale = true
        mapView.mapType = .standard
        mapView.overrideUserInterfaceStyle = .dark
        
        // 初始视野：新疆全境全貌
        let xinjiangCenter = CLLocationCoordinate2D(latitude: 45.0, longitude: 87.5)
        let span = MKCoordinateSpan(latitudeDelta: 10.0, longitudeDelta: 10.0)
        mapView.setRegion(MKCoordinateRegion(center: xinjiangCenter, span: span), animated: false)
        
        mapState.mapView = mapView
        context.coordinator.mapView = mapView
        context.coordinator.mapState = mapState
        
        return mapView
    }
    
    func updateUIView(_ uiView: MKMapView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, MKMapViewDelegate {
        weak var mapView: MKMapView?
        weak var mapState: MapStateManager?
        var currentPolyline: MKPolyline?
        
        func mapView(_ mapView: MKMapView, rendererFor overlay: MKOverlay) -> MKOverlayRenderer {
            if let polyline = overlay as? MKPolyline {
                let renderer = MKPolylineRenderer(polyline: polyline)
                renderer.strokeColor = UIColor(red: 0.65, green: 0.35, blue: 0.98, alpha: 0.95) // 紫色自驾走廊
                renderer.lineWidth = 5.0
                renderer.lineCap = .round
                renderer.lineJoin = .round
                return renderer
            }
            return MKOverlayRenderer(overlay: overlay)
        }
        
        func mapView(_ mapView: MKMapView, viewFor annotation: MKAnnotation) -> MKAnnotationView? {
            guard let tripAnn = annotation as? TripAnnotation else { return nil }
            let identifier = "TripMarker"
            var marker = mapView.dequeueReusableAnnotationView(withIdentifier: identifier) as? MKMarkerAnnotationView
            if marker == nil {
                marker = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: identifier)
                marker?.canShowCallout = true
            } else {
                marker?.annotation = annotation
            }
            
            switch tripAnn.type {
            case "day":
                marker?.markerTintColor = UIColor(red: 0.58, green: 0.20, blue: 0.92, alpha: 1.0)
                marker?.glyphText = "D\(tripAnn.dayNum)"
            case "dine":
                marker?.markerTintColor = UIColor(red: 0.94, green: 0.36, blue: 0.15, alpha: 1.0)
                marker?.glyphText = "🍲"
            case "bird":
                marker?.markerTintColor = UIColor(red: 0.05, green: 0.65, blue: 0.40, alpha: 1.0)
                marker?.glyphText = "🦅"
            case "culture":
                marker?.markerTintColor = UIColor(red: 0.70, green: 0.50, blue: 0.10, alpha: 1.0)
                marker?.glyphText = "🏛️"
            default:
                marker?.markerTintColor = UIColor(red: 0.02, green: 0.52, blue: 0.78, alpha: 1.0)
                marker?.glyphText = "📍"
            }
            
            return marker
        }
    }
}

// MARK: - Hybrid Trip Web View (带 Native JS Bridge 通信)
struct HybridTripWebView: UIViewRepresentable {
    @ObservedObject var mapState: MapStateManager
    static let remoteURLString = "https://noodlesfzy.github.io/xinjiang-trip/"
    
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        
        // 注册 Native JS Bridge
        let contentController = WKUserContentController()
        contentController.add(context.coordinator, name: "nativeMap")
        config.userContentController = contentController
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        
        context.coordinator.webView = webView
        context.coordinator.mapState = mapState
        context.coordinator.loadLocalFirst()
        
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, WKNavigationDelegate, WKScriptMessageHandler {
        weak var webView: WKWebView?
        weak var mapState: MapStateManager?
        
        func loadLocalFirst() {
            guard let webView = self.webView else { return }
            if let htmlPath = Bundle.main.path(forResource: "index", ofType: "html"),
               let htmlContent = try? String(contentsOfFile: htmlPath, encoding: .utf8) {
                let baseURL = URL(string: "https://noodlesfzy.github.io/xinjiang-trip/")
                webView.loadHTMLString(htmlContent, baseURL: baseURL)
                print("📦 已加载 App 内置最新离线路书")
            }
        }
        
        // MARK: - WKScriptMessageHandler (接收来自 Web 的地图联动指令)
        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            guard message.name == "nativeMap",
                  let body = message.body as? [String: Any],
                  let action = body["action"] as? String else { return }
            
            DispatchQueue.main.async {
                guard let mapState = self.mapState, let mapView = mapState.mapView else { return }
                
                if action == "initRoute", let pts = body["points"] as? [[Double]] {
                    // 绘制全疆自驾大环线
                    let coords = pts.map { CLLocationCoordinate2D(latitude: $0[0], longitude: $0[1]) }
                    mapState.routeCoordinates = coords
                    
                    let overlays = mapView.overlays
                    mapView.removeOverlays(overlays)
                    
                    let polyline = MKPolyline(coordinates: coords, count: coords.count)
                    mapView.addOverlay(polyline)
                    mapState.fitCoordinates(coords, animated: true)
                }
                else if action == "focusDay", let day = body["day"] as? Int {
                    mapState.currentDay = day
                    if let pts = body["points"] as? [[Double]], !pts.isEmpty {
                        let coords = pts.map { CLLocationCoordinate2D(latitude: $0[0], longitude: $0[1]) }
                        
                        // 移除旧的点位标记，添加今日点位
                        let oldAnns = mapView.annotations.filter { !($0 is MKUserLocation) }
                        mapView.removeAnnotations(oldAnns)
                        
                        if let waypoints = body["waypoints"] as? [[String: Any]] {
                            for wp in waypoints {
                                if let lat = wp["lat"] as? Double, let lng = wp["lng"] as? Double {
                                    let name = wp["name"] as? String ?? ""
                                    let time = wp["time"] as? String ?? ""
                                    let ann = TripAnnotation(
                                        coordinate: CLLocationCoordinate2D(latitude: lat, longitude: lng),
                                        title: name,
                                        subtitle: "D\(day) 预计: \(time)",
                                        type: "day",
                                        dayNum: day
                                    )
                                    mapView.addAnnotation(ann)
                                }
                            }
                        }
                        
                        mapState.fitCoordinates(coords, animated: true)
                    }
                }
                else if action == "focusPOI", let lat = body["lat"] as? Double, let lng = body["lng"] as? Double {
                    let title = body["title"] as? String ?? "目标点"
                    let subtitle = body["subtitle"] as? String ?? ""
                    let type = body["type"] as? String ?? "poi"
                    let coord = CLLocationCoordinate2D(latitude: lat, longitude: lng)
                    
                    let ann = TripAnnotation(
                        coordinate: coord,
                        title: title,
                        subtitle: subtitle,
                        type: type,
                        dayNum: mapState.currentDay
                    )
                    mapView.addAnnotation(ann)
                    mapView.selectAnnotation(ann, animated: true)
                    mapState.updateRegion(center: coord, latSpan: 0.15, lonSpan: 0.15, animated: true)
                }
                else if action == "toggleFullScreen", let isFull = body["isFullScreen"] as? Bool {
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.8)) {
                        mapState.isFullScreenMap = isFull
                    }
                }
            }
        }
        
        // MARK: - WKNavigationDelegate
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow)
                return
            }
            
            let scheme = url.scheme?.lowercased() ?? ""
            if scheme == "dianping" || scheme == "xhsdiscover" || scheme == "iosamap" || scheme == "baidumap" || scheme == "tel" || scheme == "mailto" {
                if UIApplication.shared.canOpenURL(url) {
                    UIApplication.shared.open(url, options: [:], completionHandler: nil)
                }
                decisionHandler(.cancel)
                return
            }
            
            if navigationAction.navigationType != .linkActivated {
                decisionHandler(.allow)
                return
            }
            
            if url.absoluteString.contains("uri.amap.com/navigation") {
                if let naviScheme = URL(string: url.absoluteString.replacingOccurrences(of: "https://uri.amap.com/navigation", with: "iosamap://navi")),
                   UIApplication.shared.canOpenURL(naviScheme) {
                    UIApplication.shared.open(naviScheme, options: [:], completionHandler: nil)
                    decisionHandler(.cancel)
                    return
                }
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }
            
            if let host = url.host, host.contains("github.io") || host.contains("localhost") {
                decisionHandler(.allow)
                return
            }
            
            if scheme == "http" || scheme == "https" {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }
            
            decisionHandler(.allow)
        }
    }
}

// MARK: - 颜色 Hex 辅助扩展
extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}
'''

with open(os.path.join(APP_DIR, "XinjiangTripApp.swift"), "w", encoding="utf-8") as f:
    f.write(swift_code)

# 3. 生成 Info.plist 配置
info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleDisplayName</key>
    <string>辣鸡喵</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>com.noodles.trip</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>LSApplicationQueriesSchemes</key>
    <array>
        <string>dianping</string>
        <string>xhsdiscover</string>
        <string>iosamap</string>
        <string>baidumap</string>
    </array>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
        <key>NSAllowsArbitraryLoadsInWebContent</key>
        <true/>
        <key>NSAllowsLocalNetworking</key>
        <true/>
    </dict>
    <key>UIRequiresFullScreen</key>
    <true/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UILaunchScreen</key>
    <dict>
        <key>UIColorName</key>
        <string></string>
        <key>UIImageName</key>
        <string></string>
    </dict>
    <key>UIViewControllerBasedStatusBarAppearance</key>
    <false/>
</dict>
</plist>
'''

with open(os.path.join(APP_DIR, "Info.plist"), "w", encoding="utf-8") as f:
    f.write(info_plist)

# 4. 自动检测并永久锁定当前开发者的 Apple Team ID (解决每次重新选择 Team 报错)
def detect_development_team():
    try:
        out = subprocess.check_output(["defaults", "read", "com.apple.dt.Xcode", "IDEProvisioningTeams"]).decode("utf-8", errors="ignore")
        m = re.search(r'teamID\s*=\s*"?([A-Z0-9]{10})"?', out)
        if m and m.group(1):
            return m.group(1)
    except Exception:
        pass
    pbx_path = os.path.join(PBX_DIR, "project.pbxproj")
    if os.path.exists(pbx_path):
        try:
            with open(pbx_path, "r", encoding="utf-8") as f:
                content = f.read()
                m = re.search(r'DEVELOPMENT_TEAM = "??([A-Z0-9]{10})"??;', content)
                if m and m.group(1):
                    return m.group(1)
        except Exception:
            pass
    return "D2953L7MB6"

team_id = detect_development_team()

# 5. 生成标准 PBXProject 文件 (Xcode 项目配置文件)
def gen_id():
    return uuid.uuid4().hex[:24].upper()

app_id = gen_id()
assets_id = gen_id()
swift_id = gen_id()
html_id = gen_id()
plist_id = gen_id()
group_id = gen_id()
main_group_id = gen_id()
sources_id = gen_id()
resources_id = gen_id()
frameworks_id = gen_id()
target_id = gen_id()
project_id = gen_id()
config_debug_target = gen_id()
config_release_target = gen_id()
config_list_target = gen_id()
config_debug_proj = gen_id()
config_release_proj = gen_id()
config_list_proj = gen_id()

project_pbx = f'''// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 56;
	objects = {{

/* Begin PBXBuildFile section */
		{swift_id} /* XinjiangTripApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {swift_id}F /* XinjiangTripApp.swift */; }};
		{html_id} /* index.html in Resources */ = {{isa = PBXBuildFile; fileRef = {html_id}F /* index.html */; }};
		{assets_id} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {assets_id}F /* Assets.xcassets */; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		{app_id} /* XinjiangTrip.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = XinjiangTrip.app; sourceTree = BUILT_PRODUCTS_DIR; }};
		{swift_id}F /* XinjiangTripApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = XinjiangTripApp.swift; sourceTree = "<group>"; }};
		{html_id}F /* index.html */ = {{isa = PBXFileReference; lastKnownFileType = text.html; path = index.html; sourceTree = "<group>"; }};
		{plist_id}F /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
		{assets_id}F /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		{frameworks_id} /* Frameworks */ = {{
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		{main_group_id} = {{
			isa = PBXGroup;
			children = (
				{group_id} /* XinjiangTrip */,
				{app_id} /* Products */,
			);
			sourceTree = "<group>";
		}};
		{group_id} /* XinjiangTrip */ = {{
			isa = PBXGroup;
			children = (
				{swift_id}F /* XinjiangTripApp.swift */,
				{html_id}F /* index.html */,
				{assets_id}F /* Assets.xcassets */,
				{plist_id}F /* Info.plist */,
			);
			path = XinjiangTrip;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{target_id} /* XinjiangTrip */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {config_list_target} /* Build configuration list for PBXNativeTarget "XinjiangTrip" */;
			buildPhases = (
				{sources_id} /* Sources */,
				{frameworks_id} /* Frameworks */,
				{resources_id} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = XinjiangTrip;
			productName = XinjiangTrip;
			productReference = {app_id} /* XinjiangTrip.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{project_id} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
				TargetAttributes = {{
					{target_id} = {{
						CreatedOnToolsVersion = 15.0;
						DevelopmentTeam = {team_id};
						ProvisioningStyle = Automatic;
					}};
				}};
			}};
			buildConfigurationList = {config_list_proj} /* Build configuration list for PBXProject "XinjiangTrip" */;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = zh_CN;
			hasScannedForEncodings = 0;
			knownRegions = (
				zh_CN,
				Base,
			);
			mainGroup = {main_group_id};
			productRefGroup = {main_group_id};
			projectDirPath = "";
			projectRoot = "";
			targets = (
				{target_id} /* XinjiangTrip */,
			);
		}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		{resources_id} /* Resources */ = {{
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{html_id} /* index.html in Resources */,
				{assets_id} /* Assets.xcassets in Resources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		{sources_id} /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{swift_id} /* XinjiangTripApp.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		{config_debug_proj} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
			}};
			name = Debug;
		}};
		{config_release_proj} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = s;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SWIFT_COMPILATION_MODE = wholemodule;
				SWIFT_OPTIMIZATION_LEVEL = "-O";
				VALIDATE_PRODUCT = YES;
			}};
			name = Release;
		}};
		{config_debug_target} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
				INFOPLIST_KEY_UIRequiresFullScreen = YES;
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.trip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator macosx";
				SUPPORTS_MACCATALYST = YES;
				SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2,6";
			}};
			name = Debug;
		}};
		{config_release_target} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
				INFOPLIST_KEY_UIRequiresFullScreen = YES;
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.trip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator macosx";
				SUPPORTS_MACCATALYST = YES;
				SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2,6";
			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{config_list_proj} /* Build configuration list for PBXProject "XinjiangTrip" */;
		{config_list_proj} = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{config_debug_proj} /* Debug */,
				{config_release_proj} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{config_list_target} /* Build configuration list for PBXNativeTarget "XinjiangTrip" */;
		{config_list_target} = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{config_debug_target} /* Debug */,
				{config_release_target} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
/* End XCConfigurationList section */

	}};
	rootObject = {project_id} /* Project object */;
}}
'''

with open(os.path.join(PBX_DIR, "project.pbxproj"), "w", encoding="utf-8") as f:
    f.write(project_pbx)

# 5. 生成 xcshareddata Scheme 文件，确保 Xcode 与命令行能直接识别 Scheme
shared_schemes_dir = os.path.join(PBX_DIR, "xcshareddata", "xcschemes")
os.makedirs(shared_schemes_dir, exist_ok=True)

with open("/Users/Noodles/Documents/AG_Project/ios/scheme_template.xml", "r", encoding="utf-8") as f:
    scheme_content = f.read().replace("TARGET_ID_PLACEHOLDER", target_id)

with open(os.path.join(shared_schemes_dir, "XinjiangTrip.xcscheme"), "w", encoding="utf-8") as f:
    f.write(scheme_content)

print("🎉 iOS 原生工程已成功生成至: " + IOS_DIR)

