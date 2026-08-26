//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  Clean Native WKWebView with Cellular Data Authorization Trigger
//

import SwiftUI
import WebKit
import Foundation
import CoreTelephony
import Network

@main
struct XinjiangTripApp: App {
    init() {
        // 显式触发国行 iOS 网络权限弹窗 (无线局域网与蜂窝网络)
        let cellularData = CTCellularData()
        cellularData.cellularDataRestrictionDidUpdateNotifier = { state in
            print("📶 网络权限状态变更: \(state.rawValue)")
        }
        
        // 触发一次原生网络请求唤醒 iOS 网络栈
        if let testURL = URL(string: "https://www.apple.com/library/test/success.html") {
            let task = URLSession.shared.dataTask(with: testURL) { data, _, _ in
                if let d = data {
                    print("🌐 网络连通性测试成功: \(d.count) 字节")
                }
            }
            task.resume()
        }
    }

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

// MARK: - HybridTripWebView
struct HybridTripWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        config.setValue(true, forKey: "allowUniversalAccessFromFileURLs")

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.backgroundColor = UIColor(red: 0.06, green: 0.09, blue: 0.16, alpha: 1.0)
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        if #available(iOS 16.4, *) {
            webView.isInspectable = true
        }

        context.coordinator.webView = webView
        context.coordinator.loadApp()
        return webView
    }

    func updateUIView(_ uiView: WKWebView, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator() }

    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?

        func loadApp() {
            if let htmlPath = Bundle.main.path(forResource: "index", ofType: "html"),
               let htmlContent = try? String(contentsOfFile: htmlPath, encoding: .utf8) {
                let baseURL = URL(string: "https://noodlesfzy.github.io/xinjiang-trip/")
                webView?.loadHTMLString(htmlContent, baseURL: baseURL)
                print("✅ 路书已通过 loadHTMLString (HTTPS baseURL) 加载成功")
            } else {
                print("❌ 未找到 index.html")
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor nav: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = nav.request.url else { decisionHandler(.allow); return }
            let scheme = url.scheme?.lowercased() ?? ""
            if scheme == "file" {
                decisionHandler(.allow)
                return
            }
            if ["dianping","xhsdiscover","iosamap","baidumap","tel","mailto"].contains(scheme) {
                if UIApplication.shared.canOpenURL(url) { UIApplication.shared.open(url) }
                decisionHandler(.cancel)
                return
            }
            if nav.navigationType != .linkActivated {
                decisionHandler(.allow)
                return
            }
            if url.absoluteString.contains("uri.amap.com/navigation") {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            if scheme == "http" || scheme == "https" {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
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
