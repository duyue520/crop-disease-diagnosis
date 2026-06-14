@echo off
chcp 65001 >nul
title 🌿 叶片病害诊断 — 一键启动

echo ============================================
echo   🌿 叶片病害诊断系统 一键启动
echo ============================================
echo.

REM 杀掉旧进程
echo [1/5] 清理旧进程...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM 启动后端
echo [2/5] 启动后端 API...
start "Backend" cmd /c "cd /d F:\22\crop_disease_diagnosis-main && D:\anaconda\envs\pythonproject\python -m server.main"
echo   等待后端就绪...
timeout /t 6 /nobreak >nul

REM 启动前端
echo [3/5] 启动前端...
start "Frontend" cmd /c "cd /d F:\github好看网站\leleo-home-page-main && npx vite --host 0.0.0.0 --port 5173"
timeout /t 4 /nobreak >nul

REM 启动隧道
echo [4/5] 启动公网隧道...
start "Tunnel-Backend" cmd /c "cd /d F:\22\crop_disease_diagnosis-main && cloudflared.exe tunnel --url http://localhost:8000"
echo   等待隧道建立（约10秒）...
timeout /t 12 /nobreak >nul

REM 自动部署
echo [5/5] 自动部署到腾讯云...
cd /d F:\22\crop_disease_diagnosis-main
D:\anaconda\envs\pythonproject\python update_deploy.py

echo.
echo ============================================
echo   ✅ 启动完成！
echo.
echo   🌐 网站地址（永远不变）:
echo   https://duyue-d4gw2qp01d8a7bd6e-1433783466.tcloudbaseapp.com
echo.
echo   把这个地址发给别人就能用了
echo ============================================
pause
