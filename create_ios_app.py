#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_ios_app.py — 一键构建原生 iOS Xcode 工程 (XinjiangTrip)
将 trip_mobile.html 深度打包为 100% 离线运行、支持大众点评/小红书原生 Scheme 唤起的 iOS 原生 App。
"""

import os
import shutil
import uuid

IOS_DIR = "/Users/Noodles/Documents/AG_Project/ios"
APP_DIR = os.path.join(IOS_DIR, "XinjiangTrip")
PBX_DIR = os.path.join(IOS_DIR, "XinjiangTrip.xcodeproj")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(PBX_DIR, exist_ok=True)

# 1. 复制最新编译的手机版路书到 App Bundle 资源目录
shutil.copy2("/Users/Noodles/Documents/AG_Project/trip_mobile.html", os.path.join(APP_DIR, "index.html"))

# 2. 生成原生 Swift 入口文件
swift_code = '''import SwiftUI
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
            print("⚠️ 页面加载失败: \\(error.localizedDescription)")
            if !self.hasLoadedSuccessfully || self.isLoadingRemote {
                loadLocalFallback()
            } else {
                webView.scrollView.refreshControl?.endRefreshing()
            }
        }
        
        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            print("⚠️ 网络不可用或超时: \\(error.localizedDescription)，立即降级读取本地离线包")
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
'''

with open(os.path.join(APP_DIR, "XinjiangTripApp.swift"), "w", encoding="utf-8") as f:
    f.write(swift_code)

# 3. 生成 Info.plist 配置
info_plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>zh_CN</string>
    <key>CFBundleDisplayName</key>
    <string>辣鸡喵</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>com.noodles.trip</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$(PRODUCT_NAME)</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>LSApplicationQueriesSchemes</key>
    <array>
        <string>dianping</string>
        <string>xhsdiscover</string>
        <string>iosamap</string>
        <string>baidumap</string>
    </array>
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    <key>UIRequiresFullScreen</key>
    <true/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UISupportedInterfaceOrientations~ipad</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
        <string>UIInterfaceOrientationPortraitUpsideDown</string>
        <string>UIInterfaceOrientationLandscapeLeft</string>
        <string>UIInterfaceOrientationLandscapeRight</string>
    </array>
    <key>UIViewControllerBasedStatusBarAppearance</key>
    <false/>
</dict>
</plist>
'''

with open(os.path.join(APP_DIR, "Info.plist"), "w", encoding="utf-8") as f:
    f.write(info_plist)

# 4. 生成标准 PBXProject 文件 (Xcode 项目配置文件)
def gen_id():
    return uuid.uuid4().hex[:24].upper()

app_id = gen_id()
assets_id = gen_id()
swift_id = gen_id()
html_id = gen_id()
plist_id = gen_id()
group_id = gen_id()
main_group_id = gen_id()
sources_id = gen_id()
resources_id = gen_id()
frameworks_id = gen_id()
target_id = gen_id()
project_id = gen_id()
config_debug_target = gen_id()
config_release_target = gen_id()
config_list_target = gen_id()
config_debug_proj = gen_id()
config_release_proj = gen_id()
config_list_proj = gen_id()

project_pbx = f'''// !$*UTF8*$!
{{
	archiveVersion = 1;
	classes = {{
	}};
	objectVersion = 56;
	objects = {{

/* Begin PBXBuildFile section */
		{swift_id} /* XinjiangTripApp.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {swift_id}F /* XinjiangTripApp.swift */; }};
		{html_id} /* index.html in Resources */ = {{isa = PBXBuildFile; fileRef = {html_id}F /* index.html */; }};
		{assets_id} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {assets_id}F /* Assets.xcassets */; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		{app_id} /* XinjiangTrip.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = XinjiangTrip.app; sourceTree = BUILT_PRODUCTS_DIR; }};
		{swift_id}F /* XinjiangTripApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = XinjiangTripApp.swift; sourceTree = "<group>"; }};
		{html_id}F /* index.html */ = {{isa = PBXFileReference; lastKnownFileType = text.html; path = index.html; sourceTree = "<group>"; }};
		{plist_id}F /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
		{assets_id}F /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
		{frameworks_id} /* Frameworks */ = {{
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
		{main_group_id} = {{
			isa = PBXGroup;
			children = (
				{group_id} /* XinjiangTrip */,
				{app_id} /* Products */,
			);
			sourceTree = "<group>";
		}};
		{group_id} /* XinjiangTrip */ = {{
			isa = PBXGroup;
			children = (
				{swift_id}F /* XinjiangTripApp.swift */,
				{html_id}F /* index.html */,
				{assets_id}F /* Assets.xcassets */,
				{plist_id}F /* Info.plist */,
			);
			path = XinjiangTrip;
			sourceTree = "<group>";
		}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
		{target_id} /* XinjiangTrip */ = {{
			isa = PBXNativeTarget;
			buildConfigurationList = {config_list_target} /* Build configuration list for PBXNativeTarget "XinjiangTrip" */;
			buildPhases = (
				{sources_id} /* Sources */,
				{frameworks_id} /* Frameworks */,
				{resources_id} /* Resources */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = XinjiangTrip;
			productName = XinjiangTrip;
			productReference = {app_id} /* XinjiangTrip.app */;
			productType = "com.apple.product-type.application";
		}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
		{project_id} /* Project object */ = {{
			isa = PBXProject;
			attributes = {{
				BuildIndependentTargetsInParallel = 1;
				LastSwiftUpdateCheck = 1500;
				LastUpgradeCheck = 1500;
				TargetAttributes = {{
					{target_id} = {{
						CreatedOnToolsVersion = 15.0;
					}};
				}};
			}};
			buildConfigurationList = {config_list_proj} /* Build configuration list for PBXProject "XinjiangTrip" */;
			compatibilityVersion = "Xcode 14.0";
			developmentRegion = zh_CN;
			hasScannedForEncodings = 0;
			knownRegions = (
				zh_CN,
				Base,
			);
			mainGroup = {main_group_id};
			productRefGroup = {main_group_id};
			projectDirPath = "";
			projectRoot = "";
			targets = (
				{target_id} /* XinjiangTrip */,
			);
		}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
		{resources_id} /* Resources */ = {{
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{html_id} /* index.html in Resources */,
				{assets_id} /* Assets.xcassets in Resources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
		{sources_id} /* Sources */ = {{
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
				{swift_id} /* XinjiangTripApp.swift in Sources */,
			);
			runOnlyForDeploymentPostprocessing = 0;
		}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
		{config_debug_proj} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;
				SWIFT_OPTIMIZATION_LEVEL = "-Onone";
			}};
			name = Debug;
		}};
		{config_release_proj} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ALWAYS_SEARCH_USER_PATHS = NO;
				CLANG_ANALYZER_NONNULL = YES;
				CLANG_ENABLE_MODULES = YES;
				CLANG_ENABLE_OBJC_ARC = YES;
				CLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
				CLANG_WARN_BOOL_CONVERSION = YES;
				CLANG_WARN_COMMA = YES;
				CLANG_WARN_CONSTANT_CONVERSION = YES;
				CLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
				CLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
				CLANG_WARN_DOCUMENTATION_COMMENTS = YES;
				CLANG_WARN_EMPTY_BODY = YES;
				CLANG_WARN_ENUM_CONVERSION = YES;
				CLANG_WARN_INFINITE_RECURSION = YES;
				CLANG_WARN_INT_CONVERSION = YES;
				CLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
				CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
				CLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
				CLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
				CLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
				CLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
				CLANG_WARN_STRICT_PROTOTYPES = YES;
				CLANG_WARN_SUSPICIOUS_MOVE = YES;
				CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
				CLANG_WARN_UNREACHABLE_CODE = YES;
				CLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GCC_NO_COMMON_BLOCKS = YES;
				GCC_OPTIMIZATION_LEVEL = s;
				GCC_WARN_64_TO_32_BIT_CONVERSION = YES;
				GCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
				GCC_WARN_UNDECLARED_SELECTOR = YES;
				GCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
				GCC_WARN_UNUSED_FUNCTION = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SWIFT_COMPILATION_MODE = wholemodule;
				SWIFT_OPTIMIZATION_LEVEL = "-O";
				VALIDATE_PRODUCT = YES;
			}};
			name = Release;
		}};
		{config_debug_target} /* Debug */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UIRequiresFullScreen = YES;
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.trip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator macosx";
				SUPPORTS_MACCATALYST = YES;
				SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2,6";
			}};
			name = Debug;
		}};
		{config_release_target} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UIRequiresFullScreen = YES;
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPhone = "UIInterfaceOrientationPortrait UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				INFOPLIST_KEY_UISupportedInterfaceOrientations_iPad = "UIInterfaceOrientationPortrait UIInterfaceOrientationPortraitUpsideDown UIInterfaceOrientationLandscapeLeft UIInterfaceOrientationLandscapeRight";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.trip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				STRING_CATALOG_GENERATE_SYMBOLS = YES;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator macosx";
				SUPPORTS_MACCATALYST = YES;
				SUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = YES;
				MACOSX_DEPLOYMENT_TARGET = 13.0;
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2,6";
			}};
			name = Release;
		}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
		{config_list_proj} /* Build configuration list for PBXProject "XinjiangTrip" */;
		{config_list_proj} = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{config_debug_proj} /* Debug */,
				{config_release_proj} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
		{config_list_target} /* Build configuration list for PBXNativeTarget "XinjiangTrip" */;
		{config_list_target} = {{
			isa = XCConfigurationList;
			buildConfigurations = (
				{config_debug_target} /* Debug */,
				{config_release_target} /* Release */,
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = Release;
		}};
/* End XCConfigurationList section */

	}};
	rootObject = {project_id} /* Project object */;
}}
'''

with open(os.path.join(PBX_DIR, "project.pbxproj"), "w", encoding="utf-8") as f:
    f.write(project_pbx)

# 5. 生成 xcshareddata Scheme 文件，确保 Xcode 与命令行能直接识别 Scheme
shared_schemes_dir = os.path.join(PBX_DIR, "xcshareddata", "xcschemes")
os.makedirs(shared_schemes_dir, exist_ok=True)

with open("/Users/Noodles/Documents/AG_Project/ios/scheme_template.xml", "r", encoding="utf-8") as f:
    scheme_content = f.read().replace("TARGET_ID_PLACEHOLDER", target_id)

with open(os.path.join(shared_schemes_dir, "XinjiangTrip.xcscheme"), "w", encoding="utf-8") as f:
    f.write(scheme_content)

print("🎉 iOS 原生工程已成功生成至: " + IOS_DIR)

