# 启动脚本使用指南

## 📋 概述

项目提供了多个启动脚本，支持不同操作系统和使用场景：

- **start.bat** (Windows) - 推荐使用，双击即可启动
- **start.sh** (Linux/Mac) - 支持 shell 脚本启动
- **start.py** (跨平台) - 功能完整的 Python 脚本

## 🚀 快速启动

### Windows 用户

#### 方法1: 双击启动（推荐）
1. 双击 `start.bat`
2. 等待服务器启动
3. 访问:
   - 前端: http://localhost:5173
   - 后端: http://localhost:8000
   - API文档: http://localhost:8000/docs

#### 方法2: Python 脚本启动
```bash
python start.py
```

#### 方法3: 命令行手动启动
```bash
# 启动后端 (使用 uv)
cd backend
uv run python run.py

# 新开命令行窗口启动前端
cd frontend
npm run dev
```

### Linux/Mac 用户

#### 方法1: Shell 脚本启动
```bash
chmod +x start.sh
./start.sh
```

#### 方法2: Python 脚本启动
```bash
python start.py
```

#### 方法3: 命令行手动启动
```bash
# 启动后端 (使用 uv)
cd backend
uv run python run.py

# 新开终端启动前端
cd frontend
npm run dev
```

## 🛑 停止服务器

### Windows 用户

#### 方法1: 双击停止脚本
1. 双击 `stop.bat`
2. 脚本会自动停止所有相关进程

#### 方法2: 手动停止
1. 关闭对应的命令行窗口

### Linux/Mac 用户

#### 方法1: 命令行停止
```bash
# 按 Ctrl+C 停止所有服务器
```

#### 方法2: 手动查找并停止
```bash
# 查找并停止后端进程
pkill -f "uv run python run.py"

# 查找并停止前端进程
pkill -f "npm run dev"
```

## 📋 启动脚本功能说明

### start.bat (Windows 批处理)
**功能:**
- ✅ 检查 uv 包管理器安装
- ✅ 自动启动后端服务器 (使用 uv)
- ✅ 自动启动前端开发服务器
- ✅ 显示启动信息和访问地址
- ✅ 在独立窗口中运行

**特点:**
- 🚀 双击即可启动，无需命令行操作
- 🔧 使用 uv 管理后端依赖
- 📝 显示详细的启动信息

### start.sh (Linux/Mac Shell)
**功能:**
- ✅ 检查系统依赖 (Node.js, npm, uv)
- ✅ 检查项目依赖
- ✅ 自动同步前端依赖（如需要）
- ✅ 自动同步后端依赖（使用 uv sync）
- ✅ 清理端口占用
- ✅ 启动前后端服务器
- ✅ 支持 Ctrl+C 停止所有服务

**特点:**
- 🔍 完善的依赖检查
- 🎯 自动化程度高
- 🔧 使用 uv 管理后端环境
- 🔄 支持优雅停止

### start.py (Python 跨平台)
**功能:**
- ✅ 完整的依赖检查（系统 + 项目）
- ✅ 彩色输出，信息清晰
- ✅ 自动安装前端依赖
- ✅ 使用 uv 管理后端依赖
- ✅ 清理端口占用
- ✅ 启动前后端服务器
- ✅ 监控服务器状态
- ✅ 优雅停止（Ctrl+C）
- ✅ 错误处理和提示

**特点:**
- 🌍 跨平台支持
- 🎨 友好的彩色输出
- 🔍 全面的状态检查
- 🛡️ 健壮的错误处理
- 📝 详细的启动日志
- 🔧 集成 uv 包管理器

## 🔧 关于 uv 包管理器

项目后端使用 **uv** 作为 Python 包管理器，这是现代、快速的 Python 包管理工具。

### uv 的优势
- ⚡ 极快的依赖解析和安装速度
- 🔒 一致的依赖管理（使用 uv.lock）
- 📦 与 pyproject.toml 完美集成
- 🚀 内置虚拟环境管理
- 🛠️ 替代传统的 venv + pip

### 常用 uv 命令
```bash
# 同步依赖（创建/更新虚拟环境）
cd backend
uv sync

# 在虚拟环境中运行命令
uv run python run.py
uv run python -c "print('Hello')"

# 检查 uv 版本
uv --version

# 安装新依赖
uv add <package_name>

# 移除依赖
uv remove <package_name>

# 更新依赖
uv lock --upgrade-package <package_name>
```

## 🔧 故障排除

### 前端启动失败

**问题1: 端口被占用**
```bash
# 查找占用端口的进程
netstat -ano | findstr :5173

# 手动结束进程
taskkill /PID <进程ID> /F
```

**问题2: 依赖未安装**
```bash
cd frontend
npm install
```

### 后端启动失败

**问题1: uv 未安装**
```bash
# Windows
pip install uv

# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**问题2: 依赖未同步**
```bash
cd backend
uv sync
```

**问题3: 端口被占用**
```bash
cd backend
uv run python kill_server.py
```

### 服务器无法连接

**问题1: CORS 错误**
- 检查后端 CORS 配置
- 确认前端请求地址正确

**问题2: 网络连接问题**
- 检查防火墙设置
- 确认端口未被阻止

## 📊 启动后检查清单

### ✅ 后端检查
- [ ] 后端服务器启动成功
- [ ] 可以访问 http://localhost:8000
- [ ] API文档可以打开 http://localhost:8000/docs
- [ ] 数据库连接正常
- [ ] CORS 配置正确
- [ ] uv 依赖同步成功

### ✅ 前端检查
- [ ] 前端服务器启动成功
- [ ] 可以访问 http://localhost:5173
- [ ] 页面正常加载
- [ ] 可以登录系统
- [ ] API请求正常

## 🎯 开发环境配置

### 后端配置
- **端口**: 8000 (可在 `backend/run.py` 中修改)
- **主机**: 0.0.0.0 (允许外部访问)
- **包管理器**: uv (使用 pyproject.toml 和 uv.lock)
- **自动重载**: 已启用 (代码修改自动重启)
- **日志级别**: debug (显示详细信息)

### 前端配置
- **端口**: 5173 (Vite 默认端口)
- **自动重载**: 已启用
- **热更新**: 已启用

## 📝 注意事项

1. **首次启动**: 建议首次启动使用 Python 脚本 `start.py`，它会检查所有依赖
2. **uv 依赖**: 后端使用 uv 管理依赖，首次运行会自动同步
3. **端口冲突**: 如果 8000 或 5173 端口被占用，需要修改配置或关闭占用进程
4. **权限问题**: 确保 uv 和项目文件有正确的执行权限
5. **网络问题**: 如遇网络问题，可检查防火墙和代理设置
6. **日志查看**: 启动后可在对应窗口查看服务器日志

## 🚀 性能优化

### 开发环境
- 后端启用自动重载，方便开发调试
- 前端启用热更新，提高开发效率
- 使用 debug 日志级别，便于问题排查
- uv 提供快速的依赖管理

### 生产环境
- 建议禁用自动重载和 debug 模式
- 使用生产级 Web 服务器（如 gunicorn）
- 启用缓存和压缩功能
- 使用 uv run gunicorn 启动生产服务器

## 📞 获取帮助

如果遇到问题：
1. 检查本文档的故障排除部分
2. 查看服务器日志输出
3. 确认 uv 已正确安装
4. 运行 `uv sync` 确保依赖已同步
5. 检查网络和端口配置

---

**祝开发顺利！** 🎉