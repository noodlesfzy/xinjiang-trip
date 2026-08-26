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
    <string>新疆自驾路书</string>
    <key>CFBundleExecutable</key>
    <string>$(EXECUTABLE_NAME)</string>
    <key>CFBundleIdentifier</key>
    <string>com.noodles.xinjiangtrip</string>
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
    <key>UILaunchScreen</key>
    <dict/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
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
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
		{app_id} /* XinjiangTrip.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = XinjiangTrip.app; sourceTree = BUILT_PRODUCTS_DIR; }};
		{swift_id}F /* XinjiangTripApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = XinjiangTripApp.swift; sourceTree = "<group>"; }};
		{html_id}F /* index.html */ = {{isa = PBXFileReference; lastKnownFileType = text.html; path = index.html; sourceTree = "<group>"; }};
		{plist_id}F /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
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
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = dwarf;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				ENABLE_TESTABILITY = YES;
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PREPROCESSOR_DEFINITIONS = (
					"DEBUG=1",
					"$(inherited)",
				);
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
				ONLY_ACTIVE_ARCH = YES;
				SDKROOT = iphoneos;
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
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				ENABLE_NS_ASSERTIONS = NO;
				ENABLE_STRICT_OBJC_MSGSEND = YES;
				GCC_OPTIMIZATION_LEVEL = s;
				IPHONEOS_DEPLOYMENT_TARGET = 16.0;
				MTL_ENABLE_DEBUG_INFO = NO;
				SDKROOT = iphoneos;
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
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "新疆自驾路书";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.xinjiangtrip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
			}};
			name = Debug;
		}};
		{config_release_target} /* Release */ = {{
			isa = XCBuildConfiguration;
			buildSettings = {{
				ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
				CODE_SIGN_STYLE = Automatic;
				CURRENT_PROJECT_VERSION = 1;
				DEVELOPMENT_TEAM = "";
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "新疆自驾路书";
				LD_RUNPATH_SEARCH_PATHS = (
					"$(inherited)",
					"@executable_path/Frameworks",
				);
				MARKETING_VERSION = 1.0.0;
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.xinjiangtrip;
				PRODUCT_NAME = "$(TARGET_NAME)";
				SDKROOT = iphoneos;
				SUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
				SWIFT_EMIT_LOC_STRINGS = YES;
				SWIFT_VERSION = 5.0;
				TARGETED_DEVICE_FAMILY = "1,2";
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

