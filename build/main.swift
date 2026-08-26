import AppKit
import WebKit
import SwiftUI

@main
struct XinjiangMacApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        WindowGroup {
            MacContentView()
                .preferredColorScheme(.dark)
        }
        .windowStyle(.hiddenTitleBar)
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        if let window = NSApplication.shared.windows.first {
            window.title = "辣鸡喵"
            window.titlebarAppearsTransparent = true
            window.isOpaque = false
            window.backgroundColor = NSColor(red: 7/255, green: 10/255, blue: 18/255, alpha: 1.0)
            window.setContentSize(NSSize(width: 480, height: 920))
            window.center()
        }
    }
    
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }
}

struct MacContentView: View {
    var body: some View {
        MacLiquidWebView()
            .ignoresSafeArea()
            .background(Color(red: 7/255, green: 10/255, blue: 18/255))
    }
}

struct MacLiquidWebView: NSViewRepresentable {
    static let remoteURLString = "https://noodlesfzy.github.io/xinjiang-trip/trip_mobile.html"
    
    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.preferences.setValue(true, forKey: "allowFileAccessFromFileURLs")
        
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.setValue(false, forKey: "drawsBackground")
        
        context.coordinator.webView = webView
        context.coordinator.loadWithNetworkPriority()
        return webView
    }
    
    func updateNSView(_ nsView: WKWebView, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        weak var webView: WKWebView?
        private var isLoadingRemote = false
        
        func loadWithNetworkPriority() {
            guard let webView = self.webView else { return }
            if let remoteURL = URL(string: MacLiquidWebView.remoteURLString) {
                self.isLoadingRemote = true
                var request = URLRequest(url: remoteURL, cachePolicy: .useProtocolCachePolicy, timeoutInterval: 3.5)
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
                print("📦 [Mac App] 无网或弱网，已无缝降级读取本地离线包")
            }
        }
        
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("⚠️ [Mac App] 在线加载失败，降级本地资源")
            loadLocalFallback()
        }
        
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url else {
                decisionHandler(.allow)
                return
            }
            let scheme = url.scheme?.lowercased() ?? ""
            if scheme == "dianping" || scheme == "xhsdiscover" || scheme == "iosamap" || scheme == "baidumap" {
                NSWorkspace.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            if url.isFileURL {
                decisionHandler(.allow)
                return
            }
            if let host = url.host, host.contains("github.io") || host.contains("192.168.") || host.contains("localhost") {
                decisionHandler(.allow)
                return
            }
            if scheme == "http" || scheme == "https" {
                NSWorkspace.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            decisionHandler(.allow)
        }
    }
}
