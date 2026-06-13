@echo off
chcp 65001 >nul
title 叶片病害诊断系统 — 启动中...

echo ============================================
echo   🌿 叶片病害诊断系统 一键启动
echo ============================================
echo.

REM 1. 启动后端
echo [1/4] 启动后端 API (端口 8000)...
start "Backend-API" cmd /k "cd /d F:\22\crop_disease_diagnosis-main && D:\anaconda\envs\pythonproject\python -m server.main"
timeout /t 5 /nobreak >nul

REM 2. 启动前端
echo [2/4] 启动前端 (端口 5173)...
start "Frontend" cmd /k "cd /d F:\github好看网站\leleo-home-page-main && npx vite --host 0.0.0.0"
timeout /t 5 /nobreak >nul

REM 3. 启动 Cloudflare 前端隧道
echo [3/4] 创建公网隧道...
start "Tunnel-Port5173" cmd /k "cd /d F:\22\crop_disease_diagnosis-main && cloudflared.exe tunnel --url http://localhost:5173"
timeout /t 2 /nobreak >nul

REM 4. 启动 Cloudflare 后端隧道
start "Tunnel-Port8000" cmd /k "cd /d F:\22\crop_disease_diagnosis-main && cloudflared.exe tunnel --url http://localhost:8000"

echo.
echo ============================================
echo   ✅ 启动完成！
echo.
echo   本地前端: http://localhost:5173
echo   本地后端: http://localhost:8000
echo.
echo   公网地址会在弹出的两个隧道窗口中显示
echo   (找 trycloudflare.com 结尾的链接)
echo ============================================
echo.
pause
