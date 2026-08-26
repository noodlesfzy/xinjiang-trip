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
swift_code = base64.b64decode('Ly8KLy8gIFhpbmppYW5nVHJpcEFwcC5zd2lmdAovLyAg6L6j6bih5Za1IChYaW5qaWFuZyBSb2FkIFRyaXApCi8vICBMb2NhbCBIVFRQIFNlcnZlciArIE5hdGl2ZSBUaWxlIFJlbGF5ICsgRGV0YWlsZWQgRGlhZ25vc3RpYyBMb2dnaW5nCi8vCgppbXBvcnQgU3dpZnRVSQppbXBvcnQgV2ViS2l0CmltcG9ydCBGb3VuZGF0aW9uCmltcG9ydCBOZXR3b3JrCmltcG9ydCBDb3JlVGVsZXBob255CgpAbWFpbgpzdHJ1Y3QgWGluamlhbmdUcmlwQXBwOiBBcHAgewogICAgcHJpdmF0ZSBsZXQgbG9jYWxTZXJ2ZXIgPSBMb2NhbEhUVFBTZXJ2ZXIoKQoKICAgIGluaXQoKSB7CiAgICAgICAgbG9jYWxTZXJ2ZXIuc3RhcnQoKQogICAgICAgIAogICAgICAgIGxldCBjZWxsdWxhckRhdGEgPSBDVENlbGx1bGFyRGF0YSgpCiAgICAgICAgY2VsbHVsYXJEYXRhLmNlbGx1bGFyRGF0YVJlc3RyaWN0aW9uRGlkVXBkYXRlTm90aWZpZXIgPSB7IHN0YXRlIGluCiAgICAgICAgICAgIHByaW50KCLwn5O2IENlbGx1bGFyIERhdGEgU3RhdGU6IFwoc3RhdGUucmF3VmFsdWUpIikKICAgICAgICB9CiAgICB9CgogICAgdmFyIGJvZHk6IHNvbWUgU2NlbmUgewogICAgICAgIFdpbmRvd0dyb3VwIHsKICAgICAgICAgICAgQ29udGVudFZpZXcoKQogICAgICAgICAgICAgICAgLnByZWZlcnJlZENvbG9yU2NoZW1lKC5kYXJrKQogICAgICAgIH0KICAgIH0KfQoKLy8gTUFSSzogLSBMb2NhbEhUVFBTZXJ2ZXIKY2xhc3MgTG9jYWxIVFRQU2VydmVyIHsKICAgIHByaXZhdGUgdmFyIGxpc3RlbmVyOiBOV0xpc3RlbmVyPwogICAgbGV0IHBvcnQ6IE5XRW5kcG9pbnQuUG9ydCA9IDgwODgKICAgIAogICAgcHJpdmF0ZSBsZXQgdGlsZVNlc3Npb246IFVSTFNlc3Npb24gPSB7CiAgICAgICAgbGV0IGNmZyA9IFVSTFNlc3Npb25Db25maWd1cmF0aW9uLmRlZmF1bHQKICAgICAgICBjZmcudGltZW91dEludGVydmFsRm9yUmVxdWVzdCA9IDEwCiAgICAgICAgY2ZnLnRpbWVvdXRJbnRlcnZhbEZvclJlc291cmNlID0gMTUKICAgICAgICBjZmcucmVxdWVzdENhY2hlUG9saWN5ID0gLnJldHVybkNhY2hlRGF0YUVsc2VMb2FkCiAgICAgICAgY2ZnLnVybENhY2hlID0gVVJMQ2FjaGUobWVtb3J5Q2FwYWNpdHk6IDY0KjEwMjQqMTAyNCwgZGlza0NhcGFjaXR5OiAyNTYqMTAyNCoxMDI0KQogICAgICAgIHJldHVybiBVUkxTZXNzaW9uKGNvbmZpZ3VyYXRpb246IGNmZykKICAgIH0oKQoKICAgIGZ1bmMgc3RhcnQoKSB7CiAgICAgICAgZG8gewogICAgICAgICAgICBsZXQgcGFyYW1zID0gTldQYXJhbWV0ZXJzLnRjcAogICAgICAgICAgICBsaXN0ZW5lciA9IHRyeSBOV0xpc3RlbmVyKHVzaW5nOiBwYXJhbXMsIG9uOiBwb3J0KQogICAgICAgICAgICBsaXN0ZW5lcj8ubmV3Q29ubmVjdGlvbkhhbmRsZXIgPSB7IFt3ZWFrIHNlbGZdIGNvbm5lY3Rpb24gaW4KICAgICAgICAgICAgICAgIHNlbGY/LmhhbmRsZUNvbm5lY3Rpb24oY29ubmVjdGlvbikKICAgICAgICAgICAgfQogICAgICAgICAgICBsaXN0ZW5lcj8uc3RhcnQocXVldWU6IC5nbG9iYWwocW9zOiAudXNlckluaXRpYXRlZCkpCiAgICAgICAgICAgIHByaW50KCLwn5qAIOacrOWcsOacjeWKoeWZqOW3suWcqOerr+WPoyBcKHBvcnQpIOWQr+WKqCIpCiAgICAgICAgfSBjYXRjaCB7CiAgICAgICAgICAgIHByaW50KCLinYwg5pys5Zyw5pyN5Yqh5Zmo5ZCv5Yqo5aSx6LSlOiBcKGVycm9yKSIpCiAgICAgICAgfQogICAgfQoKICAgIHByaXZhdGUgZnVuYyBoYW5kbGVDb25uZWN0aW9uKF8gY29ubmVjdGlvbjogTldDb25uZWN0aW9uKSB7CiAgICAgICAgY29ubmVjdGlvbi5zdGFydChxdWV1ZTogLmdsb2JhbChxb3M6IC51c2VySW5pdGlhdGVkKSkKICAgICAgICBjb25uZWN0aW9uLnJlY2VpdmUobWluaW11bUluY29tcGxldGVMZW5ndGg6IDEsIG1heGltdW1MZW5ndGg6IDY1NTM2KSB7IFt3ZWFrIHNlbGZdIGRhdGEsIF8sIF8sIGVycm9yIGluCiAgICAgICAgICAgIGd1YXJkIGxldCBzZWxmID0gc2VsZiwgbGV0IGRhdGEgPSBkYXRhLCBsZXQgcmVxU3RyID0gU3RyaW5nKGRhdGE6IGRhdGEsIGVuY29kaW5nOiAudXRmOCkgZWxzZSB7CiAgICAgICAgICAgICAgICBjb25uZWN0aW9uLmNhbmNlbCgpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgbGV0IGxpbmVzID0gcmVxU3RyLmNvbXBvbmVudHMoc2VwYXJhdGVkQnk6ICJcclxuIikKICAgICAgICAgICAgZ3VhcmQgbGV0IGZpcnN0TGluZSA9IGxpbmVzLmZpcnN0IGVsc2UgeyBjb25uZWN0aW9uLmNhbmNlbCgpOyByZXR1cm4gfQogICAgICAgICAgICBsZXQgcGFydHMgPSBmaXJzdExpbmUuY29tcG9uZW50cyhzZXBhcmF0ZWRCeTogIiAiKQogICAgICAgICAgICBndWFyZCBwYXJ0cy5jb3VudCA+PSAyIGVsc2UgeyBjb25uZWN0aW9uLmNhbmNlbCgpOyByZXR1cm4gfQogICAgICAgICAgICBsZXQgZnVsbFBhdGggPSBwYXJ0c1sxXQogICAgICAgICAgICAKICAgICAgICAgICAgdmFyIHBhdGggPSBmdWxsUGF0aAogICAgICAgICAgICB2YXIgcXVlcnkgPSAiIgogICAgICAgICAgICBpZiBsZXQgcUlkeCA9IGZ1bGxQYXRoLmZpcnN0SW5kZXgob2Y6ICI/IikgewogICAgICAgICAgICAgICAgcGF0aCA9IFN0cmluZyhmdWxsUGF0aFsuLjxxSWR4XSkKICAgICAgICAgICAgICAgIHF1ZXJ5ID0gU3RyaW5nKGZ1bGxQYXRoW2Z1bGxQYXRoLmluZGV4KGFmdGVyOiBxSWR4KS4uLl0pCiAgICAgICAgICAgIH0KICAgICAgICAgICAgaWYgcGF0aCA9PSAiLyIgfHwgcGF0aC5pc0VtcHR5IHsgcGF0aCA9ICIvaW5kZXguaHRtbCIgfQoKICAgICAgICAgICAgLy8g4pSA4pSAIOi3r+W+hCAx77ya55Om54mH5Lit57un5LiO6LCD6K+VIOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgOKUgAogICAgICAgICAgICBpZiBwYXRoID09ICIvbWFwdGlsZSIgewogICAgICAgICAgICAgICAgbGV0IHBhcmFtcyA9IHNlbGYucGFyc2VRdWVyeShxdWVyeSkKICAgICAgICAgICAgICAgIGxldCBzID0gcGFyYW1zWyJzIl0gPz8gIjEiCiAgICAgICAgICAgICAgICBsZXQgc3R5bGUgPSBwYXJhbXNbInN0eWxlIl0gPz8gIjciCiAgICAgICAgICAgICAgICBsZXQgeCA9IHBhcmFtc1sieCJdID8/ICIwIgogICAgICAgICAgICAgICAgbGV0IHkgPSBwYXJhbXNbInkiXSA/PyAiMCIKICAgICAgICAgICAgICAgIGxldCB6ID0gcGFyYW1zWyJ6Il0gPz8gIjAiCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgIGxldCBnYW9kZVVSTFN0ciA9ICJodHRwczovL3dwcmQwXChzKS5pcy5hdXRvbmF2aS5jb20vYXBwbWFwdGlsZT9sYW5nPXpoX2NuJnNpemU9MSZzY2FsZT0xJnN0eWxlPVwoc3R5bGUpJng9XCh4KSZ5PVwoeSkmej1cKHopIgogICAgICAgICAgICAgICAgZ3VhcmQgbGV0IGdhb2RlVVJMID0gVVJMKHN0cmluZzogZ2FvZGVVUkxTdHIpIGVsc2UgewogICAgICAgICAgICAgICAgICAgIHNlbGYuc2VuZE5vdEZvdW5kKGNvbm5lY3Rpb24sIHJlYXNvbjogIkJhZCBVUkwiKQogICAgICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICAgICAgfQogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICB2YXIgcmVxID0gVVJMUmVxdWVzdCh1cmw6IGdhb2RlVVJMLCBjYWNoZVBvbGljeTogLnJldHVybkNhY2hlRGF0YUVsc2VMb2FkLCB0aW1lb3V0SW50ZXJ2YWw6IDgpCiAgICAgICAgICAgICAgICByZXEuc2V0VmFsdWUoIk1vemlsbGEvNS4wIChpUGhvbmU7IENQVSBpUGhvbmUgT1MgMTdfMCBsaWtlIE1hYyBPUyBYKSIsIGZvckhUVFBIZWFkZXJGaWVsZDogIlVzZXItQWdlbnQiKQogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICBzZWxmLnRpbGVTZXNzaW9uLmRhdGFUYXNrKHdpdGg6IHJlcSkgeyB0aWxlRGF0YSwgcmVzcCwgZXJyIGluCiAgICAgICAgICAgICAgICAgICAgaWYgbGV0IGVyciA9IGVyciB7CiAgICAgICAgICAgICAgICAgICAgICAgIHByaW50KCLinYwg55Om54mH5LiL6L295aSx6LSlIFtcKHopL1woeCkvXCh5KV06IFwoZXJyLmxvY2FsaXplZERlc2NyaXB0aW9uKSIpCiAgICAgICAgICAgICAgICAgICAgICAgIHNlbGYuc2VuZE5vdEZvdW5kKGNvbm5lY3Rpb24sIHJlYXNvbjogZXJyLmxvY2FsaXplZERlc2NyaXB0aW9uKQogICAgICAgICAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgICAgICAgICB9CiAgICAgICAgICAgICAgICAgICAgZ3VhcmQgbGV0IHRpbGVEYXRhID0gdGlsZURhdGEsICF0aWxlRGF0YS5pc0VtcHR5IGVsc2UgewogICAgICAgICAgICAgICAgICAgICAgICBwcmludCgi4p2MIOeTpueJh+aVsOaNruS4uuepuiBbXCh6KS9cKHgpL1woeSldIikKICAgICAgICAgICAgICAgICAgICAgICAgc2VsZi5zZW5kTm90Rm91bmQoY29ubmVjdGlvbiwgcmVhc29uOiAiRW1wdHkgZGF0YSIpCiAgICAgICAgICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICBsZXQgaGVhZGVyID0gIkhUVFAvMS4xIDIwMCBPS1xyXG5Db250ZW50LVR5cGU6IGltYWdlL3BuZ1xyXG5Db250ZW50LUxlbmd0aDogXCh0aWxlRGF0YS5jb3VudClcclxuQWNjZXNzLUNvbnRyb2wtQWxsb3ctT3JpZ2luOiAqXHJcbkNhY2hlLUNvbnRyb2w6IHB1YmxpYywgbWF4LWFnZT04NjQwMFxyXG5Db25uZWN0aW9uOiBjbG9zZVxyXG5cclxuIgogICAgICAgICAgICAgICAgICAgIHZhciB0b3RhbCA9IGhlYWRlci5kYXRhKHVzaW5nOiAudXRmOCkhCiAgICAgICAgICAgICAgICAgICAgdG90YWwuYXBwZW5kKHRpbGVEYXRhKQogICAgICAgICAgICAgICAgICAgIGNvbm5lY3Rpb24uc2VuZChjb250ZW50OiB0b3RhbCwgY29tcGxldGlvbjogLmNvbnRlbnRQcm9jZXNzZWQoeyBfIGluCiAgICAgICAgICAgICAgICAgICAgICAgIGNvbm5lY3Rpb24uY2FuY2VsKCkKICAgICAgICAgICAgICAgICAgICB9KSkKICAgICAgICAgICAgICAgIH0ucmVzdW1lKCkKICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICB9CgogICAgICAgICAgICAvLyDilIDilIAg6Lev5b6EIDLvvJror4rmlq3mjqXlj6MgKC9kaWFnKSDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIDilIAKICAgICAgICAgICAgaWYgcGF0aCA9PSAiL2RpYWciIHsKICAgICAgICAgICAgICAgIGxldCBkaWFnVVJMID0gVVJMKHN0cmluZzogImh0dHBzOi8vd3ByZDAxLmlzLmF1dG9uYXZpLmNvbS9hcHBtYXB0aWxlP2xhbmc9emhfY24mc2l6ZT0xJnNjYWxlPTEmc3R5bGU9NyZ4PTQ3Jnk9MjMmej02IikhCiAgICAgICAgICAgICAgICB2YXIgcmVxID0gVVJMUmVxdWVzdCh1cmw6IGRpYWdVUkwsIHRpbWVvdXRJbnRlcnZhbDogNSkKICAgICAgICAgICAgICAgIHJlcS5zZXRWYWx1ZSgiTW96aWxsYS81LjAgKGlQaG9uZTsgQ1BVIGlQaG9uZSBPUyAxN18wIGxpa2UgTWFjIE9TIFgpIiwgZm9ySFRUUEhlYWRlckZpZWxkOiAiVXNlci1BZ2VudCIpCiAgICAgICAgICAgICAgICBzZWxmLnRpbGVTZXNzaW9uLmRhdGFUYXNrKHdpdGg6IHJlcSkgeyBkLCByLCBlIGluCiAgICAgICAgICAgICAgICAgICAgbGV0IHN0YXR1cyA9IChyIGFzPyBIVFRQVVJMUmVzcG9uc2UpPy5zdGF0dXNDb2RlID8/IDAKICAgICAgICAgICAgICAgICAgICBsZXQgcmVzSlNPTiA9ICJ7XCJodHRwX3N0YXR1c1wiOiBcKHN0YXR1cyksIFwiZGF0YV9ieXRlc1wiOiBcKGQ/LmNvdW50ID8/IDApLCBcImVycm9yXCI6IFwiXChlPy5sb2NhbGl6ZWREZXNjcmlwdGlvbiA/PyAibm9uZSIpXCJ9IgogICAgICAgICAgICAgICAgICAgIGxldCBoZWFkZXIgPSAiSFRUUC8xLjEgMjAwIE9LXHJcbkNvbnRlbnQtVHlwZTogYXBwbGljYXRpb24vanNvbjsgY2hhcnNldD11dGYtOFxyXG5BY2Nlc3MtQ29udHJvbC1BbGxvdy1PcmlnaW46ICpcclxuQ29ubmVjdGlvbjogY2xvc2VcclxuXHJcbiIKICAgICAgICAgICAgICAgICAgICB2YXIgdG90YWwgPSBoZWFkZXIuZGF0YSh1c2luZzogLnV0ZjgpIQogICAgICAgICAgICAgICAgICAgIHRvdGFsLmFwcGVuZChyZXNKU09OLmRhdGEodXNpbmc6IC51dGY4KSEpCiAgICAgICAgICAgICAgICAgICAgY29ubmVjdGlvbi5zZW5kKGNvbnRlbnQ6IHRvdGFsLCBjb21wbGV0aW9uOiAuY29udGVudFByb2Nlc3NlZCh7IF8gaW4gY29ubmVjdGlvbi5jYW5jZWwoKSB9KSkKICAgICAgICAgICAgICAgIH0ucmVzdW1lKCkKICAgICAgICAgICAgICAgIHJldHVybgogICAgICAgICAgICB9CgogICAgICAgICAgICAvLyDilIDilIAg6Lev5b6EIDPvvJrmnKzlnLDpnZnmgIHotYTmupAg4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSA4pSACiAgICAgICAgICAgIGxldCBmaWxlbmFtZSA9IChwYXRoIGFzIE5TU3RyaW5nKS5sYXN0UGF0aENvbXBvbmVudAogICAgICAgICAgICBsZXQgZXh0ID0gKGZpbGVuYW1lIGFzIE5TU3RyaW5nKS5wYXRoRXh0ZW5zaW9uCiAgICAgICAgICAgIGxldCBuYW1lID0gKGZpbGVuYW1lIGFzIE5TU3RyaW5nKS5kZWxldGluZ1BhdGhFeHRlbnNpb24KCiAgICAgICAgICAgIHZhciBtaW1lID0gInRleHQvaHRtbDsgY2hhcnNldD11dGYtOCIKICAgICAgICAgICAgaWYgZXh0ID09ICJqcyIgeyBtaW1lID0gImFwcGxpY2F0aW9uL2phdmFzY3JpcHQiIH0KICAgICAgICAgICAgZWxzZSBpZiBleHQgPT0gImNzcyIgeyBtaW1lID0gInRleHQvY3NzIiB9CiAgICAgICAgICAgIGVsc2UgaWYgZXh0ID09ICJwbmciIHsgbWltZSA9ICJpbWFnZS9wbmciIH0KICAgICAgICAgICAgZWxzZSBpZiBleHQgPT0gImpwZyIgfHwgZXh0ID09ICJqcGVnIiB7IG1pbWUgPSAiaW1hZ2UvanBlZyIgfQogICAgICAgICAgICBlbHNlIGlmIGV4dCA9PSAianNvbiIgeyBtaW1lID0gImFwcGxpY2F0aW9uL2pzb24iIH0KCiAgICAgICAgICAgIGlmIGxldCBmaWxlUGF0aCA9IEJ1bmRsZS5tYWluLnBhdGgoZm9yUmVzb3VyY2U6IG5hbWUsIG9mVHlwZTogZXh0LmlzRW1wdHkgPyBuaWwgOiBleHQpLAogICAgICAgICAgICAgICBsZXQgZmlsZURhdGEgPSB0cnk/IERhdGEoY29udGVudHNPZjogVVJMKGZpbGVVUkxXaXRoUGF0aDogZmlsZVBhdGgpKSB7CiAgICAgICAgICAgICAgICBsZXQgaGVhZGVyID0gIkhUVFAvMS4xIDIwMCBPS1xyXG5Db250ZW50LVR5cGU6IFwobWltZSlcclxuQ29udGVudC1MZW5ndGg6IFwoZmlsZURhdGEuY291bnQpXHJcbkFjY2Vzcy1Db250cm9sLUFsbG93LU9yaWdpbjogKlxyXG5DYWNoZS1Db250cm9sOiBuby1jYWNoZVxyXG5Db25uZWN0aW9uOiBjbG9zZVxyXG5cclxuIgoKICAgICAgICAgICAgICAgIHZhciB0b3RhbERhdGEgPSBoZWFkZXIuZGF0YSh1c2luZzogLnV0ZjgpIQogICAgICAgICAgICAgICAgdG90YWxEYXRhLmFwcGVuZChmaWxlRGF0YSkKICAgICAgICAgICAgICAgIGNvbm5lY3Rpb24uc2VuZChjb250ZW50OiB0b3RhbERhdGEsIGNvbXBsZXRpb246IC5jb250ZW50UHJvY2Vzc2VkKHsgXyBpbgogICAgICAgICAgICAgICAgICAgIGNvbm5lY3Rpb24uY2FuY2VsKCkKICAgICAgICAgICAgICAgIH0pKQogICAgICAgICAgICB9IGVsc2UgewogICAgICAgICAgICAgICAgc2VsZi5zZW5kTm90Rm91bmQoY29ubmVjdGlvbiwgcmVhc29uOiAiRmlsZSBub3QgZm91bmQ6IFwocGF0aCkiKQogICAgICAgICAgICB9CiAgICAgICAgfQogICAgfQogICAgCiAgICBwcml2YXRlIGZ1bmMgcGFyc2VRdWVyeShfIHE6IFN0cmluZykgLT4gW1N0cmluZzogU3RyaW5nXSB7CiAgICAgICAgdmFyIHJlczogW1N0cmluZzogU3RyaW5nXSA9IFs6XQogICAgICAgIGZvciBpdGVtIGluIHEuY29tcG9uZW50cyhzZXBhcmF0ZWRCeTogIiYiKSB7CiAgICAgICAgICAgIGxldCBwYWlyID0gaXRlbS5jb21wb25lbnRzKHNlcGFyYXRlZEJ5OiAiPSIpCiAgICAgICAgICAgIGlmIHBhaXIuY291bnQgPT0gMiB7IHJlc1twYWlyWzBdXSA9IHBhaXJbMV0gfQogICAgICAgIH0KICAgICAgICByZXR1cm4gcmVzCiAgICB9CiAgICAKICAgIHByaXZhdGUgZnVuYyBzZW5kTm90Rm91bmQoXyBjb25uZWN0aW9uOiBOV0Nvbm5lY3Rpb24sIHJlYXNvbjogU3RyaW5nID0gIiIpIHsKICAgICAgICBsZXQgbXNnID0gIkhUVFAvMS4xIDQwNCBOb3QgRm91bmRcclxuWC1FcnJvci1SZWFzb246IFwocmVhc29uKVxyXG5Db250ZW50LUxlbmd0aDogMFxyXG5BY2Nlc3MtQ29udHJvbC1BbGxvdy1PcmlnaW46ICpcclxuQ29ubmVjdGlvbjogY2xvc2VcclxuXHJcbiIKICAgICAgICBjb25uZWN0aW9uLnNlbmQoY29udGVudDogbXNnLmRhdGEodXNpbmc6IC51dGY4KSEsIGNvbXBsZXRpb246IC5jb250ZW50UHJvY2Vzc2VkKHsgXyBpbgogICAgICAgICAgICBjb25uZWN0aW9uLmNhbmNlbCgpCiAgICAgICAgfSkpCiAgICB9Cn0KCi8vIE1BUks6IC0gQ29udGVudFZpZXcKc3RydWN0IENvbnRlbnRWaWV3OiBWaWV3IHsKICAgIHZhciBib2R5OiBzb21lIFZpZXcgewogICAgICAgIFpTdGFjayB7CiAgICAgICAgICAgIENvbG9yKGhleDogIiMwZjE3MmEiKS5pZ25vcmVzU2FmZUFyZWEoKQogICAgICAgICAgICBIeWJyaWRUcmlwV2ViVmlldygpCiAgICAgICAgICAgICAgICAuZWRnZXNJZ25vcmluZ1NhZmVBcmVhKC5hbGwpCiAgICAgICAgfQogICAgfQp9CgovLyBNQVJLOiAtIEh5YnJpZFRyaXBXZWJWaWV3CnN0cnVjdCBIeWJyaWRUcmlwV2ViVmlldzogVUlWaWV3UmVwcmVzZW50YWJsZSB7CiAgICBmdW5jIG1ha2VVSVZpZXcoY29udGV4dDogQ29udGV4dCkgLT4gV0tXZWJWaWV3IHsKICAgICAgICBsZXQgY29uZmlnID0gV0tXZWJWaWV3Q29uZmlndXJhdGlvbigpCiAgICAgICAgY29uZmlnLmFsbG93c0lubGluZU1lZGlhUGxheWJhY2sgPSB0cnVlCgogICAgICAgIGxldCB3ZWJWaWV3ID0gV0tXZWJWaWV3KGZyYW1lOiAuemVybywgY29uZmlndXJhdGlvbjogY29uZmlnKQogICAgICAgIHdlYlZpZXcubmF2aWdhdGlvbkRlbGVnYXRlID0gY29udGV4dC5jb29yZGluYXRvcgogICAgICAgIHdlYlZpZXcuaXNPcGFxdWUgPSBmYWxzZQogICAgICAgIHdlYlZpZXcuYmFja2dyb3VuZENvbG9yID0gVUlDb2xvcihyZWQ6IDAuMDYsIGdyZWVuOiAwLjA5LCBibHVlOiAwLjE2LCBhbHBoYTogMS4wKQogICAgICAgIHdlYlZpZXcuc2Nyb2xsVmlldy5iYWNrZ3JvdW5kQ29sb3IgPSBVSUNvbG9yKHJlZDogMC4wNiwgZ3JlZW46IDAuMDksIGJsdWU6IDAuMTYsIGFscGhhOiAxLjApCiAgICAgICAgd2ViVmlldy5zY3JvbGxWaWV3LmNvbnRlbnRJbnNldEFkanVzdG1lbnRCZWhhdmlvciA9IC5uZXZlcgogICAgICAgIGlmICNhdmFpbGFibGUoaU9TIDE2LjQsICopIHsKICAgICAgICAgICAgd2ViVmlldy5pc0luc3BlY3RhYmxlID0gdHJ1ZQogICAgICAgIH0KCiAgICAgICAgY29udGV4dC5jb29yZGluYXRvci53ZWJWaWV3ID0gd2ViVmlldwogICAgICAgIGNvbnRleHQuY29vcmRpbmF0b3IubG9hZEFwcCgpCiAgICAgICAgcmV0dXJuIHdlYlZpZXcKICAgIH0KCiAgICBmdW5jIHVwZGF0ZVVJVmlldyhfIHVpVmlldzogV0tXZWJWaWV3LCBjb250ZXh0OiBDb250ZXh0KSB7fQogICAgZnVuYyBtYWtlQ29vcmRpbmF0b3IoKSAtPiBDb29yZGluYXRvciB7IENvb3JkaW5hdG9yKCkgfQoKICAgIGNsYXNzIENvb3JkaW5hdG9yOiBOU09iamVjdCwgV0tOYXZpZ2F0aW9uRGVsZWdhdGUgewogICAgICAgIHdlYWsgdmFyIHdlYlZpZXc6IFdLV2ViVmlldz8KCiAgICAgICAgZnVuYyBsb2FkQXBwKCkgewogICAgICAgICAgICBEaXNwYXRjaFF1ZXVlLm1haW4uYXN5bmNBZnRlcihkZWFkbGluZTogLm5vdygpICsgMC4xNSkgeyBbd2VhayBzZWxmXSBpbgogICAgICAgICAgICAgICAgaWYgbGV0IHVybCA9IFVSTChzdHJpbmc6ICJodHRwOi8vMTI3LjAuMC4xOjgwODgvaW5kZXguaHRtbCIpIHsKICAgICAgICAgICAgICAgICAgICBsZXQgcmVxID0gVVJMUmVxdWVzdCh1cmw6IHVybCwgY2FjaGVQb2xpY3k6IC5yZWxvYWRJZ25vcmluZ0xvY2FsQ2FjaGVEYXRhLCB0aW1lb3V0SW50ZXJ2YWw6IDEwKQogICAgICAgICAgICAgICAgICAgIHNlbGY/LndlYlZpZXc/LmxvYWQocmVxKQogICAgICAgICAgICAgICAgICAgIHByaW50KCLinIUg6Lev5Lmm5bey6YCa6L+H5pys5ZywIEhUVFAg5pyN5Yqh5ZmoIChodHRwOi8vMTI3LjAuMC4xOjgwODgvaW5kZXguaHRtbCkg5Yqg6L29IikKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgfQogICAgICAgIH0KCiAgICAgICAgZnVuYyB3ZWJWaWV3KF8gd2ViVmlldzogV0tXZWJWaWV3LCBkZWNpZGVQb2xpY3lGb3IgbmF2OiBXS05hdmlnYXRpb25BY3Rpb24sCiAgICAgICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlcjogQGVzY2FwaW5nIChXS05hdmlnYXRpb25BY3Rpb25Qb2xpY3kpIC0+IFZvaWQpIHsKICAgICAgICAgICAgZ3VhcmQgbGV0IHVybCA9IG5hdi5yZXF1ZXN0LnVybCBlbHNlIHsgZGVjaXNpb25IYW5kbGVyKC5hbGxvdyk7IHJldHVybiB9CiAgICAgICAgICAgIGxldCBzY2hlbWUgPSB1cmwuc2NoZW1lPy5sb3dlcmNhc2VkKCkgPz8gIiIKCiAgICAgICAgICAgIGlmIGxldCBob3N0ID0gdXJsLmhvc3Q/Lmxvd2VyY2FzZWQoKSwgaG9zdCA9PSAiMTI3LjAuMC4xIiB8fCBob3N0ID09ICJsb2NhbGhvc3QiIHsKICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlciguYWxsb3cpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgaWYgWyJkaWFucGluZyIsInhoc2Rpc2NvdmVyIiwiaW9zYW1hcCIsImJhaWR1bWFwIiwidGVsIiwibWFpbHRvIl0uY29udGFpbnMoc2NoZW1lKSB7CiAgICAgICAgICAgICAgICBpZiBVSUFwcGxpY2F0aW9uLnNoYXJlZC5jYW5PcGVuVVJMKHVybCkgeyBVSUFwcGxpY2F0aW9uLnNoYXJlZC5vcGVuKHVybCkgfQogICAgICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyKC5jYW5jZWwpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgaWYgdXJsLmFic29sdXRlU3RyaW5nLmNvbnRhaW5zKCJ1cmkuYW1hcC5jb20vbmF2aWdhdGlvbiIpIHsKICAgICAgICAgICAgICAgIFVJQXBwbGljYXRpb24uc2hhcmVkLm9wZW4odXJsKQogICAgICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyKC5jYW5jZWwpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgaWYgbmF2Lm5hdmlnYXRpb25UeXBlICE9IC5saW5rQWN0aXZhdGVkIHsKICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlciguYWxsb3cpCiAgICAgICAgICAgICAgICByZXR1cm4KICAgICAgICAgICAgfQoKICAgICAgICAgICAgaWYgc2NoZW1lID09ICJodHRwIiB8fCBzY2hlbWUgPT0gImh0dHBzIiB7CiAgICAgICAgICAgICAgICBVSUFwcGxpY2F0aW9uLnNoYXJlZC5vcGVuKHVybCkKICAgICAgICAgICAgICAgIGRlY2lzaW9uSGFuZGxlciguY2FuY2VsKQogICAgICAgICAgICAgICAgcmV0dXJuCiAgICAgICAgICAgIH0KICAgICAgICAgICAgZGVjaXNpb25IYW5kbGVyKC5hbGxvdykKICAgICAgICB9CiAgICB9Cn0KCmV4dGVuc2lvbiBDb2xvciB7CiAgICBpbml0KGhleDogU3RyaW5nKSB7CiAgICAgICAgbGV0IGhleCA9IGhleC50cmltbWluZ0NoYXJhY3RlcnMoaW46IENoYXJhY3RlclNldC5hbHBoYW51bWVyaWNzLmludmVydGVkKQogICAgICAgIHZhciBpbnQ6IFVJbnQ2NCA9IDAKICAgICAgICBTY2FubmVyKHN0cmluZzogaGV4KS5zY2FuSGV4SW50NjQoJmludCkKICAgICAgICBsZXQgYSwgciwgZywgYjogVUludDY0CiAgICAgICAgc3dpdGNoIGhleC5jb3VudCB7CiAgICAgICAgY2FzZSAzOiAgKGEscixnLGIpID0gKDI1NSwoaW50Pj44KSoxNywoaW50Pj40ICYgMHhGKSoxNywoaW50ICYgMHhGKSoxNykKICAgICAgICBjYXNlIDY6ICAoYSxyLGcsYikgPSAoMjU1LGludD4+MTYsaW50Pj44ICYgMHhGRixpbnQgJiAweEZGKQogICAgICAgIGNhc2UgODogIChhLHIsZyxiKSA9IChpbnQ+PjI0LGludD4+MTYgJiAweEZGLGludD4+OCAmIDB4RkYsaW50ICYgMHhGRikKICAgICAgICBkZWZhdWx0OiAoYSxyLGcsYikgPSAoMjU1LDAsMCwwKQogICAgICAgIH0KICAgICAgICBzZWxmLmluaXQoLnNSR0IscmVkOkRvdWJsZShyKS8yNTUsZ3JlZW46RG91YmxlKGcpLzI1NSxibHVlOkRvdWJsZShiKS8yNTUsb3BhY2l0eTpEb3VibGUoYSkvMjU1KQogICAgfQp9Cg==').decode('utf-8')

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
    <string>com.noodles.xinjiang.trip</string>
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
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.xinjiang.trip;
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
				PRODUCT_BUNDLE_IDENTIFIER = com.noodles.xinjiang.trip;
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

