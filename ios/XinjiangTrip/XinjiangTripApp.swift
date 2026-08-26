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
        HybridTripWebView()
            .ignoresSafeArea()
            .background(Color(red: 13/255, green: 19/255, blue: 34/255))
    }
}

struct HybridTripWebView: UIViewRepresentable {
    // 线上实时路书地址（优先调用，获取最新实时路况、天气、通知与动态信息）
    static let remoteURLString = "https://noodlesfzy.github.io/xinjiang-trip/trip_mobile.html"
    
    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true
        config.mediaTypesRequiringUserActionForPlayback = []
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.isOpaque = false
        webView.backgroundColor = UIColor(red: 13/255, green: 19/255, blue: 34/255, alpha: 1.0)
        webView.scrollView.bounces = true
        webView.scrollView.contentInsetAdjustmentBehavior = .never
        
        // 绑定下拉刷新控件 (Pull to Refresh)
        let refreshControl = UIRefreshControl()
        refreshControl.tintColor = UIColor(red: 248/255, green: 113/255, blue: 113/255, alpha: 1.0)
        refreshControl.addTarget(context.coordinator, action: #selector(Coordinator.handleRefresh(_:)), for: .valueChanged)
        webView.scrollView.refreshControl = refreshControl
        
        context.coordinator.webView = webView
        
        // 启动加载：在线优先检测与加载
        context.coordinator.loadWithNetworkPriority()
        
        return webView
    }
    
    func updateUIView(_ uiView: WKWebView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?
        private var hasLoadedSuccessfully = false
        private var isLoadingRemote = false
        
        @objc func handleRefresh(_ sender: UIRefreshControl) {
            loadWithNetworkPriority()
        }
        
        func loadWithNetworkPriority() {
            guard let webView = self.webView else { return }
            
            // 1. 发起带 3.5 秒超时的在线优先请求
            if let remoteURL = URL(string: HybridTripWebView.remoteURLString) {
                self.isLoadingRemote = true
                var request = URLRequest(url: remoteURL, cachePolicy: .useProtocolCachePolicy, timeoutInterval: 3.5)
                request.addValue("XinjiangTrip-iOS-Hybrid", forHTTPHeaderField: "User-Agent")
                webView.load(request)
            } else {
                loadLocalFallback()
            }
        }
        
        func loadLocalFallback() {
            guard let webView = self.webView else { return }
            self.isLoadingRemote = false
            
            if let htmlPath = Bundle.main.path(forResource: "index", ofType: "html") {
                let fileURL = URL(fileURLWithPath: htmlPath)
                let bundleDir = Bundle.main.bundleURL
                webView.loadFileURL(fileURL, allowingReadAccessTo: bundleDir)
                print("📦 网络不佳或无信号，已无缝切换至本地离线路书资源")
            }
            
            webView.scrollView.refreshControl?.endRefreshing()
        }
        
        // MARK: - WKNavigationDelegate
        
        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            self.hasLoadedSuccessfully = true
            webView.scrollView.refreshControl?.endRefreshing()
            if self.isLoadingRemote {
                print("🌐 成功加载在线最新路书资源")
            }
        }
        
        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            print("⚠️ 页面加载失败: \(error.localizedDescription)")
            if !self.hasLoadedSuccessfully || self.isLoadingRemote {
                loadLocalFallback()
            } else {
                webView.scrollView.refreshControl?.endRefreshing()
            }
        }
        
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("⚠️ 网络不可用或超时: \(error.localizedDescription)，立即降级读取本地离线包")
            loadLocalFallback()
        }
        
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow)
                return
            }
            
            let scheme = url.scheme?.lowercased() ?? ""
            
            // 拦截并直接唤起 iPhone 原生 App（大众点评、小红书、高德、百度地图、电话等）
            if scheme == "dianping" || scheme == "xhsdiscover" || scheme == "iosamap" || scheme == "baidumap" || scheme == "tel" || scheme == "mailto" {
                if UIApplication.shared.canOpenURL(url) {
                    UIApplication.shared.open(url, options: [:], completionHandler: nil)
                } else {
                    // 若未安装 App，且为大众点评/小红书，降级调用系统 Safari 页面
                    if url.absoluteString.contains("dianping") || url.absoluteString.contains("xiaohongshu") {
                        UIApplication.shared.open(url, options: [:], completionHandler: nil)
                    }
                }
                decisionHandler(.cancel)
                return
            }
            
            // 允许本地离线文件
            if url.isFileURL {
                decisionHandler(.allow)
                return
            }
            
            // 如果是本路书的在线域名，允许在 WebView 内部实时浏览
            if let host = url.host, host.contains("github.io") || host.contains("192.168.") || host.contains("localhost") {
                decisionHandler(.allow)
                return
            }
            
            // 其他外部链接（如外部资讯、外部网站），统一调用系统 Safari 打开，避免污染路书主界面
            if scheme == "http" || scheme == "https" {
                UIApplication.shared.open(url, options: [:], completionHandler: nil)
                decisionHandler(.cancel)
                return
            }
            
            decisionHandler(.allow)
        }
    }
}
