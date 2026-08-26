#!/opt/bin/python3
# -*- coding: utf-8 -*-
"""
东航脚本管理中心 & Shadowrocket 自动回传 API (运行在路由器 8090 端口)
智能防抖版：只有 Token 真正变化时才重置日期并弹窗通知，未变化时保持天数统计
"""

from bottle import route, run, template, request, post, response
import re
import os
import json
import subprocess
from datetime import datetime, date

SCRIPT_PATH = "/jffs/scripts/custom/ceair_task.py"

# Shadowrocket 脚本内容
SHADOWROCKET_JS = '''/**
 * 东航 App Token 自动同步脚本 (Shadowrocket / Surge / Loon / QX)
 * 智能防抖：仅当 Token 发生变化时才弹出手机横幅通知
 */

const routerApiUrl = "http://192.168.50.1:8090/api/update";

function main() {
    const headers = $request.headers || {};
    let token = "";
    
    for (let key in headers) {
        let lower = key.toLowerCase();
        if (lower === "ceair-ecuser-token" || lower === "app_token_key" || lower === "ceair-token") {
            let val = headers[key];
            if (val && val.length > 10 && val !== "null" && val !== "undefined") {
                token = val.trim();
                break;
            }
        }
    }

    if (token) {
        $httpClient.post({
            url: routerApiUrl,
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({token: token})
        }, function(error, response, data) {
            if (!error && data) {
                try {
                    let res = JSON.parse(data);
                    // 仅当 Token 真正变更时才弹窗通知，避免日常刷 App 时频繁打扰
                    if (res.status === "updated") {
                        $notification.post(
                            "✈️ 东航 Token 已自动更新",
                            "检测到新 Token，已同步至路由器并重置天数！",
                            "新 Token: " + token.substring(0, 16) + "..."
                        );
                    }
                } catch (e) {}
            }
            $done({});
        });
    } else {
        $done({});
    }
}

main();
'''

