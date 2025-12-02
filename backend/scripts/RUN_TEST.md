# 运行 Souvenir 测试脚本

## 快速开始

### 1. 确保后端服务运行

```bash
# 在backend目录
cd backend
source venv/bin/activate  # 如果使用虚拟环境
uvicorn app.main:app --reload
```

### 2. 运行完整测试

```bash
# 在backend目录
python3 scripts/test_souvenirs.py
```

### 3. 运行快速测试（不等待AI）

```bash
python3 scripts/test_souvenirs_quick.py
```

## 测试输出说明

- ✅ **绿色** = 测试成功
- ❌ **红色** = 测试失败
- ⚠️  **黄色** = 警告（可能的问题）
- ℹ️  **蓝色** = 信息消息

## 常见问题

### 问题1: 连接错误
```
❌ 无法连接到后端服务
```
**解决**: 确保后端在 `http://localhost:8000` 运行

### 问题2: 超时
```
⚠️  请求超时（AI生成可能需要更长时间）
```
**解决**: 
- 检查Ollama是否运行: `curl http://localhost:11434/api/tags`
- 如果Ollama不可用，测试仍会继续（使用fallback摘要）

### 问题3: 没有路线数据
```
❌ 没有可用的路线
```
**解决**: 运行数据导入脚本
```bash
python scripts/import_outdooractive_routes.py
```

## 测试流程

1. ✅ 健康检查 - 验证后端可访问
2. ✅ 创建Profile - 创建测试用户（可能需要等待AI）
3. ✅ 获取路线 - 从数据库获取路线
4. ✅ 创建Souvenir - 完成路线并创建souvenir
5. ✅ 获取列表 - 测试souvenirs列表API
6. ✅ 获取单个 - 测试单个souvenir API
7. ✅ 测试排序 - 验证排序功能
8. ✅ 验证更新 - 确认XP和Level更新

## 预期时间

- **快速测试**: 10-30秒
- **完整测试**: 1-3分钟（取决于AI生成速度）

## 清理测试数据

测试完成后，可以清理测试数据：

```bash
# 删除所有用户（会级联删除souvenirs）
python scripts/delete_all_users.py
```

