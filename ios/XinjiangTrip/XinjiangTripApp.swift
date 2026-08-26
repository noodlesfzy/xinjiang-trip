//
//  XinjiangTripApp.swift
//  辣鸡喵 (Xinjiang Road Trip)
//  Local HTTP Server + Native Tile Relay + Detailed Diagnostic Logging
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
        localServer.start()
        
        let cellularData = CTCellularData()
        cellularData.cellularDataRestrictionDidUpdateNotifier = { state in
            print("📶 Cellular Data State: \(state.rawValue)")
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - LocalHTTPServer
class LocalHTTPServer {
    private var listener: NWListener?
    let port: NWEndpoint.Port = 8088
    
    private let tileSession: URLSession = {
        let cfg = URLSessionConfiguration.default
        cfg.timeoutIntervalForRequest = 10
        cfg.timeoutIntervalForResource = 15
        cfg.requestCachePolicy = .returnCacheDataElseLoad
        cfg.urlCache = URLCache(memoryCapacity: 64*1024*1024, diskCapacity: 256*1024*1024)
        return URLSession(configuration: cfg)
    }()

    func start() {
        do {
            let params = NWParameters.tcp
            listener = try NWListener(using: params, on: port)
            listener?.newConnectionHandler = { [weak self] connection in
                self?.handleConnection(connection)
            }
            listener?.start(queue: .global(qos: .userInitiated))
            print("🚀 本地服务器已在端口 \(port) 启动")
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
            let fullPath = parts[1]
            
            var path = fullPath
            var query = ""
            if let qIdx = fullPath.firstIndex(of: "?") {
                path = String(fullPath[..<qIdx])
                query = String(fullPath[fullPath.index(after: qIdx)...])
            }
            if path == "/" || path.isEmpty { path = "/index.html" }

            // ── 路径 1：瓦片中继与调试 ─────────────────────────────────────────
            if path == "/maptile" {
                let params = self.parseQuery(query)
                let s = params["s"] ?? "1"
                let style = params["style"] ?? "7"
                let x = params["x"] ?? "0"
                let y = params["y"] ?? "0"
                let z = params["z"] ?? "0"
                
                let gaodeURLStr = "https://wprd0\(s).is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=\(style)&x=\(x)&y=\(y)&z=\(z)"
                guard let gaodeURL = URL(string: gaodeURLStr) else {
                    self.sendNotFound(connection, reason: "Bad URL")
                    return
                }
                
                var req = URLRequest(url: gaodeURL, cachePolicy: .returnCacheDataElseLoad, timeoutInterval: 8)
                req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", forHTTPHeaderField: "User-Agent")
                
                self.tileSession.dataTask(with: req) { tileData, resp, err in
                    if let err = err {
                        print("❌ 瓦片下载失败 [\(z)/\(x)/\(y)]: \(err.localizedDescription)")
                        self.sendNotFound(connection, reason: err.localizedDescription)
                        return
                    }
                    guard let tileData = tileData, !tileData.isEmpty else {
                        print("❌ 瓦片数据为空 [\(z)/\(x)/\(y)]")
                        self.sendNotFound(connection, reason: "Empty data")
                        return
                    }
                    
                    let header = "HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: \(tileData.count)\r\nAccess-Control-Allow-Origin: *\r\nCache-Control: public, max-age=86400\r\nConnection: close\r\n\r\n"
                    var total = header.data(using: .utf8)!
                    total.append(tileData)
                    connection.send(content: total, completion: .contentProcessed({ _ in
                        connection.cancel()
                    }))
                }.resume()
                return
            }

            // ── 路径 2：诊断接口 (/diag) ───────────────────────────────────────
            if path == "/diag" {
                let diagURL = URL(string: "https://wprd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x=47&y=23&z=6")!
                var req = URLRequest(url: diagURL, timeoutInterval: 5)
                req.setValue("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)", forHTTPHeaderField: "User-Agent")
                self.tileSession.dataTask(with: req) { d, r, e in
                    let status = (r as? HTTPURLResponse)?.statusCode ?? 0
                    let resJSON = "{\"http_status\": \(status), \"data_bytes\": \(d?.count ?? 0), \"error\": \"\(e?.localizedDescription ?? "none")\"}"
                    let header = "HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n"
                    var total = header.data(using: .utf8)!
                    total.append(resJSON.data(using: .utf8)!)
                    connection.send(content: total, completion: .contentProcessed({ _ in connection.cancel() }))
                }.resume()
                return
            }

            // ── 路径 3：本地静态资源 ──────────────────────────────────────────
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
                self.sendNotFound(connection, reason: "File not found: \(path)")
            }
        }
    }
    
    private func parseQuery(_ q: String) -> [String: String] {
        var res: [String: String] = [:]
        for item in q.components(separatedBy: "&") {
            let pair = item.components(separatedBy: "=")
            if pair.count == 2 { res[pair[0]] = pair[1] }
        }
        return res
    }
    
    private func sendNotFound(_ connection: NWConnection, reason: String = "") {
        let msg = "HTTP/1.1 404 Not Found\r\nX-Error-Reason: \(reason)\r\nContent-Length: 0\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n"
        connection.send(content: msg.data(using: .utf8)!, completion: .contentProcessed({ _ in
            connection.cancel()
        }))
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

            if let host = url.host?.lowercased(), host == "127.0.0.1" || host == "localhost" {
                decisionHandler(.allow)
                return
            }

            if ["dianping","xhsdiscover","iosamap","baidumap","tel","mailto"].contains(scheme) {
                if UIApplication.shared.canOpenURL(url) { UIApplication.shared.open(url) }
                decisionHandler(.cancel)
                return
            }

            if url.absoluteString.contains("uri.amap.com/navigation") {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }

            if nav.navigationType != .linkActivated {
                decisionHandler(.allow)
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
