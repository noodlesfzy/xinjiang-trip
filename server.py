#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py — 高性能多线程本地静态 Web 服务器 (支持手机局域网高并发访问)
"""

import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

DIRECTORY = "/Users/Noodles/Documents/AG_Project"
PORT = 8000

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # 简化日志输出
        pass

def run():
    # 确保绑定所有网络接口 0.0.0.0
    server_address = ("0.0.0.0", PORT)
    httpd = ThreadingHTTPServer(server_address, CustomHandler)
    print(f"🚀 Server running at http://0.0.0.0:{PORT} (Directory: {DIRECTORY})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run()
