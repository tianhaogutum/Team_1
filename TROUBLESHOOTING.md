# 前端连接后端失败 - 故障排除指南

## 错误信息
```
ApiError: Network error: Could not connect to the server. 
Please check if the backend is running.
```

## 快速解决方案

### 1. 检查后端是否运行

```bash
# 检查后端进程
ps aux | grep uvicorn

# 检查端口
lsof -i :8000

# 测试后端健康检查
curl http://localhost:8000/healthz
```

### 2. 重启后端

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 3. 检查前端 API 配置

确保前端正确配置了 API URL：

**创建或检查 `frontend/.env.local`：**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. 检查 CORS 配置

后端 `backend/app/main.py` 应该允许前端端口：
- `http://localhost:3000` ✅
- `http://localhost:3001` ✅

### 5. 检查浏览器控制台

打开浏览器开发者工具（F12），查看：
- Network 标签：查看请求是否发送
- Console 标签：查看错误信息

### 6. 常见问题

#### 问题 A：后端卡住（GenAI 调用超时）

**症状：** 后端进程运行，但不响应请求

**解决：**
1. 检查 Ollama 是否运行：`curl http://localhost:11434/api/tags`
2. 如果 Ollama 未运行，启动它：`brew services start ollama`
3. 重启后端

#### 问题 A1：Ollama 返回 503 Service Unavailable

**症状：** 后端日志显示 `503 Service Unavailable` 错误，但 `curl` 命令可以正常工作

**原因：** IPv6/IPv4 解析问题。Ollama 只监听 IPv4，但 Python 的 httpx 可能尝试使用 IPv6

**解决：**
1. 运行诊断脚本：`python backend/scripts/diagnose_ollama.py`
2. 如果发现问题，修改配置使用 `127.0.0.1` 而不是 `localhost`：
   - 在 `backend/.env` 中添加：`OLLAMA_API_URL=http://127.0.0.1:11434/api/generate`
   - 或者修改 `backend/app/settings.py` 中的默认值（已修复）
3. 重启后端服务

#### 问题 B：端口冲突

**症状：** 端口 8000 被占用

**解决：**
```bash
# 查找占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn app.main:app --reload --port 8001
# 然后更新 frontend/.env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8001
```

#### 问题 C：前端环境变量未加载

**症状：** 前端使用默认 URL，但后端在不同端口

**解决：**
1. 创建 `frontend/.env.local`：
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
2. 重启前端开发服务器

#### 问题 D：CORS 错误

**症状：** 浏览器控制台显示 CORS 错误

**解决：**
1. 检查前端运行端口（通常是 3000）
2. 确保后端 `main.py` 的 CORS 配置包含该端口
3. 重启后端

## 完整测试流程

### 步骤 1：测试后端健康检查
```bash
curl http://localhost:8000/healthz
# 应该返回: {"status":"ok"}
```

### 步骤 2：测试创建用户资料
```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "fitness": "beginner",
    "type": ["history-culture"],
    "narrative": "adventure"
  }'
```

### 步骤 3：检查前端配置
```bash
# 在 frontend 目录
cat .env.local
# 应该显示: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 步骤 4：检查浏览器网络请求
1. 打开浏览器开发者工具（F12）
2. 切换到 Network 标签
3. 刷新页面
4. 查看是否有对 `http://localhost:8000` 的请求
5. 检查请求状态和错误信息

## Ollama 诊断工具

如果遇到 Ollama 相关问题，可以使用内置的诊断脚本：

```bash
cd backend
source venv/bin/activate
python scripts/diagnose_ollama.py
```

该脚本会检查：
1. Ollama 服务是否运行
2. 所需模型是否已安装
3. API 连接是否正常
4. 生成功能是否工作

## 如果问题仍然存在

1. **查看后端日志**：检查后端终端输出的错误信息
2. **查看前端日志**：检查浏览器控制台的完整错误堆栈
3. **检查数据库**：确保数据库文件存在且可访问
4. **检查 Ollama**：
   - 运行诊断脚本：`python backend/scripts/diagnose_ollama.py`
   - 确保 LLM 服务正常运行
   - 如果使用 `localhost` 遇到问题，尝试使用 `127.0.0.1`

## 联系支持

如果以上步骤都无法解决问题，请提供：
- 后端终端完整错误日志
- 浏览器控制台完整错误信息
- 网络请求的详细信息（从 Network 标签）

