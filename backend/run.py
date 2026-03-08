"""
启动脚本
"""
import uvicorn


if __name__ == "__main__":


    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="debug",  # 改为debug级别以显示更多信息
        access_log=True,  # 显示访问日志
    )
