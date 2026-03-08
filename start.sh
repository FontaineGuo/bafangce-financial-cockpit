#!/bin/bash

# 八方策金融座舱 - 启动脚本

echo "========================================"
echo "  八方策金融座舱 - 启动脚本"
echo "========================================"
echo ""

# 检查依赖
echo "[信息] 检查系统依赖..."

if ! command -v node &> /dev/null; then
    echo "[错误] Node.js 未安装"
    exit 1
fi
echo "[成功] Node.js 已安装"

if ! command -v npm &> /dev/null; then
    echo "[错误] npm 未安装"
    exit 1
fi
echo "[成功] npm 已安装"

if ! command -v uv &> /dev/null; then
    echo "[错误] uv 包管理器未安装"
    echo "[提示] 请安装 uv: pip install uv 或 curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo "[成功] uv 包管理器已安装"

# 检查前端依赖
echo ""
echo "[信息] 检查前端依赖..."

if [ ! -d "frontend/node_modules" ]; then
    echo "[警告] 前端依赖未安装，正在安装..."
    cd frontend && npm install && cd ..
    echo "[成功] 前端依赖安装完成"
else
    echo "[成功] 前端依赖已安装"
fi

# 检查后端依赖
echo ""
echo "[信息] 检查后端依赖..."

cd backend
if [ ! -f "uv.lock" ]; then
    echo "[错误] 后端 uv.lock 文件不存在"
    cd ..
    exit 1
fi
echo "[成功] 后端 uv 配置文件存在"

# 同步依赖（如果需要）
if ! uv run python -c "import akshare" &> /dev/null 2>&1; then
    echo "[信息] 后端依赖未完全安装，正在同步..."
    uv sync
    echo "[成功] 后端依赖同步完成"
else
    echo "[成功] 后端依赖已安装"
fi
cd ..

# 清理端口占用
echo ""
echo "[信息] 清理端口占用..."

if [ -f "backend/kill_server.py" ]; then
    cd backend && uv run python kill_server.py && cd ..
    echo "[成功] 端口清理完成"
else
    echo "[信息] 端口清理脚本不存在"
fi

# 启动后端服务器
echo ""
echo "[信息] 正在启动后端服务器..."
echo "[信息] 后端服务器将在 http://localhost:8000 启动"
echo "[信息] API文档: http://localhost:8000/docs"
echo ""

cd backend
uv run python run.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端开发服务器
echo ""
echo "[信息] 正在启动前端开发服务器..."
echo "[信息] 前端服务器将在 http://localhost:5173 启动"
echo ""

cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
sleep 2

echo ""
echo "========================================"
echo "  启动完成！"
echo "========================================"
echo ""
echo "[信息] 前端: http://localhost:5173"
echo "[信息] 后端: http://localhost:8000"
echo "[信息] API文档: http://localhost:8000/docs"
echo ""
echo "[提示] 按 Ctrl+C 停止所有服务器"
echo "========================================"

# 等待进程
trap 'kill $BACKEND_PID $FRONTEND_PID; exit' INT TERM

wait $BACKEND_PID $FRONTEND_PID