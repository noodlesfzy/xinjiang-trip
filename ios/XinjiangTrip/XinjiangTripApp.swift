//
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
