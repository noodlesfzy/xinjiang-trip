#!/opt/bin/python3
# -*- coding: utf-8 -*-
"""
东航 APP 每日自动签到脚本
增强版：包含真实响应分析、重试机制、Token 寿命预警、高精告警与微信推送
"""

import requests
import json
import time
import random
import logging
import ssl
import urllib3
from datetime import datetime, date
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

urllib3.disable_warnings()

# ================= 配置区域 =================

SERVERCHAN_KEY = "SCT311643TkpJ5XNcLW9xLCodYO5bHGDuj"
TOKEN_UPDATE_DATE = "2026-08-21"  # 记录 Token 更新日期 (YYYY-MM-DD)
ROUTER_MGR_URL = "http://192.168.50.1:8090"  # 手机端更新后台地址

URL = "https://selfservice.ceair.com/additional/api/v1/star/checkin"
HEADERS = {
    "Host": "selfservice.ceair.com",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148/iPhone16,2/NEW_CEAIRAPP_IOS_9.5.12",
    "Referer": "https://ecmembers.ceair.com/",
    "Origin": "https://ecmembers.ceair.com",
    "M-CEAIR-ENCRYPTED": "true",
    "ceair-ecuser-token": "32249125-3a14d500-e5e6-4fae-a722-674f00c27e5e"
}

RAW_BODY = "0049ea52622d224f8e31ee183b9782caf3e99d29e13047fb29ce69cd348a3ecff7f2a7c70774412c6e23c37abc8f94cb0ef41bf7d0b808cb549285648fa09fc432fbe8c63b69976354aed2b6d11485f2d4e66616597cda99cd1e96843e984611b698d462ad8e9354326f60bf6e094c2aafae250734e33c6c688c3c6cbec4490b55623008bf8fb2ff88516877e457660dfaca0fd0b8992253c0dff9902df7217ce257b93b168fa158bc358e4d305d68d4e3ee3869a0d5eff9efc446e507985c3ccdacfc60089d9cff3a79741757baca33"

# ===========================================

class LegacySSLAdapter(HTTPAdapter):
    """解决旧版 SSL/TLS 握手兼容性"""
    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = create_urllib3_context()
        ctx.load_default_certs()
        ctx.options |= 0x4 
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, ssl_context=ctx
        )

def get_token_age_info():
    """计算 Token 使用天数与预警信息"""
    try:
        start_date = datetime.strptime(TOKEN_UPDATE_DATE, "%Y-%m-%d").date()
        today = date.today()
        days_used = (today - start_date).days
        
        warn_msg = ""
        if days_used >= 90:
            warn_msg = f"\n\n> ⚠️ **Token 寿命预警**：当前 Token 已持续使用 **{days_used} 天**（官方有效期约 120 天），近期请注意在 App 中刷新凭证！"
        elif days_used >= 60:
            warn_msg = f"\n\n> ℹ️ **Token 状态**：已使用 **{days_used} 天**（状态良好）。"
        else:
            warn_msg = f"\n\n> ℹ️ **Token 状态**：已使用 **{days_used} 天**。"
            
        return days_used, warn_msg
    except Exception:
        return 0, ""

def send_notification(title, content):
    """发送 Server酱 微信通知"""
    if "SCT" not in SERVERCHAN_KEY:
        print("未配置有效的 Server酱 KEY，跳过微信推送")
        return
    try:
        push_url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
        data = {"title": title, "desp": content}
        resp = requests.post(push_url, data=data, timeout=8)
        if resp.status_code == 200:
            print(">> 微信推送已发送成功")
        else:
            print(f">> 微信推送接口返回异常状态码: {resp.status_code}")
    except Exception as e:
        print(f">> 微信推送失败: {e}")

