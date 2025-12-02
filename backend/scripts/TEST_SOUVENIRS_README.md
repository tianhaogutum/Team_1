# Souvenir API 测试脚本使用说明

## 概述

`test_souvenirs.py` 是一个全面的测试脚本，用于测试Souvenir API的所有功能。

## 功能测试

脚本会测试以下功能：

1. **健康检查** - 验证后端服务是否运行
2. **创建Profile** - 创建测试用户profile
3. **获取路线** - 获取一个可用的路线用于测试
4. **创建Souvenir** - 完成路线并创建souvenir
5. **获取Souvenirs列表** - 测试列表API
6. **获取单个Souvenir** - 测试单个souvenir详情API
7. **排序功能** - 测试不同的排序选项（newest, oldest, xp_high, xp_low）
8. **Profile更新验证** - 验证XP和Level是否正确更新

## 使用方法

### 前置条件

1. 确保后端服务正在运行：
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. 确保数据库已初始化并有路线数据

### 运行测试

```bash
# 从backend目录运行
cd backend
python scripts/test_souvenirs.py

# 或者直接运行
python backend/scripts/test_souvenirs.py
```

### 预期输出

脚本会显示：
- ✅ 成功测试（绿色）
- ❌ 失败测试（红色）
- ⚠️  警告信息（黄色）
- ℹ️  信息消息（蓝色）

## 测试流程

1. **健康检查** - 验证后端可访问
2. **创建Profile** - 创建测试用户（可能需要等待AI生成welcome summary）
3. **获取路线** - 从数据库获取一个路线
4. **创建Souvenir** - 完成路线，创建souvenir（包括AI摘要生成）
5. **验证数据** - 检查souvenir是否正确创建和保存
6. **测试排序** - 验证不同的排序选项
7. **验证更新** - 确认用户profile的XP和Level已更新

## 注意事项

- **超时设置**: 脚本使用120秒超时，因为AI生成可能需要时间
- **数据清理**: 测试会创建真实的数据库记录，测试后可能需要手动清理
- **依赖**: 需要Ollama服务运行（用于AI摘要生成），如果Ollama不可用，会使用fallback摘要

## 故障排除

### 连接错误
```
❌ 无法连接到后端服务
```
**解决方案**: 确保后端服务正在运行在 `http://localhost:8000`

### 超时错误
```
⚠️  请求超时（AI生成可能需要更长时间）
```
**解决方案**: 
- 检查Ollama服务是否运行
- 增加TIMEOUT值
- 检查网络连接

### 没有路线
```
❌ 没有可用的路线
```
**解决方案**: 运行数据导入脚本：
```bash
python scripts/import_outdooractive_routes.py
```

### Profile创建失败
```
❌ 创建Profile失败
```
**解决方案**: 
- 检查数据库连接
- 查看后端日志
- 确认数据库表已创建

## 示例输出

```
================================================================================
                        Souvenir API 功能测试                        
================================================================================

ℹ️  Base URL: http://localhost:8000
ℹ️  Timeout: 120.0秒

1. 健康检查
   ✅ 后端服务正常 (Status: 200)

2. 创建测试用户Profile
   ✅ Profile创建成功!
   ℹ️  Profile ID: 1

3. 获取测试路线
   ✅ 获取路线成功!
   ℹ️  Route ID: 1362328

4. 创建Souvenir（完成路线）
   ✅ Souvenir创建成功!
   ℹ️  Souvenir ID: 1
   ℹ️  Total XP Gained: 180

...
```

## 清理测试数据

测试完成后，如果需要清理测试数据：

```bash
# 删除测试profile（会级联删除souvenirs）
python scripts/delete_all_users.py
```

或者使用SQL：
```sql
DELETE FROM souvenirs WHERE demo_profile_id = <test_profile_id>;
DELETE FROM demo_profiles WHERE id = <test_profile_id>;
```

