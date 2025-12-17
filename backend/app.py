# FastAPI主应用
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据库初始化函数
from backend.core.database import create_tables, add_category_column_to_holdings

# 创建FastAPI应用
app = FastAPI(
    title="八方策金融座舱API",
    description="金融投资组合管理和资产配置API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化 - 使用新的lifespan事件处理方式
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期事件处理"""
    # 启动时执行
    print("正在初始化数据库...")
    create_tables()
    add_category_column_to_holdings()
    print("数据库初始化完成！")
    
    yield  # 应用运行中
    
    # 关闭时执行（如果需要）
    print("应用正在关闭...")

# 重新创建FastAPI应用，使用新的lifespan
app = FastAPI(
    title="八方策金融座舱API",
    description="金融投资组合管理和资产配置API",
    version="1.0.0",
    lifespan=lifespan
)

# 重新配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  
# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "message": "八方策金融座舱API服务正常运行中"}

# 导入API路由
# 注意：需要在创建app之后导入，避免循环导入
from backend.api import portfolio

# 注册路由
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])

if __name__ == "__main__":
    """主程序入口"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
