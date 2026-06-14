"""
一键更新隧道地址并部署
用法: python update_deploy.py           → 自动检测隧道URL
       python update_deploy.py <URL>     → 手动指定
"""
import sys, re, subprocess, os, glob, time

def find_tunnel_url():
    """自动检测活跃的隧道URL"""
    import subprocess, urllib.request
    patterns = [
        os.path.expandvars(r"%TEMP%\claude\f--22-crop-disease-diagnosis-main\*\tasks\*.output"),
        os.path.expandvars(r"%TEMP%\claude\*\tasks\*.output"),
    ]
    candidates = {}
    for pat in patterns:
        for f in sorted(glob.glob(pat), key=os.path.getmtime, reverse=True)[:20]:
            try:
                with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                for url in re.findall(r'https://[a-z0-9-]+\.trycloudflare\.com', content):
                    if url not in candidates:
                        candidates[url] = os.path.getmtime(f)
            except: pass
    # 验证哪个URL活着（最新的优先）
    for url in sorted(candidates, key=candidates.get, reverse=True)[:5]:
        try:
            req = urllib.request.Request(url + '/api/health')
            urllib.request.urlopen(req, timeout=5)
            return url  # 这个活着！
        except: continue
    return None  # 都死了，需要重启隧道

if len(sys.argv) >= 2:
    new_url = sys.argv[1].rstrip('/')
else:
    print("正在自动检测隧道地址...")
    new_url = find_tunnel_url()
    if not new_url:
        print("❌ 未找到隧道地址")
        print("请确保 cloudflared 隧道正在运行")
        print("或手动指定: python update_deploy.py https://xxx.trycloudflare.com")
        sys.exit(1)

if 'trycloudflare' not in new_url:
    print(f"⚠️ 地址格式不对: {new_url}")
    sys.exit(1)

print(f"🔗 隧道地址: {new_url}")

# 1. 更新 api.js
api_js = r"F:\github好看网站\leleo-home-page-main\src\services\api.js"
with open(api_js, 'r', encoding='utf-8') as f:
    content = f.read()
old = re.findall(r"https://[^'\"]*trycloudflare\.com", content)
if old and old[0] == new_url:
    print("✅ 地址未变，无需更新")
    sys.exit(0)
if old:
    content = content.replace(old[0], new_url)
    with open(api_js, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ api.js: {old[0]} → {new_url}")

# 2. 构建
print("🔨 构建前端...")
os.chdir(r"F:\github好看网站\leleo-home-page-main")
subprocess.run(["npx", "vite", "build"], shell=True)

# 3. 部署
print("🚀 部署到腾讯云...")
subprocess.run(f'echo | npx tcb hosting deploy dist/ -e duyue-d4gw2qp01d8a7bd6e', shell=True)

print(f"\n🎉 完成！https://duyue-d4gw2qp01d8a7bd6e-1433783466.tcloudbaseapp.com")