def parse_response_result(response):
    """
    深度解析东航签到接口的返回内容：
    - 状态码非 200 -> 明确失败
    - 状态码 200 时，分析 Body 结构：
      * 192 字符密文 -> 判定成功
      * 224 字符密文 (或含 token/auth 错误) -> 判定 Token 失效
      * JSON 明文 -> 深度判断 code / msg
    """
    status_code = response.status_code
    body_text = response.text.strip()
    
    if status_code != 200:
        return {
            "success": False,
            "reason": "HTTP_ERROR",
            "detail": f"服务器返回 HTTP 状态码: {status_code}"
        }
    
    # 尝试作为 JSON 解析（如果服务端返回未加密的错误说明）
    try:
        data = response.json()
        code = str(data.get("resultCode", data.get("code", "")))
        msg = str(data.get("resultMsg", data.get("msg", data.get("message", ""))))
        
        if code in ["0000", "0", "200", "SUCCESS", "success"]:
            return {"success": True, "reason": "SUCCESS", "detail": f"接口返回成功: {msg or '签到完成'}"}
        elif any(k in msg for k in ["token", "登录", "凭证", "鉴权", "过期", "失效", "重新登录", "auth"]):
            return {"success": False, "reason": "TOKEN_EXPIRED", "detail": f"Token 鉴权失败: {msg} (code={code})"}
        else:
            return {"success": False, "reason": "BIZ_ERROR", "detail": f"业务返回异常: {msg} (code={code})"}
    except Exception:
        pass  # 不是 JSON，是密文字符串
    
    # 密文模式长度与特征分析
    body_len = len(body_text)
    
    # 正常签到成功返回的密文长度通常为 192 字符 (96 字节 AES)
    if body_len == 192:
        return {
            "success": True,
            "reason": "SUCCESS",
            "detail": f"服务器响应正常密文 (192位)，签到执行成功"
        }
    # Token 失效/鉴权失败的密文长度通常为 224 字符 (112 字节 AES)
    elif body_len == 224:
        return {
            "success": False,
            "reason": "TOKEN_EXPIRED",
            "detail": f"东航鉴权拒绝 (224位错误密文)，Token 已失效或过期"
        }
    elif body_len == 0:
        return {
            "success": False,
            "reason": "EMPTY_BODY",
            "detail": "服务器返回空响应体"
        }
    else:
        # 其他未知长度密文，记录前32位以供排查
        return {
            "success": True,
            "reason": "UNKNOWN_ENCRYPTED",
            "detail": f"状态码 200，返回未知长度密文({body_len}位: {body_text[:32]}...)"
        }

def do_sign():
    # 随机延迟，防止固定时刻被识别为机械请求 (仅定时执行时)
    delay = random.randint(2, 8)
    print(f"随机等待 {delay} 秒后发起签到...")
    time.sleep(delay)

    days_used, token_age_md = get_token_age_info()
    
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    
    max_retries = 3
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[{attempt}/{max_retries}] 正在请求东航服务器...")
            response = session.post(URL, headers=HEADERS, data=RAW_BODY, timeout=25)
            
            result = parse_response_result(response)
            
            if result["success"]:
                print(f"✅ 签到判定成功: {result['detail']}")
                title = f"✈️ 东航签到成功 (Token使用第{days_used}天)"
                desp = (
                    f"### ✅ 东航每日签到成功\n\n"
                    f"- **执行状态**：{result['detail']}\n"
                    f"- **当前时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"{token_age_md}"
                )
                send_notification(title, desp)
                return True
                
            elif result["reason"] == "TOKEN_EXPIRED":
                print(f"❌ 签到失败: {result['detail']}")
                title = "❌ 东航签到失败：Token 已失效！"
                desp = (
                    f"### ❌【告警】东航 Token 已过期失效\n\n"
                    f"- **失败原因**：{result['detail']}\n"
                    f"- **已用天数**：当前 Token 已持续使用 **{days_used} 天**\n"
                    f"- **解决方式**：\n"
                    f"  1. 在手机端打开【东航 APP】-> 进入【里程积分账单】刷新抓包；\n"
                    f"  2. 点击快捷更新后台：[{ROUTER_MGR_URL}]({ROUTER_MGR_URL}) 粘贴新 Token 保存。"
                )
                send_notification(title, desp)
                return False
                
            else:
                print(f"⚠️ 签到返回异常: {result['detail']}")
                title = "⚠️ 东航签到异常告警"
                desp = (
                    f"### ⚠️ 东航签到异常\n\n"
                    f"- **原因**：{result['detail']}\n"
                    f"- **HTTP 状态**：{response.status_code}\n"
                    f"- **返回预览**：`{response.text[:100]}`\n"
                    f"{token_age_md}\n\n"
                    f"👉 如需更新凭证可访问: [{ROUTER_MGR_URL}]({ROUTER_MGR_URL})"
                )
                send_notification(title, desp)
                return False

        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as net_err:
            print(f"[{attempt}/{max_retries}] 网络请求异常: {net_err}")
            last_error = net_err
            if attempt < max_retries:
                time.sleep(5)
                continue
        except Exception as e:
            print(f"脚本执行未知错误: {e}")
            last_error = e
            break

    # 所有重试失败
    print(f"❌ 多次重试均失败: {last_error}")
    title = "⚠️ 东航签到网络请求失败"
    desp = (
        f"### ⚠️ 东航签到执行失败（网络/系统错误）\n\n"
        f"- **重试次数**：已重试 {max_retries} 次\n"
        f"- **错误详情**：`{str(last_error)}`\n"
        f"- **执行时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"{token_age_md}"
    )
    send_notification(title, desp)
    return False

if __name__ == "__main__":
    do_sign()
