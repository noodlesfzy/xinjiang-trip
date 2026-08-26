//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  双 Custom Scheme Handler 架构：tripapp:// 托管页面 + autonavi:// 代理地图瓦片
//  彻底规避 HTTPS Mixed Content 拦截
//

import SwiftUI
import WebKit
import Foundation

@main
struct XinjiangTripApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
    }
}

struct ContentView: View {
    var body: some View {
        ZStack {
            Color(hex: "#0f172a").ignoresSafeArea()
            HybridTripWebView()
                .edgesIgnoringSafeArea(.all)
        }
    }
}

// MARK: - AppSchemeHandler
// 托管本地 HTML/JS/CSS 资源，页面源为 tripapp://localhost（非 HTTPS）
// 从而彻底规避 Mixed Content 拦截
class AppSchemeHandler: NSObject, WKURLSchemeHandler {
    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else {
            task.didFailWithError(URLError(.badURL)); return
        }

        var path = url.path
        if path == "/" || path.isEmpty { path = "/index.html" }

        // 从 App Bundle 中读取文件
        let filename = (path as NSString).lastPathComponent
        let ext = (filename as NSString).pathExtension
        let name = (filename as NSString).deletingPathExtension

        var mimeType = "text/plain"
        switch ext.lowercased() {
        case "html": mimeType = "text/html; charset=utf-8"
        case "js":   mimeType = "application/javascript"
        case "css":  mimeType = "text/css"
        case "png":  mimeType = "image/png"
        case "jpg", "jpeg": mimeType = "image/jpeg"
        case "json": mimeType = "application/json"
        default: break
        }

        if let filePath = Bundle.main.path(forResource: name, ofType: ext.isEmpty ? nil : ext),
           let data = try? Data(contentsOf: URL(fileURLWithPath: filePath)) {
            let response = HTTPURLResponse(
                url: url,
                statusCode: 200,
                httpVersion: "HTTP/1.1",
                headerFields: [
                    "Content-Type": mimeType,
                    "Access-Control-Allow-Origin": "*"
                ]
            )!
            task.didReceive(response)
            task.didReceive(data)
            task.didFinish()
        } else {
            task.didFailWithError(URLError(.fileDoesNotExist))
        }
    }
    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

// MARK: - TileProxySchemeHandler
// 拦截 autonavi:// 伪协议 → 原生 URLSession 注入 Referer，完全绕过防盗链
class TileProxySchemeHandler: NSObject, WKURLSchemeHandler {
    private let session: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.requestCachePolicy = .returnCacheDataElseLoad
        cfg.urlCache = URLCache(memoryCapacity: 32*1024*1024, diskCapacity: 256*1024*1024)
        return URLSession(configuration: cfg)
    }()

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url,
              var comps = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            task.didFailWithError(URLError(.badURL)); return
        }
        comps.scheme = "https"
        guard let realURL = comps.url else {
            task.didFailWithError(URLError(.badURL)); return
        }
        var req = URLRequest(url: realURL, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 15)
        req.setValue("https://www.amap.com/", forHTTPHeaderField: "Referer")
        req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15", forHTTPHeaderField: "User-Agent")

        session.dataTask(with: req) { [weak task] data, response, error in
            guard let task = task else { return }
            if let e = error { task.didFailWithError(e); return }
            if let r = response { task.didReceive(r) }
            if let d = data { task.didReceive(d) }
            task.didFinish()
        }.resume()
    }
    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

// MARK: - HybridTripWebView
struct HybridTripWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        // 注册双 custom scheme handler
        config.setURLSchemeHandler(AppSchemeHandler(),        forURLScheme: "tripapp")
        config.setURLSchemeHandler(TileProxySchemeHandler(),  forURLScheme: "autonavi")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        if #available(iOS 16.4, *) { webView.isInspectable = true }

        context.coordinator.webView = webView
        context.coordinator.loadApp()
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?

        func loadApp() {
            // 使用 tripapp:// 非 HTTPS 源托管页面，彻底规避 Mixed Content
            if let url = URL(string: "tripapp://localhost/index.html") {
                webView?.load(URLRequest(url: url))
                print("✅ 路书已通过 tripapp:// 加载，autonavi:// 瓦片代理已就绪")
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor nav: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = nav.request.url else { decisionHandler(.allow); return }
            let scheme = url.scheme?.lowercased() ?? ""
            // 内部自定义协议直接放行
            if scheme == "tripapp" || scheme == "autonavi" {
                decisionHandler(.allow); return
            }
            if ["dianping","xhsdiscover","iosamap","baidumap","tel","mailto"].contains(scheme) {
                if UIApplication.shared.canOpenURL(url) { UIApplication.shared.open(url) }
                decisionHandler(.cancel); return
            }
            if nav.navigationType != .linkActivated { decisionHandler(.allow); return }
            if url.absoluteString.contains("uri.amap.com/navigation") {
                UIApplication.shared.open(url); decisionHandler(.cancel); return
            }
            if let host = url.host, host.contains("github.io") || host.contains("localhost") {
                decisionHandler(.allow); return
            }
            if scheme == "http" || scheme == "https" {
                UIApplication.shared.open(url); decisionHandler(.cancel); return
            }
            decisionHandler(.allow)
        }
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3:  (a,r,g,b) = (255, (int>>8)*17, (int>>4 & 0xF)*17, (int & 0xF)*17)
        case 6:  (a,r,g,b) = (255, int>>16, int>>8 & 0xFF, int & 0xFF)
        case 8:  (a,r,g,b) = (int>>24, int>>16 & 0xFF, int>>8 & 0xFF, int & 0xFF)
        default: (a,r,g,b) = (255,0,0,0)
        }
        self.init(.sRGB, red: Double(r)/255, green: Double(g)/255, blue: Double(b)/255, opacity: Double(a)/255)
    }
}