HTML_TPL = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>东航签到管理中心</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 15px; background: #f4f6f8; margin: 0; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); max-width: 500px; margin: 0 auto 15px auto; }
        h2 { margin-top: 0; color: #1a1a1a; font-size: 20px; display: flex; align-items: center; gap: 8px; }
        .status-badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 15px; }
        .status-good { background: #e6f4ea; color: #137333; }
        .status-warn { background: #fef7e0; color: #b06000; }
        .info-row { font-size: 14px; color: #555; margin-bottom: 8px; }
        .info-row b { color: #222; }
        label { display: block; font-weight: 600; font-size: 14px; margin-top: 15px; margin-bottom: 5px; color: #333; }
        textarea { width: 100%; height: 75px; padding: 10px; border: 1px solid #dcdfe6; border-radius: 8px; font-size: 13px; font-family: monospace; resize: vertical; }
        .btn-primary { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; margin-top: 15px; cursor: pointer; }
        .btn-secondary { width: 100%; padding: 12px; background: #34a853; color: white; border: none; border-radius: 8px; font-size: 15px; font-weight: 600; margin-top: 10px; cursor: pointer; text-align: center; text-decoration: none; display: block; }
        .msg { padding: 12px; border-radius: 8px; font-size: 14px; margin-bottom: 15px; line-height: 1.5; }
        .msg-success { background: #e6f4ea; color: #137333; border: 1px solid #ceead6; }
        .msg-error { background: #fce8e6; color: #c5221f; border: 1px solid #fad2cf; }
        pre { background: #282c34; color: #abb2bf; padding: 12px; border-radius: 8px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; }
        .tips { font-size: 12px; color: #666; margin-top: 15px; line-height: 1.6; border-top: 1px solid #eee; padding-top: 10px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>✈️ 东航签到管理中心</h2>
        
        <div class="status-badge {{'status-warn' if days_used >= 150 else 'status-good'}}">
            {{'⚠️ 建议近期刷新' if days_used >= 150 else '✅ 凭证运行良好'}} (已连续使用 {{days_used}} 天)
        </div>

        <div class="info-row"><b>当前 Token：</b><code>{{token_preview}}</code></div>
        <div class="info-row"><b>生效日期：</b>{{token_date or '未知'}}</div>
        <div class="info-row"><b>定时任务：</b>每天 08:15 自动签到并微信推送</div>

        % if msg:
            <div class="msg {{'msg-success' if is_success else 'msg-error'}}">{{!msg}}</div>
        % end

        % if test_output:
            <div style="margin-top: 15px;">
                <label>实时测试输出：</label>
                <pre>{{test_output}}</pre>
            </div>
        % end

        <form action="/" method="post">
            <label>新 ceair-ecuser-token：</label>
            <textarea name="token" placeholder="从抓包中复制 ceair-ecuser-token"></textarea>
            
            <label>新 RAW_BODY (如未变更可留空)：</label>
            <textarea name="body" placeholder="留空则保持当前加密串不变"></textarea>
            
            <button type="submit" class="btn-primary">💾 手动保存并更新</button>
        </form>

        <form action="/test" method="post">
            <button type="submit" class="btn-secondary">▶️ 立即触发一次在线签到测试</button>
        </form>

        <div class="tips">
            <b>💡 自动更新方式：</b>配合 Shadowrocket 规则，手机浏览东航 APP 时将自动检查并回传新 Token（Token 未改变时天数不会被误重置）。
        </div>
    </div>
</body>
</html>
'''

def get_script_meta():
    token_preview = "未知"
    token_raw = ""
    token_date = "未知"
    days_used = 0
    
    if os.path.exists(SCRIPT_PATH):
        try:
            with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
                content = f.read()
            
            m_token = re.search(r'"ceair-ecuser-token":\s*"([^"]+)"', content)
            if m_token:
                token_raw = m_token.group(1)
                token_preview = token_raw[:12] + "..." + token_raw[-8:] if len(token_raw) > 20 else token_raw
                
            m_date = re.search(r'TOKEN_UPDATE_DATE\s*=\s*"([^"]+)"', content)
            if m_date:
                token_date = m_date.group(1)
                d = datetime.strptime(token_date, "%Y-%m-%d").date()
                days_used = (date.today() - d).days
        except Exception:
            pass
            
    return token_raw, token_preview, token_date, max(0, days_used)

def update_token_in_file(new_token, new_body=None, force_date=False):
    """
    智能更新：
    - 如果 Token 没有变化且未强制更新日期 -> 保持原日期和天数不变
    - 如果 Token 发生变化 -> 写入新 Token 并重置日期为今天
    """
    with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    m_token = re.search(r'"ceair-ecuser-token":\s*"([^"]+)"', content)
    curr_token = m_token.group(1) if m_token else ""
    
    is_changed = (new_token != curr_token) or bool(new_body) or force_date
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    if not is_changed:
        return False, "Token 未发生变化，已保留原使用天数"

    # 执行替换
    content = re.sub(r'("ceair-ecuser-token":\s*")[^"]+(")', r'\g<1>' + new_token + r'\g<2>', content)
    content = re.sub(r'(TOKEN_UPDATE_DATE\s*=\s*")[^"]+(")', r'\g<1>' + today_str + r'\g<2>', content)
    
    if new_body:
        content = re.sub(r'(RAW_BODY\s*=\s*")[^"]+(")', r'\g<1>' + new_body + r'\g<2>', content)

    with open(SCRIPT_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
        
    return True, f"Token 已更新为最新凭证，日期已重置为 {today_str}"

@route('/')
def index():
    _, token_preview, token_date, days_used = get_script_meta()
    return template(HTML_TPL, msg=None, is_success=True, test_output=None,
                    token_preview=token_preview, token_date=token_date, days_used=days_used)

@post('/')
def do_update():
    token = request.forms.get('token', '').strip()
    body = request.forms.get('body', '').strip()
    
    if not token:
        _, token_preview, token_date, days_used = get_script_meta()
        return template(HTML_TPL, msg="❌ 错误：Token 不能为空！", is_success=False, test_output=None,
                        token_preview=token_preview, token_date=token_date, days_used=days_used)

    try:
        changed, msg = update_token_in_file(token, body, force_date=True)
        _, token_preview, token_date, days_used = get_script_meta()
        return template(HTML_TPL, msg=f"✅ {msg}", is_success=True, test_output=None,
                        token_preview=token_preview, token_date=token_date, days_used=days_used)
    except Exception as e:
        _, token_preview, token_date, days_used = get_script_meta()
        return template(HTML_TPL, msg=f"❌ 更新失败: {str(e)}", is_success=False, test_output=None,
                        token_preview=token_preview, token_date=token_date, days_used=days_used)

# 供 Shadowrocket 调用的自动回传 API
@post('/api/update')
def api_update():
    response.content_type = 'application/json'
    try:
        payload = request.json or {}
        if not payload:
            payload = {
                "token": request.forms.get('token'),
                "body": request.forms.get('body')
            }
        token = (payload.get('token') or '').strip()
        body = (payload.get('body') or '').strip()
        
        if not token:
            return json.dumps({"status": "error", "message": "token is required"})
            
        changed, msg = update_token_in_file(token, body, force_date=False)
        
        if changed:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔔 检测到新 Token 发生变化，已更新并重置日期！Token: {token[:15]}...")
            return json.dumps({"status": "updated", "message": "Token changed and date reset"})
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ℹ️ 收到 Token，内容无变化，保持原天数统计。")
            return json.dumps({"status": "unchanged", "message": "Token unchanged"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

@route('/ceair.js')
def serve_js():
    response.content_type = 'application/javascript; charset=utf-8'
    return SHADOWROCKET_JS

@post('/test')
def do_test():
    _, token_preview, token_date, days_used = get_script_meta()
    try:
        res = subprocess.run(
            ["/opt/bin/python3", SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
            text=True
        )
        output = res.stdout
        is_success = "判定成功" in output or "200" in output
        return template(HTML_TPL, msg="测试已执行完成，请查看下方日志及微信通知！" if is_success else "测试返回异常，请检查！",
                        is_success=is_success, test_output=output,
                        token_preview=token_preview, token_date=token_date, days_used=days_used)
    except Exception as e:
        return template(HTML_TPL, msg=f"执行测试出错: {str(e)}", is_success=False, test_output=str(e),
                        token_preview=token_preview, token_date=token_date, days_used=days_used)

if __name__ == "__main__":
    run(host='192.168.50.1', port=8090)
