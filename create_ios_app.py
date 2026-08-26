#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_ios_app.py — 一键构建原生 iOS Xcode 工程 (XinjiangTrip)
将 trip_mobile.html 深度打包为 100% 离线运行、支持大众点评/小红书原生 Scheme 唤起的 iOS 原生 App。
"""

import os
import re
import shutil
import subprocess
import uuid

IOS_DIR = "/Users/Noodles/Documents/AG_Project/ios"
APP_DIR = os.path.join(IOS_DIR, "XinjiangTrip")
PBX_DIR = os.path.join(IOS_DIR, "XinjiangTrip.xcodeproj")

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(PBX_DIR, exist_ok=True)

# 1. 复制最新编译的手机版路书到 App Bundle 资源目录
shutil.copy2("/Users/Noodles/Documents/AG_Project/trip_mobile.html", os.path.join(APP_DIR, "index.html"))

# 2. 生成原生 Swift 入口文件
import base64
swift_code = base64.b64decode('Ly8KLy8gIFhpbmppYW5nVHJpcEFwcC5zd2lmdAovLyAg6L6j6bih5Za1IChYaW5qaWFuZyBSb2FkIFRyaXApCi8vICBMb2NhbCBIVFRQIFNlcnZlciBBcmNoaXRlY3R1cmUgKE5XTGlzdGVuZXIgb24gbG9jYWxob3N0OjgwODgpCi8vICDlvbvlupXmkYbohLEgZmlsZTovLyDmspnnm5Llr7kgSFRUUFMg5YiH54mH5Zu+54mH55qE6Leo5Z+f6Zi75pat77yMMTAwJSDlr7npvZAgU2FmYXJpIOe6r+agh+WHhiBXZWIg546v5aKDCi8vCgppbXBvcnQgU3dpZnRVSQppbXBvcnQgV2ViS2l0CmltcG9ydCBGb3VuZGF0aW9uCmltcG9ydCBOZXR3b3JrCmltcG9ydCBDb3JlVGVsZXBob255CgpAbWFpbgpzdHJ1Y3QgWGluamlhbmdUcmlwQXBwOiBBcHAgewogICAgcHJpdmF0ZSBsZXQgbG9jYWxTZXJ2ZXIgPSBMb2NhbEhUVFBTZXJ2ZXIoKQoKICAgIGluaXQoKSB7CiAgICAgICAgLy8g5ZCv5Yqo5YaF572u5pys5Zyw6auY6YCfIEhUVFAg5pyN5Yqh5ZmoICgxMjcuMC4wLjE6ODA4OCkKICAgICAgICBsb2NhbFNlcnZlci5zdGFydCgpCiAgICAgICAgCiAgICAgICAgLy8g6Kem5Y+R5Zu96KGMIGlPUyDonILnqp3kuI7ml6Dnur/lsYDln5/nvZHmjojmnYMKICAgICAgICBsZXQgY2VsbHVsYXJEYXRhID0gQ1RDZWxsdWxhckRhdGEoKQogICAgICAgIGNlbGx1bGFyRGF0YS5jZWxsdWxhckRhdGFSZXN0cmljdGlvbkRpZFVwZGF0ZU5vdGlmaWVyID0geyBfIGluIH0KICAgIH0KCiAgICB2YXIgYm9keTogc29tZSBTY2VuZSB7CiAgICAgICAgV2luZG93R3JvdXAgewogICAgICAgICAgICBDb250ZW50VmlldygpCiAgICAgICAgICAgICAgICAucHJlZmVycmVkQ29sb3JTY2hlbWUoLmRhcmspCiAgICAgICAgfQogICAgfQp9CgovLyBNQVJLOiAtIExvY2FsSFRUUFNlcnZlciAo5Z+65LqOIEFwcGxlIOWOn+eUnyBOZXR3b3JrLmZyYW1ld29yayBOV0xpc3RlbmVyKQpjbGFzcyBMb2NhbEhUVFBTZXJ2ZXIgewogICAgcHJpdmF0ZSB2YXIgbGlzdGVuZXI6IE5XTGlzdGVuZXI/CiAgICBsZXQgcG9ydDogTldFbmRwb2ludC5Qb3J0ID0gODA4OAoKICAgIGZ1bmMgc3RhcnQoKSB7CiAgICAgICAgZG8gewogICAgICAgICAgICBsZXQgcGFyYW1zID0gTldQYXJhbWV0ZXJzLnRjcAogICAgICAgICAgICBsaXN0ZW5lciA9IHRyeSBOV0xpc3RlbmVyKHVzaW5nOiBwYXJhbXMsIG9uOiBwb3J0KQogICAgICAgICAgICBsaXN0ZW5lcj8ubmV3Q29ubmVjdGlvbkhhbmRsZXIgPSB7IFt3ZWFrIHNlbGZdIGNvbm5lY3Rpb24gaW4KICAgICAgICAgICAgICAgIHNlbGY/LmhhbmRsZUNvbm5lY3Rpb24oY29ubmVjdGlvbikKICAgICAgICAgICAgfQogICAgICAgICAgICBsaXN0ZW5lcj8uc3RhcnQocXVldWU6IC5nbG9iYWwocW9zOiAudXNlckluaXRpYXRlZCkpCiAgICAgICAgICAgIHByaW50KCLwn5qAIOacrOWcsOaegemAnyBIVFRQIOacjeWKoeWZqOW3suWcqCBodHRwOi8vMTI3LjAuMC4xOlwocG9ydCkvIOWQr+WKqCIpCiAgICAgICAgfSBjYXRjaCB7CiAgICAgICAgICAgIHByaW50KCLinYwg5pys5Zyw5pyN5Yqh5Zmo5ZCv5Yqo5aSx6LSlOiBcKGVycm9yKSIpCiAgICAgICAgfQogICAgfQoKICAgIHByaXZhdGUgZnVuYyBoYW5kbGVDb25uZWN0aW9uKF8gY29ubmVjdGlvbjogTldDb25uZWN0aW9uKSB7CiAgICAgICAgY29ubmVjdGlvbi5zdGFydChxdWV1ZTogLmdsb2JhbChxb3M6IC51c2VySW5pdGlhdGVkKSkKICAgICAgICBjb25uZWN0aW9uLnJlY2VpdmUobWluaW11bUluY29tcGxldGVMZW5ndGg6IDEsIG1heGltdW1MZW5ndGg6IDY1NTM2KSB7IFt3ZWFrIHNlbGZdIGRhdGEsIF8sIF8sIGVycm9yIGluCiAgICAgICAgICAgIGd1YXJkIGxldCBzZWxmID0gc2VsZiwgbGV0IGRhdGEgPSBkYXRhLCBsZXQgcmVxU3RyID0gU3RyaW5nKGRhdGE6IGRhdGEsIGVuY29kaW5nOiAudXRmOCkgZWxzZSB7CiAgICAgICAgICAgICAgICBjb25uZWN0aW9uLmNhbmNlbCgpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgbGV0IGxpbmVzID0gcmVxU3RyLmNvbXBvbmVudHMoc2VwYXJhdGVkQnk6ICJcclxuIikKICAgICAgICAgICAgZ3VhcmQgbGV0IGZpcnN0TGluZSA9IGxpbmVzLmZpcnN0IGVsc2UgeyBjb25uZWN0aW9uLmNhbmNlbCgpOyByZXR1cm4gfQogICAgICAgICAgICBsZXQgcGFydHMgPSBmaXJzdExpbmUuY29tcG9uZW50cyhzZXBhcmF0ZWRCeTogIiAiKQogICAgICAgICAgICBndWFyZCBwYXJ0cy5jb3VudCA+PSAyIGVsc2UgeyBjb25uZWN0aW9uLmNhbmNlbCgpOyByZXR1cm4gfQogICAgICAgICAgICB2YXIgcGF0aCA9IHBhcnRzWzFdCiAgICAgICAgICAgIGlmIHBhdGggPT0gIi8iIHx8IHBhdGguaXNFbXB0eSB7IHBhdGggPSAiL2luZGV4Lmh0bWwiIH0KICAgICAgICAgICAgaWYgbGV0IHFJZHggPSBwYXRoLmZpcnN0SW5kZXgob2Y6ICI/IikgewogICAgICAgICAgICAgICAgcGF0aCA9IFN0cmluZyhwYXRoWy4uPHFJZHhdKQogICAgICAgICAgICB9CgogICAgICAgICAgICBsZXQgZmlsZW5hbWUgPSAocGF0aCBhcyBOU1N0cmluZykubGFzdFBhdGhDb21wb25lbnQKICAgICAgICAgICAgbGV0IGV4dCA9IChmaWxlbmFtZSBhcyBOU1N0cmluZykucGF0aEV4dGVuc2lvbgogICAgICAgICAgICBsZXQgbmFtZSA9IChmaWxlbmFtZSBhcyBOU1N0cmluZykuZGVsZXRpbmdQYXRoRXh0ZW5zaW9uCgogICAgICAgICAgICB2YXIgbWltZSA9ICJ0ZXh0L2h0bWw7IGNoYXJzZXQ9dXRmLTgiCiAgICAgICAgICAgIGlmIGV4dCA9PSAianMiIHsgbWltZSA9ICJhcHBsaWNhdGlvbi9qYXZhc2NyaXB0IiB9CiAgICAgICAgICAgIGVsc2UgaWYgZXh0ID09ICJjc3MiIHsgbWltZSA9ICJ0ZXh0L2NzcyIgfQogICAgICAgICAgICBlbHNlIGlmIGV4dCA9PSAicG5nIiB7IG1pbWUgPSAiaW1hZ2UvcG5nIiB9CiAgICAgICAgICAgIGVsc2UgaWYgZXh0ID09ICJqcGciIHx8IGV4dCA9PSAianBlZyIgeyBtaW1lID0gImltYWdlL2pwZWciIH0KICAgICAgICAgICAgZWxzZSBpZiBleHQgPT0gImpzb24iIHsgbWltZSA9ICJhcHBsaWNhdGlvbi9qc29uIiB9CgogICAgICAgICAgICBpZiBsZXQgZmlsZVBhdGggPSBCdW5kbGUubWFpbi5wYXRoKGZvclJlc291cmNlOiBuYW1lLCBvZlR5cGU6IGV4dC5pc0VtcHR5ID8gbmlsIDogZXh0KSwKICAgICAgICAgICAgICAgbGV0IGZpbGVEYXRhID0gdHJ5PyBEYXRhKGNvbnRlbnRzT2Y6IFVSTChmaWxlVVJMV2l0aFBhdGg6IGZpbGVQYXRoKSkgewogICAgICAgICAgICAgICAgbGV0IGhlYWRlciA9ICJIVFRQLzEuMSAyMDAgT0tcclxuQ29udGVudC1UeXBlOiBcKG1pbWUpXHJcbkNvbnRlbnQtTGVuZ3RoOiBcKGZpbGVEYXRhLmNvdW50KVxyXG5BY2Nlc3MtQ29udHJvbC1BbGxvdy1PcmlnaW46ICpcclxuQ2FjaGUtQ29udHJvbDogbm8tY2FjaGVcclxuQ29ubmVjdGlvbjogY2xvc2VcclxuXHJcbiIKCiAgICAgICAgICAgICAgICB2YXIgdG90YWxEYXRhID0gaGVhZGVyLmRhdGEodXNpbmc6IC51dGY4KSEKICAgICAgICAgICAgICAgIHRvdGFsRGF0YS5hcHBlbmQoZmlsZURhdGEpCiAgICAgICAgICAgICAgICBjb25uZWN0aW9uLnNlbmQoY29udGVudDogdG90YWxEYXRhLCBjb21wbGV0aW9uOiAuY29udGVudFByb2Nlc3NlZCh7IF8gaW4KICAgICAgICAgICAgICAgICAgICBjb25uZWN0aW9uLmNhbmNlbCgpCiAgICAgICAgICAgICAgICB9KSkKICAgICAgICAgICAgfSBlbHNlIHsKICAgICAgICAgICAgICAgIGxldCBub3RGb3VuZCA9ICJIVFRQLzEuMSA0MDQgTm90IEZvdW5kXHJcbkNvbnRlbnQtTGVuZ3RoOiAwXHJcbkNvbm5lY3Rpb246IGNsb3NlXHJcblxyXG4iCiAgICAgICAgICAgICAgICBjb25uZWN0aW9uLnNlbmQoY29udGVudDogbm90Rm91bmQuZGF0YSh1c2luZzogLnV0ZjgpISwgY29tcGxldGlvbjogLmNvbnRlbnRQcm9jZXNzZWQoeyBfIGluCiAgICAgICAgICAgICAgICAgICAgY29ubmVjdGlvbi5jYW5jZWwoKQogICAgICAgICAgICAgICAgfSkpCiAgICAgICAgICAgIH0KICAgICAgICB9CiAgICB9Cn0KCi8vIE1BUks6IC0gQ29udGVudFZpZXcKc3RydWN0IENvbnRlbnRWaWV3OiBWaWV3IHsKICAgIHZhciBib2R5OiBzb21lIFZpZXcgewogICAgICAgIFpTdGFjayB7CiAgICAgICAgICAgIENvbG9yKGhleDogIiMwZjE3MmEiKS5pZ25vcmVzU2FmZUFyZWEoKQogICAgICAgICAgICBIeWJyaWRUcmlwV2ViVmlldygpCiAgICAgICAgICAgICAgICAuZWRnZXNJZ25vcmluZ1NhZmVBcmVhKC5hbGwpCiAgICAgICAgfQogICAgfQp9CgovLyBNQVJLOiAtIEh5YnJpZFRyaXBXZWJWaWV3CnN0cnVjdCBIeWJyaWRUcmlwV2ViVmlldzogVUlWaWV3UmVwcmVzZW50YWJsZSB7CiAgICBmdW5jIG1ha2VVSVZpZXcoY29udGV4dDogQ29udGV4dCkgLT4gV0tXZWJWaWV3IHsKICAgICAgICBsZXQgY29uZmlnID0gV0tXZWJWaWV3Q29uZmlndXJhdGlvbigpCiAgICAgICAgY29uZmlnLmFsbG93c0lubGluZU1lZGlhUGxheWJhY2sgPSB0cnVlCgogICAgICAgIGxldCB3ZWJWaWV3ID0gV0tXZWJWaWV3KGZyYW1lOiAuemVybywgY29uZmlndXJhdGlvbjogY29uZmlnKQogICAgICAgIHdlYlZpZXcubmF2aWdhdGlvbkRlbGVnYXRlID0gY29udGV4dC5jb29yZGluYXRvcgogICAgICAgIHdlYlZpZXcuaXNPcGFxdWUgPSBmYWxzZQogICAgICAgIHdlYlZpZXcuYmFja2dyb3VuZENvbG9yID0gVUlDb2xvcihyZWQ6IDAuMDYsIGdyZWVuOiAwLjA5LCBibHVlOiAwLjE2LCBhbHBoYTogMS4wKQogICAgICAgIHdlYlZpZXcuc2Nyb2xsVmlldy5iYWNrZ3JvdW5kQ29sb3IgPSBVSUNvbG9yKHJlZDogMC4wNiwgZ3JlZW46IDAuMDksIGJsdWU6IDAuMTYsIGFscGhhOiAxLjApCiAgICAgICAgd2ViVmlldy5zY3JvbGxWaWV3LmNvbnRlbnRJbnNldEFkanVzdG1lbnRCZWhhdmlvciA9IC5uZXZlcgogICAgICAgIGlmICNhdmFpbGFibGUoaU9TIDE2LjQsICopIHsKICAgICAgICAgICAgd2ViVmlldy5pc0luc3BlY3RhYmxlID0gdHJ1ZQogICAgICAgIH0KCiAgICAgICAgY29udGV4dC5jb29yZGluYXRvci53ZWJWaWV3ID0gd2ViVmlldwogICAgICAgIGNvbnRleHQuY29vcmRpbmF0b3IubG9hZEFwcCgpCiAgICAgICAgcmV0dXJuIHdlYlZpZXcKICAgIH0KCiAgICBmdW5jIHVwZGF0ZVVJVmlldyhfIHVpVmlldzogV0tXZWJWaWV3LCBjb250ZXh0OiBDb250ZXh0KSB7fQogICAgZnVuYyBtYWtlQ29vcmRpbmF0b3IoKSAtPiBDb29yZGluYXRvciB7IENvb3JkaW5hdG9yKCkgfQoKICAgIGNsYXNzIENvb3JkaW5hdG9yOiBOU09iamVjdCwgV0tOYXZpZ2F0aW9uRGVsZWdhdGUgewogICAgICAgIHdlYWsgdmFyIHdlYlZpZXc6IFdLV2ViVmlldz8KCiAgICAgICAgZnVuYyBsb2FkQXBwKCkgewogICAgICAgICAgICAvLyDnqI3nrYkgMTUwbXMg56Gu5L+d5pys5Zyw5pyN5Yqh5Zmo56uv5Y+j5bCx57uq5ZCO5Yqg6L29CiAgICAgICAgICAgIERpc3BhdGNoUXVldWUubWFpbi5hc3luY0FmdGVyKGRlYWRsaW5lOiAubm93KCkgKyAwLjE1KSB7IFt3ZWFrIHNlbGZdIGluCiAgICAgICAgICAgICAgICBpZiBsZXQgdXJsID0gVVJMKHN0cmluZzogImh0dHA6Ly8xMjcuMC4wLjE6ODA4OC9pbmRleC5odG1sIikgewogICAgICAgICAgICAgICAgICAgIGxldCByZXEgPSBVUkxSZXF1ZXN0KHVybDogdXJsLCBjYWNoZVBvbGljeTogLnJlbG9hZElnbm9yaW5nTG9jYWxDYWNoZURhdGEsIHRpbWVvdXRJbnRlcnZhbDogMTApCiAgICAgICAgICAgICAgICAgICAgc2VsZj8ud2ViVmlldz8ubG9hZChyZXEpCiAgICAgICAgICAgICAgICAgICAgcHJpbnQoIuKchSDot6/kuablt7LpgJrov4fmnKzlnLAgSFRUUCDmnI3liqHlmaggKGh0dHA6Ly8xMjcuMC4wLjE6ODA4OC9pbmRleC5odG1sKSDliqDovb0iKQogICAgICAgICAgICAgICAgfQogICAgICAgICAgICB9CiAgICAgICAgfQoKICAgICAgICBmdW5jIHdlYlZpZXcoXyB3ZWJWaWV3OiBXS1dlYlZpZXcsIGRlY2lkZVBvbGljeUZvciBuYXY6IFdLTmF2aWdhdGlvbkFjdGlvbiwKICAgICAgICAgICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyOiBAZXNjYXBpbmcgKFdLTmF2aWdhdGlvbkFjdGlvblBvbGljeSkgLT4gVm9pZCkgewogICAgICAgICAgICBndWFyZCBsZXQgdXJsID0gbmF2LnJlcXVlc3QudXJsIGVsc2UgeyBkZWNpc2lvbkhhbmRsZXIoLmFsbG93KTsgcmV0dXJuIH0KICAgICAgICAgICAgbGV0IHNjaGVtZSA9IHVybC5zY2hlbWU/Lmxvd2VyY2FzZWQoKSA/PyAiIgoKICAgICAgICAgICAgLy8g5pys5ZywIEhUVFAg5pyN5Yqh5Zmo5LiO5YaF6YOo5a+86Iiq55u05o6l5pS+6KGMCiAgICAgICAgICAgIGlmIGxldCBob3N0ID0gdXJsLmhvc3Q/Lmxvd2VyY2FzZWQoKSwgaG9zdCA9PSAiMTI3LjAuMC4xIiB8fCBob3N0ID09ICJsb2NhbGhvc3QiIHsKICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlciguYWxsb3cpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgLy8g56ys5LiJ5pa5IEFwcCBTY2hlbWUgKOWkp+S8l+eCueivhCAvIOWwj+e6ouS5piAvIOmrmOW+t+WcsOWbviAvIOeUteivnSAvIOmCruS7tikg5Y6f55Sf5ZSk6LW3CiAgICAgICAgICAgIGlmIFsiZGlhbnBpbmciLCJ4aHNkaXNjb3ZlciIsImlvc2FtYXAiLCJiYWlkdW1hcCIsInRlbCIsIm1haWx0byJdLmNvbnRhaW5zKHNjaGVtZSkgewogICAgICAgICAgICAgICAgaWYgVUlBcHBsaWNhdGlvbi5zaGFyZWQuY2FuT3BlblVSTCh1cmwpIHsgVUlBcHBsaWNhdGlvbi5zaGFyZWQub3Blbih1cmwpIH0KICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlciguY2FuY2VsKQogICAgICAgICAgICAgICAgcmV0dXJuCiAgICAgICAgICAgIH0KCiAgICAgICAgICAgIC8vIOmrmOW+t+WvvOiIquWklumDqOmTvuaOpQogICAgICAgICAgICBpZiB1cmwuYWJzb2x1dGVTdHJpbmcuY29udGFpbnMoInVyaS5hbWFwLmNvbS9uYXZpZ2F0aW9uIikgewogICAgICAgICAgICAgICAgVUlBcHBsaWNhdGlvbi5zaGFyZWQub3Blbih1cmwpCiAgICAgICAgICAgICAgICBkZWNpc2lvbkhhbmRsZXIoLmNhbmNlbCkKICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICB9CgogICAgICAgICAgICAvLyDlpoLmnpzkuI3mmK/nlKjmiLfkuLvliqjngrnlh7vnmoTlpJbpk77vvIjkvovlpoLpobXpnaLlj5HotbfnmoTnk6bniYflm77niYfjgIFmZXRjaOOAgUFQSe+8ie+8jOWFqOmDqOaUvuihjAogICAgICAgICAgICBpZiBuYXYubmF2aWdhdGlvblR5cGUgIT0gLmxpbmtBY3RpdmF0ZWQgewogICAgICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyKC5hbGxvdykKICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICB9CgogICAgICAgICAgICAvLyDnlKjmiLfngrnlh7vnmoTlhbbku5blpJbpg6jnvZHpobXpk77mjqXvvIzosIPnlKjns7vnu58gU2FmYXJpIOaJk+W8gAogICAgICAgICAgICBpZiBzY2hlbWUgPT0gImh0dHAiIHx8IHNjaGVtZSA9PSAiaHR0cHMiIHsKICAgICAgICAgICAgICAgIFVJQXBwbGljYXRpb24uc2hhcmVkLm9wZW4odXJsKQogICAgICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyKC5jYW5jZWwpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQogICAgICAgICAgICBkZWNpc2lvbkhhbmRsZXIoLmFsbG93KQogICAgICAgIH0KICAgIH0KfQoKZXh0ZW5zaW9uIENvbG9yIHsKICAgIGluaXQoaGV4OiBTdHJpbmcpIHsKICAgICAgICBsZXQgaGV4ID0gaGV4LnRyaW1taW5nQ2hhcmFjdGVycyhpbjogQ2hhcmFjdGVyU2V0LmFscGhhbnVtZXJpY3MuaW52ZXJ0ZWQpCiAgICAgICAgdmFyIGludDogVUludDY0ID0gMAogICAgICAgIFNjYW5uZXIoc3RyaW5nOiBoZXgpLnNjYW5IZXhJbnQ2NCgmaW50KQogICAgICAgIGxldCBhLCByLCBnLCBiOiBVSW50NjQKICAgICAgICBzd2l0Y2ggaGV4LmNvdW50IHsKICAgICAgICBjYXNlIDM6ICAoYSxyLGcsYikgPSAoMjU1LChpbnQ+PjgpKjE3LChpbnQ+PjQgJiAweEYpKjE3LChpbnQgJiAweEYpKjE3KQogICAgICAgIGNhc2UgNjogIChhLHIsZyxiKSA9ICgyNTUsaW50Pj4xNixpbnQ+PjggJiAweEZGLGludCAmIDB4RkYpCiAgICAgICAgY2FzZSA4OiAgKGEscixnLGIpID0gKGludD4+MjQsaW50Pj4xNiAmIDB4RkYsaW50Pj44ICYgMHhGRixpbnQgJiAweEZGKQogICAgICAgIGRlZmF1bHQ6IChhLHIsZyxiKSA9ICgyNTUsMCwwLDApCiAgICAgICAgfQogICAgICAgIHNlbGYuaW5pdCguc1JHQixyZWQ6RG91YmxlKHIpLzI1NSxncmVlbjpEb3VibGUoZykvMjU1LGJsdWU6RG91YmxlKGIpLzI1NSxvcGFjaXR5OkRvdWJsZShhKS8yNTUpCiAgICB9Cn0K').decode('utf-8')

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
        <key>NSAllowsArbitraryLoadsInWebContent</key>
        <true/>
        <key>NSAllowsLocalNetworking</key>
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
    <key>UILaunchScreen</key>
    <dict>
        <key>UIColorName</key>
        <string></string>
        <key>UIImageName</key>
        <string></string>
    </dict>
    <key>UIViewControllerBasedStatusBarAppearance</key>
    <false/>
</dict>
</plist>
'''

with open(os.path.join(APP_DIR, "Info.plist"), "w", encoding="utf-8") as f:
    f.write(info_plist)

# 4. 自动检测并永久锁定当前开发者的 Apple Team ID (解决每次重新选择 Team 报错)
def detect_development_team():
    try:
        out = subprocess.check_output(["defaults", "read", "com.apple.dt.Xcode", "IDEProvisioningTeams"]).decode("utf-8", errors="ignore")
        m = re.search(r'teamID\s*=\s*"?([A-Z0-9]{10})"?', out)
        if m and m.group(1):
            return m.group(1)
    except Exception:
        pass
    pbx_path = os.path.join(PBX_DIR, "project.pbxproj")
    if os.path.exists(pbx_path):
        try:
            with open(pbx_path, "r", encoding="utf-8") as f:
                content = f.read()
                m = re.search(r'DEVELOPMENT_TEAM = "??([A-Z0-9]{10})"??;', content)
                if m and m.group(1):
                    return m.group(1)
        except Exception:
            pass
    return "D2953L7MB6"

team_id = detect_development_team()

# 5. 生成标准 PBXProject 文件 (Xcode 项目配置文件)
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
						DevelopmentTeam = {team_id};
						ProvisioningStyle = Automatic;
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
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
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
				DEVELOPMENT_TEAM = {team_id};
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
				ASSETCATALOG_COMPILER_GENERATE_ASSET_SYMBOLS = YES;
				ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
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
				DEVELOPMENT_TEAM = {team_id};
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
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
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
				DEVELOPMENT_TEAM = {team_id};
				ENABLE_USER_SCRIPT_SANDBOXING = YES;
				GENERATE_INFOPLIST_FILE = NO;
				INFOPLIST_FILE = XinjiangTrip/Info.plist;
				INFOPLIST_KEY_CFBundleDisplayName = "辣鸡喵";
				INFOPLIST_KEY_UILaunchScreen_Generation = YES;
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

