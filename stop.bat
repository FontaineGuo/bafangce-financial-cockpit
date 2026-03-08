@echo off
chcp 65001 >nul
title 八方策金融座舱 - 停止脚本

echo ========================================
echo   八方策金融座舱 - 停止脚本
echo ========================================
echo.

echo [信息] 正在查找并停止所有相关进程...
echo.

tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq 后端服务器*" 2>nul | find /I "python.exe" >nul && (
    echo [信息] 正在停止后端服务器...
    taskkill /FI "WINDOWTITLE eq 后端服务器*" /F >nul 2>&1
    echo [成功] 后端服务器已停止
) || (
    echo [信息] 后端服务器未运行
)

tasklist /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq 前端服务器*" 2>nul | find /I "node.exe" >nul && (
    echo [信息] 正在停止前端服务器...
    taskkill /FI "WINDOWTITLE eq 前端服务器*" /F >nul 2>&1
    echo [成功] 前端服务器已停止
) || (
    echo [信息] 前端服务器未运行
)

echo.
echo [信息] 清理端口占用...

cd backend
where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    uv run python kill_server.py
    echo [成功] 端口清理完成
) else (
    echo [警告] uv 未找到，跳过端口清理
)

cd ..
echo.
echo ========================================
echo   停止完成！
echo ========================================

pause