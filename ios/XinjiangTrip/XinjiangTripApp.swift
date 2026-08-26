//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  WKURLSchemeHandler 原生代理注入 Referer，彻底破解高德防盗链
//

import SwiftUI
import WebKit

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

// MARK: - TileProxySchemeHandler
// 拦截 JS 中的 autonavi:// 伪协议请求 → 转为真实 https://
// 并在原生 URLRequest 层注入 Referer: https://www.amap.com/
// 从根本上解决 WKWebView 无法发送 Referer 的问题
class TileProxySchemeHandler: NSObject, WKURLSchemeHandler {
    private let session = URLSession(configuration: {
        let cfg = URLSessionConfiguration.default
        cfg.requestCachePolicy = .returnCacheDataElseLoad
        cfg.urlCache = URLCache(memoryCapacity: 32 * 1024 * 1024, diskCapacity: 256 * 1024 * 1024)
        return cfg
    }())

    func webView(_ webView: WKWebView, start task: WKURLSchemeTask) {
        guard let url = task.request.url,
              var comps = URLComponents(url: url, resolvingAgainstBaseURL: false) else {
            task.didFailWithError(URLError(.badURL))
            return
        }
        comps.scheme = "https"
        guard let realURL = comps.url else {
            task.didFailWithError(URLError(.badURL))
            return
        }
        var req = URLRequest(url: realURL, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 15)
        req.setValue("https://www.amap.com/", forHTTPHeaderField: "Referer")
        req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148", forHTTPHeaderField: "User-Agent")
        req.setValue("image/webp,image/png,*/*", forHTTPHeaderField: "Accept")

        session.dataTask(with: req) { [weak task] data, response, error in
            guard let task = task else { return }
            if let error = error { task.didFailWithError(error); return }
            if let response = response { task.didReceive(response) }
            if let data = data { task.didReceive(data) }
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
        // 注册 autonavi:// 自定义协议，所有 JS 瓦片请求都经过原生代理
        config.setURLSchemeHandler(TileProxySchemeHandler(), forURLScheme: "autonavi")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.contentInsetAdjustmentBehavior = .never

        context.coordinator.webView = webView
        context.coordinator.loadLocalFirst()
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?

        func loadLocalFirst() {
            guard let webView = self.webView else { return }
            if let htmlPath = Bundle.main.path(forResource: "index", ofType: "html"),
               let html = try? String(contentsOfFile: htmlPath, encoding: .utf8) {
                let base = URL(string: "https://noodlesfzy.github.io/xinjiang-trip/")
                webView.loadHTMLString(html, baseURL: base)
                print("✅ 路书已加载，autonavi:// 代理瓦片管道已就绪")
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor nav: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = nav.request.url else { decisionHandler(.allow); return }
            let scheme = url.scheme?.lowercased() ?? ""
            if ["dianping","xhsdiscover","iosamap","baidumap","tel","mailto"].contains(scheme) {
                if UIApplication.shared.canOpenURL(url) {
                    UIApplication.shared.open(url)
                }
                decisionHandler(.cancel); return
            }
            if nav.navigationType != .linkActivated { decisionHandler(.allow); return }
            if url.absoluteString.contains("uri.amap.com/navigation") {
                UIApplication.shared.open(url)
                decisionHandler(.cancel); return
            }
            if let host = url.host, host.contains("github.io") || host.contains("localhost") {
                decisionHandler(.allow); return
            }
            if scheme == "http" || scheme == "https" {
                UIApplication.shared.open(url)
                decisionHandler(.cancel); return
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
