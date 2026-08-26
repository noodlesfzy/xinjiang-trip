import os
import shutil
import subprocess

PROJECT_DIR = "/Users/Noodles/Documents/AG_Project"
BUILD_DIR = os.path.join(PROJECT_DIR, "build")
APP_BUNDLE = os.path.join(BUILD_DIR, "新疆自驾路书.app")
CONTENTS_DIR = os.path.join(APP_BUNDLE, "Contents")
MACOS_DIR = os.path.join(CONTENTS_DIR, "MacOS")
RESOURCES_DIR = os.path.join(CONTENTS_DIR, "Resources")

os.makedirs(MACOS_DIR, exist_ok=True)
os.makedirs(RESOURCES_DIR, exist_ok=True)

# 1. 复制最新编译的手机版/通用版路书到 App 资源目录
shutil.copy2(os.path.join(PROJECT_DIR, "trip_mobile.html"), os.path.join(RESOURCES_DIR, "index.html"))

# 2. 生成 App Info.plist
info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleDisplayName</key>
    <string>新疆自驾路书</string>
    <key>CFBundleExecutable</key>
    <string>XinjiangTrip</string>
    <key>CFBundleIdentifier</key>
    <string>com.noodles.xinjiangtrip.mac</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>新疆自驾路书</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
'''

with open(os.path.join(CONTENTS_DIR, "Info.plist"), "w", encoding="utf-8") as f:
    f.write(info_plist)

# 3. 编写 macOS 原生 Liquid Glass 独立容器 (采用 SwiftUI + AppKit + WebKit)
swift_source = '''import AppKit
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
            window.title = "新疆14天自驾路书"
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
'''

src_path = os.path.join(BUILD_DIR, "main.swift")
with open(src_path, "w", encoding="utf-8") as f:
    f.write(swift_source)

# 4. 自动调用 swiftc 编译器进行原生 Release 编译
bin_path = os.path.join(MACOS_DIR, "XinjiangTrip")
cmd = [
    "swiftc",
    "-parse-as-library",
    src_path,
    "-o", bin_path,
    "-target", "arm64-apple-macos13.0",
    "-O",
    "-framework", "AppKit",
    "-framework", "WebKit",
    "-framework", "SwiftUI"
]

print("🔨 正在自动编译原生 macOS / iOS 架构独立可执行文件...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0:
    print(f"🎉 编译成功！独立原生 App 已生成至: {APP_BUNDLE}")
else:
    print("❌ 编译报错:", res.stderr)
