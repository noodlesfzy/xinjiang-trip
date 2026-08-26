import SwiftUI
import WebKit

@main
struct XinjiangTripApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .ignoresSafeArea()
                .preferredColorScheme(.dark)
        }
    }
}

struct ContentView: View {
    var body: some View {
        OfflineWebView()
            .ignoresSafeArea()
            .background(Color(red: 13/255, green: 19/255, blue: 34/255))
    }
}

struct OfflineWebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 13/255, green: 19/255, blue: 34/255, alpha: 1.0)
        webView.scrollView.bounces = false
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        
        if let htmlPath = Bundle.main.path(forResource: "index", ofType: "html") {
            let fileURL = URL(fileURLWithPath: htmlPath)
            let bundleDir = Bundle.main.bundleURL
            webView.loadFileURL(fileURL, allowingReadAccessTo: bundleDir)
        }
        
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow)
                return
            }
            
            let scheme = url.scheme?.lowercased() ?? ""
            
            // 拦截外部原生 App 协议（大众点评、小红书、高德、百度地图、电话等）
            if scheme == "dianping" || scheme == "xhsdiscover" || scheme == "iosamap" || scheme == "baidumap" || scheme == "tel" || scheme == "mailto" {
                if UIApplication.shared.canOpenURL(url) {
                    UIApplication.shared.open(url, options: [:], completionHandler: nil)
                } else {
                    // 若未安装 App，且为大众点评/小红书，降级为 Safari 网页打开
                    if let host = url.host, (url.absoluteString.contains("dianping") || url.absoluteString.contains("xiaohongshu")) {
                        UIApplication.shared.open(url, options: [:], completionHandler: nil)
                    }
                }
                decisionHandler(.cancel)
                return
            }
            
            // 允许本地 HTML 与正常外链
            if url.isFileURL {
                decisionHandler(.allow)
            } else if scheme == "http" || scheme == "https" {
                // 外链跳转系统浏览器，保持路书主界面干净
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
            } else {
                decisionHandler(.allow)
            }
        }
    }
}
