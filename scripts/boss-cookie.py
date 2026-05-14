#!/usr/bin/env python3
"""
BOSS直聘 Cookie 导出/注入工具

使用方法：
1. 先在 Firefox 中登录 zhipin.com
2. 运行: python3 boss-cookie.py export
   → 从 Firefox 的 cookies.sqlite 导出 zhipin.com 的 cookies
3. 运行: python3 boss-cookie.py inject
   → 生成 browser_cdp 注入命令，供 Hermes skill 使用

手动导出方式：
1. 在浏览器中登录 zhipin.com
2. F12 → Application → Cookies → 复制所有 cookie
3. 保存为 JSON 文件: ~/.hermes/boss-cookies.json

命令: python3 boss-cookie.py [export|inject|help]
"""

import json
import sqlite3
import os
import sys
import subprocess
import http.cookiejar
from pathlib import Path
from datetime import datetime

# Firefox cookies.sqlite 位置
FIREFOX_PROFILES = [
    os.path.expanduser("~/.mozilla/firefox"),
]

# 输出文件
COOKIE_FILE = os.path.expanduser("~/.hermes/boss-cookies.json")

# Hermes browser CDP endpoint (agent-browser in Docker)
# We'll use the Hermes CLI approach instead


def export_firefox_cookies():
    """从 Firefox 导出 zhipin.com cookies"""
    for profile_dir in FIREFOX_PROFILES:
        if not os.path.isdir(profile_dir):
            continue
        for entry in os.listdir(profile_dir):
            full = os.path.join(profile_dir, entry)
            if os.path.isdir(full) and ("default" in entry.lower() or os.path.exists(os.path.join(full, "cookies.sqlite"))):
                cookies_db = os.path.join(full, "cookies.sqlite")
                if not os.path.exists(cookies_db):
                    continue
                print(f"Found Firefox profile: {full}")
                # Firefox locks the DB, copy it first
                tmp_db = "/tmp/firefox_cookies_tmp.sqlite"
                try:
                    subprocess.run(["cp", cookies_db, tmp_db], check=True)
                except Exception as e:
                    print(f"Cannot copy cookies db: {e}")
                    continue

                cookies = []
                try:
                    conn = sqlite3.connect(tmp_db)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT name, value, host, path, isSecure, expiry
                        FROM moz_cookies
                        WHERE host LIKE '%zhipin.com%'
                    """)
                    for row in cursor.fetchall():
                        name, value, host, path, secure, expiry = row
                        cookies.append({
                            "name": name,
                            "value": value,
                            "domain": host,
                            "path": path,
                            "secure": bool(secure),
                            "httpOnly": False,
                            "sameSite": "Lax",
                        })
                    conn.close()
                except Exception as e:
                    print(f"Error reading cookies: {e}")
                    continue
                finally:
                    try:
                        os.unlink(tmp_db)
                    except OSError:
                        pass

                if cookies:
                    os.makedirs(os.path.dirname(COOKIE_FILE), exist_ok=True)
                    with open(COOKIE_FILE, "w") as f:
                        json.dump(cookies, f, indent=2, ensure_ascii=False)
                    print(f"Exported {len(cookies)} cookies to {COOKIE_FILE}")
                    return cookies
                else:
                    print("No zhipin.com cookies found in this profile")

    print("No Firefox cookies found. Make sure you've logged into zhipin.com in Firefox.")
    print("\nAlternative: export cookies manually from browser DevTools:")
    print("  1. Open zhipin.com in browser")
    print("  2. F12 → Application → Cookies → https://www.zhipin.com")
    print("  3. Select all cookies, right-click → Copy")
    print(f"  4. Save to {COOKIE_FILE}")
    return None


def generate_cdp_commands():
    """生成 browser_cdp 注入命令，供 Hermes skill 使用"""
    if not os.path.exists(COOKIE_FILE):
        print(f"Cookie file not found: {COOKIE_FILE}")
        print("Run: python3 boss-cookie.py export")
        return

    with open(COOKIE_FILE) as f:
        cookies = json.load(f)

    print(f"\n# 在 Hermes 对话中执行以下操作来注入 cookies：")
    print(f"# 共 {len(cookies)} 个 cookies\n")
    print(f"1. 先让 Hermes 打开 zhipin.com:")
    print(f"   browser_navigate('https://www.zhipin.com')")
    print(f"")
    print(f"2. 用 browser_cdp 注入每个 cookie:")
    for c in cookies:
        params = {
            "name": c["name"],
            "value": c["value"],
            "domain": c.get("domain", ".zhipin.com"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", True),
            "httpOnly": c.get("httpOnly", False),
            "sameSite": c.get("sameSite", "Lax"),
        }
        # Truncate value for display
        display_val = c["value"][:20] + "..." if len(c["value"]) > 20 else c["value"]
        print(f'   browser_cdp(method="Network.setCookie", params={json.dumps(params, ensure_ascii=False)})')

    print(f"\n3. 刷新页面验证:")
    print(f"   browser_navigate('https://www.zhipin.com/web/geek/recommend')")
    print(f"   browser_snapshot()")

    print(f"\n--- 或者直接让 Hermes 读取 cookie 文件自动注入 ---")
    print(f"在飞书对 Hermes 说：")
    print(f'  "读取 {COOKIE_FILE} 中的 cookies 并注入到浏览器，然后打开 zhipin.com"')


def print_manual_instructions():
    """打印手动导出 cookies 的说明"""
    print("""
========================================
手动导出 BOSS直聘 Cookies 方法
========================================

方法1: Firefox (推荐)
  1. 在 Firefox 中打开并登录 zhipin.com
  2. 运行: python3 boss-cookie.py export

方法2: Chromium/Chrome DevTools
  1. 在浏览器中打开并登录 zhipin.com
  2. F12 → Console
  3. 粘贴执行:
     copy(document.cookie.split(';').map(c => {
       const [name, ...rest] = c.trim().split('=');
       return {name: name, value: rest.join('='), domain: '.zhipin.com', path: '/', secure: true};
     }))
  4. 这会复制到剪贴板
  5. 保存到文件: echo '[粘贴内容]' > ~/.hermes/boss-cookies.json

方法3: 浏览器扩展 (EditThisCookie 等)
  1. 安装 EditThisCookie 扩展
  2. 打开 zhipin.com
  3. 点击扩展 → Export → 复制 JSON
  4. 保存到 ~/.hermes/boss-cookies.json

导出后运行: python3 boss-cookie.py inject
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_manual_instructions()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    if cmd == "export":
        export_firefox_cookies()
    elif cmd == "inject":
        generate_cdp_commands()
    elif cmd == "help":
        print_manual_instructions()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python3 boss-cookie.py [export|inject|help]")
