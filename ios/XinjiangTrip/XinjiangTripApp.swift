//
//  XinjiangTripApp.swift
//  辣鸡喵 — 同源代理架构：tripapp://localhost 完整托管 HTML + 瓦片代理
//  page: tripapp://localhost/index.html
//  tile: tripapp://localhost/autonavi/webrd01.is.autonavi.com/appmaptile?...
//         ↓ AppSchemeHandler 拦截，注入 Referer 后原生 URLSession 请求高德 CDN
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
// 处理所有 tripapp:// 请求：
//   /index.html        → 从 Bundle 返回本地 HTML
//   /autonavi/<host>/  → 代理到高德 CDN，注入 Referer: https://www.amap.com/
class AppSchemeHandler: NSObject, WKURLSchemeHandler {
    private let proxySession: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.requestCachePolicy = .returnCacheDataElseLoad
        cfg.urlCache = URLCache(memoryCapacity: 32*1024*1024, diskCapacity: 256*1024*1024)
        return URLSession(configuration: cfg)
    }()

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url else {
            task.didFailWithError(URLError(.badURL)); return
        }
        let path = url.path.isEmpty ? "/" : url.path

        // ── 路径 1：高德瓦片代理 ───────────────────────────────────────────
        // tripapp://localhost/autonavi/webrd01.is.autonavi.com/appmaptile?...
        if path.hasPrefix("/autonavi/") {
            let rest = String(path.dropFirst("/autonavi/".count))
            // rest = "webrd01.is.autonavi.com/appmaptile"
            let slashIdx = rest.firstIndex(of: "/") ?? rest.endIndex
            let host  = String(rest[..<slashIdx])
            let spath = slashIdx < rest.endIndex ? String(rest[slashIdx...]) : "/"
            var comps = URLComponents()
            comps.scheme = "https"
            comps.host   = host
            comps.path   = spath
            comps.percentEncodedQuery = url.query
            guard let realURL = comps.url else {
                task.didFailWithError(URLError(.badURL)); return
            }
            var req = URLRequest(url: realURL, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 15)
            req.setValue("https://www.amap.com/", forHTTPHeaderField: "Referer")
            req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148", forHTTPHeaderField: "User-Agent")
            proxySession.dataTask(with: req) { [weak task] data, resp, err in
                guard let task = task else { return }
                if let e = err { task.didFailWithError(e); return }
                // 包装一个带 CORS 头的 HTTP 响应
                let httpResp = HTTPURLResponse(
                    url: url, statusCode: 200, httpVersion: "HTTP/1.1",
                    headerFields: [
                        "Content-Type": "image/png",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "max-age=3600"
                    ]
                )!
                task.didReceive(httpResp)
                if let d = data { task.didReceive(d) }
                task.didFinish()
            }.resume()
            return
        }

        // ── 路径 2：Bundle 本地文件 ─────────────────────────────────────────
        var filePath = path == "/" ? "/index.html" : path
        let filename = (filePath as NSString).lastPathComponent
        let ext  = (filename as NSString).pathExtension
        let name = (filename as NSString).deletingPathExtension
        var mimeType = "text/plain; charset=utf-8"
        switch ext.lowercased() {
        case "html": mimeType = "text/html; charset=utf-8"
        case "js":   mimeType = "application/javascript"
        case "css":  mimeType = "text/css"
        case "png":  mimeType = "image/png"
        case "jpg", "jpeg": mimeType = "image/jpeg"
        case "json": mimeType = "application/json"
        default: break
        }
        if let fp = Bundle.main.path(forResource: name, ofType: ext.isEmpty ? nil : ext),
           let data = try? Data(contentsOf: URL(fileURLWithPath: fp)) {
            let resp = HTTPURLResponse(
                url: url, statusCode: 200, httpVersion: "HTTP/1.1",
                headerFields: ["Content-Type": mimeType, "Access-Control-Allow-Origin": "*"]
            )!
            task.didReceive(resp); task.didReceive(data); task.didFinish()
        } else {
            print("⚠️ AppSchemeHandler: file not found for \(path)")
            task.didFailWithError(URLError(.fileDoesNotExist))
        }
    }
    func webView(_ webView: WKWebView, stop task: WKURLSchemeTask) {}
}

// MARK: - HybridTripWebView
struct HybridTripWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        // 只注册一个 scheme：tripapp://
        // 同时处理 HTML 托管 + 高德瓦片代理（无跨协议问题）
        config.setURLSchemeHandler(AppSchemeHandler(), forURLScheme: "tripapp")

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
            if let url = URL(string: "tripapp://localhost/index.html") {
                webView?.load(URLRequest(url: url))
                print("✅ 路书已通过 tripapp:// 加载（同源代理模式）")
            }
        }
        func webView(_ webView: WKWebView, decidePolicyFor nav: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = nav.request.url else { decisionHandler(.allow); return }
            let scheme = url.scheme?.lowercased() ?? ""
            if scheme == "tripapp" { decisionHandler(.allow); return }
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
        case 3:  (a,r,g,b) = (255,(int>>8)*17,(int>>4 & 0xF)*17,(int & 0xF)*17)
        case 6:  (a,r,g,b) = (255,int>>16,int>>8 & 0xFF,int & 0xFF)
        case 8:  (a,r,g,b) = (int>>24,int>>16 & 0xFF,int>>8 & 0xFF,int & 0xFF)
        default: (a,r,g,b) = (255,0,0,0)
        }
        self.init(.sRGB,red:Double(r)/255,green:Double(g)/255,blue:Double(b)/255,opacity:Double(a)/255)
    }
}
