//
//  XinjiangTripApp.swift
//  辣鸡喵 — tripapp:// 同源架构，AppSchemeHandler 统一托管 HTML + 瓦片代理
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
// 处理所有 tripapp:// 请求
//   /index.html              → Bundle 本地 HTML
//   /autonavi/<host><path>?  → 代理至高德 CDN，注入 Referer
class AppSchemeHandler: NSObject, WKURLSchemeHandler {
    // 线程安全的任务状态追踪
    private var activeURLTasks: [ObjectIdentifier: URLSessionDataTask] = [:]
    private var cancelledSchemeTaskIDs: Set<ObjectIdentifier> = []
    private let taskQueue = DispatchQueue(label: "com.noodles.tile-proxy", attributes: .concurrent)

    private lazy var session: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.timeoutIntervalForRequest  = 12
        cfg.timeoutIntervalForResource = 20
        cfg.requestCachePolicy = .returnCacheDataElseLoad
        cfg.urlCache = URLCache(memoryCapacity: 64*1024*1024, diskCapacity: 512*1024*1024)
        return URLSession(configuration: cfg)
    }()

    func webView(_ webView: WKWebView, start schemeTask: WKURLSchemeTask) {
        guard let requestURL = schemeTask.request.url else {
            schemeTask.didFailWithError(URLError(.badURL)); return
        }
        let path = requestURL.path.isEmpty ? "/" : requestURL.path
        let schemeTaskID = ObjectIdentifier(schemeTask)

        // ── 路径1：高德瓦片代理 ────────────────────────────────────────────
        // tripapp://localhost/autonavi/webrd01.is.autonavi.com/appmaptile?...
        if path.hasPrefix("/autonavi/") {
            let rest = String(path.dropFirst("/autonavi/".count))
            guard let slashRange = rest.range(of: "/") else {
                schemeTask.didFailWithError(URLError(.badURL)); return
            }
            let host  = String(rest[..<slashRange.lowerBound])      // webrd01.is.autonavi.com
            let spath = String(rest[slashRange.lowerBound...])       // /appmaptile
            let query = requestURL.query ?? ""
            let realURLStr = "https://\(host)\(spath)?\(query)"

            guard let realURL = URL(string: realURLStr) else {
                print("❌ AppSchemeHandler 无法构造 URL: \(realURLStr)")
                schemeTask.didFailWithError(URLError(.badURL)); return
            }
            var req = URLRequest(url: realURL, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 12)
            req.setValue("https://www.amap.com/", forHTTPHeaderField: "Referer")
            req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148", forHTTPHeaderField: "User-Agent")
            req.setValue("image/png,image/webp,*/*", forHTTPHeaderField: "Accept")

            let urlTask = session.dataTask(with: req) { [weak self] data, response, error in
                guard let self = self else { return }
                // 检查是否已被取消
                let wasCancelled: Bool = self.taskQueue.sync {
                    self.cancelledSchemeTaskIDs.contains(schemeTaskID)
                }
                if wasCancelled { return }

                // 从活跃任务中移除
                self.taskQueue.async(flags: .barrier) {
                    self.activeURLTasks.removeValue(forKey: schemeTaskID)
                }

                if let error = error {
                    print("❌ 瓦片请求失败: \(realURLStr) — \(error.localizedDescription)")
                    schemeTask.didFailWithError(error)
                    return
                }
                guard let data = data, !data.isEmpty else {
                    print("❌ 瓦片空数据: \(realURLStr)")
                    schemeTask.didFailWithError(URLError(.zeroByteResource))
                    return
                }
                print("✅ 瓦片加载成功: \(host)\(spath), \(data.count) bytes")
                let httpResp = HTTPURLResponse(
                    url: requestURL, statusCode: 200, httpVersion: "HTTP/1.1",
                    headerFields: [
                        "Content-Type": "image/png",
                        "Content-Length": "\(data.count)",
                        "Access-Control-Allow-Origin": "*",
                        "Cache-Control": "max-age=3600"
                    ]
                )!
                schemeTask.didReceive(httpResp)
                schemeTask.didReceive(data)
                schemeTask.didFinish()
            }
            // 注册并启动
            taskQueue.async(flags: .barrier) {
                self.activeURLTasks[schemeTaskID] = urlTask
            }
            urlTask.resume()
            return
        }

        // ── 路径2：Bundle 本地文件 ─────────────────────────────────────────
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
                url: requestURL, statusCode: 200, httpVersion: "HTTP/1.1",
                headerFields: ["Content-Type": mimeType, "Access-Control-Allow-Origin": "*"]
            )!
            schemeTask.didReceive(resp)
            schemeTask.didReceive(data)
            schemeTask.didFinish()
        } else {
            print("⚠️ AppSchemeHandler: 文件未找到 \(path)")
            schemeTask.didFailWithError(URLError(.fileDoesNotExist))
        }
    }

    func webView(_ webView: WKWebView, stop schemeTask: WKURLSchemeTask) {
        let schemeTaskID = ObjectIdentifier(schemeTask)
        taskQueue.async(flags: .barrier) { [weak self] in
            guard let self = self else { return }
            self.cancelledSchemeTaskIDs.insert(schemeTaskID)
            self.activeURLTasks[schemeTaskID]?.cancel()
            self.activeURLTasks.removeValue(forKey: schemeTaskID)
        }
    }
}

// MARK: - HybridTripWebView
struct HybridTripWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
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
            guard let url = URL(string: "tripapp://localhost/index.html") else { return }
            webView?.load(URLRequest(url: url))
            print("✅ 路书已通过 tripapp://localhost/index.html 加载")
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
