//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  Local HTTP Server Architecture (NWListener on localhost:8088)
//  彻底摆脱 file:// 沙盒对 HTTPS 切片图片的跨域阻断，100% 对齐 Safari 纯标准 Web 环境
//

import SwiftUI
import WebKit
import Foundation
import Network
import CoreTelephony

@main
struct XinjiangTripApp: App {
    private let localServer = LocalHTTPServer()

    init() {
        // 启动内置本地高速 HTTP 服务器 (127.0.0.1:8088)
        localServer.start()
        
        // 触发国行 iOS 蜂窝与无线局域网授权
        let cellularData = CTCellularData()
        cellularData.cellularDataRestrictionDidUpdateNotifier = { _ in }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - LocalHTTPServer (基于 Apple 原生 Network.framework NWListener)
class LocalHTTPServer {
    private var listener: NWListener?
    let port: NWEndpoint.Port = 8088

    func start() {
        do {
            let params = NWParameters.tcp
            listener = try NWListener(using: params, on: port)
            listener?.newConnectionHandler = { [weak self] connection in
                self?.handleConnection(connection)
            }
            listener?.start(queue: .global(qos: .userInitiated))
            print("🚀 本地极速 HTTP 服务器已在 http://127.0.0.1:\(port)/ 启动")
        } catch {
            print("❌ 本地服务器启动失败: \(error)")
        }
    }

    private func handleConnection(_ connection: NWConnection) {
        connection.start(queue: .global(qos: .userInitiated))
        connection.receive(minimumIncompleteLength: 1, maximumLength: 65536) { [weak self] data, _, _, error in
            guard let self = self, let data = data, let reqStr = String(data: data, encoding: .utf8) else {
                connection.cancel()
                return
            }

            let lines = reqStr.components(separatedBy: "\r\n")
            guard let firstLine = lines.first else { connection.cancel(); return }
            let parts = firstLine.components(separatedBy: " ")
            guard parts.count >= 2 else { connection.cancel(); return }
            var path = parts[1]
            if path == "/" || path.isEmpty { path = "/index.html" }
            if let qIdx = path.firstIndex(of: "?") {
                path = String(path[..<qIdx])
            }

            let filename = (path as NSString).lastPathComponent
            let ext = (filename as NSString).pathExtension
            let name = (filename as NSString).deletingPathExtension

            var mime = "text/html; charset=utf-8"
            if ext == "js" { mime = "application/javascript" }
            else if ext == "css" { mime = "text/css" }
            else if ext == "png" { mime = "image/png" }
            else if ext == "jpg" || ext == "jpeg" { mime = "image/jpeg" }
            else if ext == "json" { mime = "application/json" }

            if let filePath = Bundle.main.path(forResource: name, ofType: ext.isEmpty ? nil : ext),
               let fileData = try? Data(contentsOf: URL(fileURLWithPath: filePath)) {
                let header = "HTTP/1.1 200 OK\r\nContent-Type: \(mime)\r\nContent-Length: \(fileData.count)\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: no-cache\r\nConnection: close\r\n\r\n"

                var totalData = header.data(using: .utf8)!
                totalData.append(fileData)
                connection.send(content: totalData, completion: .contentProcessed({ _ in
                    connection.cancel()
                }))
            } else {
                let notFound = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
                connection.send(content: notFound.data(using: .utf8)!, completion: .contentProcessed({ _ in
                    connection.cancel()
                }))
            }
        }
    }
}

// MARK: - ContentView
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
            // 稍等 150ms 确保本地服务器端口就绪后加载
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.15) { [weak self] in
                if let url = URL(string: "http://127.0.0.1:8088/index.html") {
                    let req = URLRequest(url: url, cachePolicy: .reloadIgnoringLocalCacheData, timeoutInterval: 10)
                    self?.webView?.load(req)
                    print("✅ 路书已通过本地 HTTP 服务器 (http://127.0.0.1:8088/index.html) 加载")
                }
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor nav: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = nav.request.url else { decisionHandler(.allow); return }
            let scheme = url.scheme?.lowercased() ?? ""

            // 本地 HTTP 服务器与内部导航直接放行
            if let host = url.host?.lowercased(), host == "127.0.0.1" || host == "localhost" {
                decisionHandler(.allow)
                return
            }

            // 第三方 App Scheme (大众点评 / 小红书 / 高德地图 / 电话 / 邮件) 原生唤起
            if ["dianping","xhsdiscover","iosamap","baidumap","tel","mailto"].contains(scheme) {
                if UIApplication.shared.canOpenURL(url) { UIApplication.shared.open(url) }
                decisionHandler(.cancel)
                return
            }

            // 高德导航外部链接
            if url.absoluteString.contains("uri.amap.com/navigation") {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }

            // 如果不是用户主动点击的外链（例如页面发起的瓦片图片、fetch、API），全部放行
            if nav.navigationType != .linkActivated {
                decisionHandler(.allow)
                return
            }

            // 用户点击的其他外部网页链接，调用系统 Safari 打开
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
