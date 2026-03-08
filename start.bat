@echo off
chcp 65001 >nul
title 八方策金融座舱 - 启动脚本

echo ========================================
echo   八方策金融座舱 - 启动脚本
echo ========================================
echo.

echo [信息] 检查 uv 包管理器...
where uv >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] uv 未安装
    echo [提示] 请安装 uv: pip install uv
    pause
    exit /b 1
)
echo [成功] uv 已安装

echo.
echo [信息] 正在启动后端服务器...
start "后端服务器" cmd /k "cd backend && uv run python run.py"

timeout /t 3 >nul

echo [信息] 正在启动前端开发服务器...
start "前端服务器" cmd /k "cd frontend && npm run dev"

timeout /t 2 >nul

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo [信息] 前端: http://localhost:5173
echo [信息] 后端: http://localhost:8000
echo [信息] API文档: http://localhost:8000/docs
echo.
echo [提示] 关闭对应的命令行窗口来停止服务器
echo ========================================

pause