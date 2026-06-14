@echo off
chcp 65001 >nul
title 更新隧道地址...

echo ============================================
echo   🔄 更新隧道地址
echo ============================================
echo.

REM 1. 获取最新的后端隧道URL
echo [1/3] 获取最新隧道地址...
set TUNNEL_URL=

REM 从 cloudflared 输出中提取 trycloudflare URL
for /f "tokens=*" %%a in ('type "%TEMP%\claude\f--22-crop-disease-diagnosis-main\*\tasks\*.output" 2^>nul ^| findstr "trycloudflare.com"') do (
    echo %%a | findstr "https://.*trycloudflare.com" >nul
    if not errorlevel 1 (
        for /f "tokens=2 delims= " %%b in ("%%a") do set TUNNEL_URL=%%b
    )
)

if "%TUNNEL_URL%"=="" (
    echo ⚠️ 未找到隧道URL，请确保隧道已启动
    echo 查看隧道窗口中的 trycloudflare.com 地址
    echo 手动复制地址后，运行: node update_api.js 你的隧道地址
    pause
    exit /b
)

echo   隧道地址: %TUNNEL_URL%

REM 2. 更新 api.js
echo [2/3] 更新前端配置...
cd /d "F:\github好看网站\leleo-home-page-main"

REM 创建临时 node 脚本更新 api.js
echo const fs = require('fs'); > _update_api.js
echo const url = '%TUNNEL_URL%'; >> _update_api.js
echo let content = fs.readFileSync('src/services/api.js', 'utf-8'); >> _update_api.js
echo content = content.replace(/return 'https:\/\/[^']*trycloudflare\.com'/, "return '" + url + "'"); >> _update_api.js
echo fs.writeFileSync('src/services/api.js', content); >> _update_api.js
echo console.log('api.js 已更新'); >> _update_api.js
node _update_api.js
del _update_api.js

REM 3. 构建和部署
echo [3/3] 构建并部署到腾讯云...
call npx vite build
echo | npx tcb hosting deploy dist/ -e duyue-d4gw2qp01d8a7bd6e

echo.
echo ============================================
echo   ✅ 更新完成！
echo   网站: https://duyue-d4gw2qp01d8a7bd6e-1433783466.tcloudbaseapp.com
echo ============================================
pause
