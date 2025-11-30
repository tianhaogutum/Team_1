# 启动指南 (Start Guide)

## 📋 前置要求

- **Python**: 3.9+ (推荐 3.11+)
- **Node.js**: 18+ 
- **包管理器**: pnpm 或 npm

---

## 🚀 快速启动

### 方式一：分别启动（开发模式推荐）

#### 1. 启动后端 (Backend)

```bash
# 进入后端目录
cd backend

# 激活虚拟环境（如果已创建）
source venv/bin/activate  # macOS/Linux
# 或
# venv\Scripts\activate  # Windows

# 如果没有虚拟环境，先创建
python -m venv venv
source venv/bin/activate

# 安装依赖（首次运行）
pip install -r requirements.txt

# 运行数据库迁移（首次运行）
alembic upgrade head

# 启动后端服务器
uvicorn app.main:app --reload --port 8000
```

**后端访问地址：**
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/healthz
- API 基础 URL: http://localhost:8000

#### 2. 启动前端 (Frontend)

打开**新的终端窗口**：

```bash
# 进入前端目录
cd frontend

# 安装依赖（首次运行）
pnpm install
# 或
# npm install

# 启动开发服务器
pnpm run dev
# 或
# npm run dev
```

**前端访问地址：**
- 应用: http://localhost:3000

---

### 方式二：使用开发脚本（一键启动后端）

```bash
# 在项目根目录
./scripts/dev.sh
```

这会启动后端服务器（端口 8000），但前端仍需单独启动。

---

## 🔧 首次设置（如果还没做过）

### 后端首次设置

```bash
cd backend

# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖（可选）

# 3. 运行数据库迁移
alembic upgrade head

# 4. （可选）填充测试数据
python scripts/seed_db.py
```

### 前端首次设置

```bash
cd frontend

# 安装依赖
pnpm install
# 或
# npm install
```

---

## 🌐 环境变量配置

### 后端环境变量

后端使用默认配置即可运行。如需自定义，创建 `backend/.env` 文件：

```bash
cd backend
cp env.example .env
# 然后编辑 .env 文件
```

**可选配置：**
- `DATABASE_URL`: 数据库连接 URL（默认使用 SQLite）

### 前端环境变量

前端默认连接到 `http://localhost:8000`。如需修改，创建 `frontend/.env.local` 文件：

```bash
cd frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

---

## 📝 常用命令

### 后端命令

```bash
# 启动开发服务器（带热重载）
uvicorn app.main:app --reload --port 8000

# 运行数据库迁移
alembic upgrade head

# 创建新的迁移文件
alembic revision --autogenerate -m "描述信息"

# 填充测试数据
python scripts/seed_db.py

# 计算路线 XP
python scripts/calculate_route_xp.py
```

### 前端命令

```bash
# 开发模式（热重载）
pnpm run dev

# 构建生产版本
pnpm run build

# 启动生产服务器
pnpm run start

# 代码检查
pnpm run lint
```

---

## 🐛 常见问题

### 1. 后端启动失败

**问题**: `ModuleNotFoundError` 或 `command not found: uvicorn`

**解决**:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 前端启动失败

**问题**: `pnpm: command not found`

**解决**:
```bash
# 安装 pnpm
npm install -g pnpm

# 或使用 npm
npm install
npm run dev
```

### 3. 数据库连接错误

**问题**: 数据库文件不存在

**解决**:
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 4. 端口被占用

**问题**: `Address already in use`

**解决**:
- 后端：修改端口 `uvicorn app.main:app --reload --port 8001`
- 前端：修改端口（在 `package.json` 中或使用 `-p` 参数）

---

## 📊 开发工作流

### 典型开发流程

1. **启动后端**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --port 8000
   ```

2. **启动前端**（新终端）
   ```bash
   cd frontend
   pnpm run dev
   ```

3. **访问应用**
   - 前端: http://localhost:3000
   - API 文档: http://localhost:8000/docs

4. **修改代码**
   - 后端：自动重载（`--reload` 参数）
   - 前端：自动重载（Next.js 默认）

---

## ✅ 验证启动成功

### 后端验证

访问 http://localhost:8000/healthz，应该返回：
```json
{"status": "ok"}
```

### 前端验证

访问 http://localhost:3000，应该看到应用界面。

### API 验证

访问 http://localhost:8000/docs，应该看到 Swagger API 文档。

---

## 🎯 下一步

- 查看 `README.md` 了解项目结构
- 查看 `Tianhao_dev.md` 了解待实现功能
- 查看 API 文档: http://localhost:8000/docs

