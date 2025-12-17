# 日志系统使用指南

本文档介绍前后端统一的日志系统，帮助开发者进行调试和问题排查。

## 目录

- [后端日志系统](#后端日志系统)
- [前端日志系统](#前端日志系统)
- [日志级别说明](#日志级别说明)
- [最佳实践](#最佳实践)

## 后端日志系统

### 配置

日志配置在 `backend/app/settings.py` 中，支持通过环境变量配置：

```bash
# 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# 是否启用文件日志
LOG_ENABLE_FILE=true

# 是否启用控制台日志
LOG_ENABLE_CONSOLE=true

# 是否使用详细格式（包含函数名和行号）
LOG_DETAILED_FORMAT=true
```

### 日志文件位置

日志文件存储在 `backend/logs/` 目录：

- `app.log` - 所有级别的日志
- `error.log` - 仅 WARNING 及以上级别
- `debug.log` - 仅 DEBUG 级别

日志文件会自动轮转，单个文件最大 10MB，保留 5 个备份。

### 使用方式

#### 基本使用

```python
from app.logger import get_logger

logger = get_logger(__name__)

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息", exc_info=True)  # exc_info=True 会记录堆栈跟踪
```

#### 记录 HTTP 请求

```python
from app.logger import log_request
import time

start_time = time.time()
# ... 处理请求 ...
duration_ms = (time.time() - start_time) * 1000

log_request(
    logger,
    "POST",
    "/api/profiles",
    status_code=201,
    duration_ms=duration_ms,
    user_id=profile_id
)
```

#### 记录数据库操作

```python
from app.logger import log_database_operation
import time

start_time = time.time()
# ... 数据库操作 ...
duration_ms = (time.time() - start_time) * 1000

log_database_operation(
    logger,
    "INSERT",
    "DemoProfile",
    record_id=new_profile.id,
    duration_ms=duration_ms
)
```

#### 记录外部 API 调用

```python
from app.logger import log_api_call
import time

start_time = time.time()
# ... API 调用 ...
duration_ms = (time.time() - start_time) * 1000

log_api_call(
    logger,
    "Ollama",
    "http://127.0.0.1:11434/api/generate",
    method="POST",
    duration_ms=duration_ms,
    success=True,
    model="llama3.1:8b"
)
```

#### 记录业务逻辑

```python
from app.logger import log_business_logic

log_business_logic(
    logger,
    "创建",
    "用户档案",
    entity_id=profile_id,
    fitness=questionnaire.fitness,
    narrative=questionnaire.narrative
)
```

### 日志格式

详细格式示例：
```
2024-01-15 10:30:45 | INFO     | app.api.v1.profiles | submit_questionnaire:93 | 📝 收到用户问卷提交
```

简单格式示例：
```
2024-01-15 10:30:45 | INFO     | 📝 收到用户问卷提交
```

## 前端日志系统

### 使用方式

#### 基本使用

```typescript
import { logger } from '@/lib/logger';

// 不同级别的日志
logger.debug('调试信息', data, 'ComponentName', 'ACTION');
logger.info('一般信息', data, 'ComponentName', 'ACTION');
logger.warn('警告信息', data, 'ComponentName', 'ACTION');
logger.error('错误信息', error, 'ComponentName', 'ACTION');
```

#### 记录 API 请求/响应

```typescript
// 在 API client 中自动记录，也可以手动记录
logger.logApiRequest('POST', '/api/profiles', requestData, 'ComponentName');
logger.logApiResponse('POST', '/api/profiles', 201, 150.5, responseData, 'ComponentName');
logger.logApiError('POST', '/api/profiles', error, 'ComponentName');
```

#### 记录组件生命周期

```typescript
useEffect(() => {
  logger.logComponentLifecycle('MyComponent', 'mount', props);
  
  return () => {
    logger.logComponentLifecycle('MyComponent', 'unmount');
  };
}, []);
```

#### 记录业务逻辑

```typescript
logger.logBusinessLogic(
  '创建',
  '用户档案',
  profileId,
  { fitness, narrative },
  'ComponentName'
);
```

#### 记录用户操作

```typescript
const handleClick = () => {
  logger.logUserAction('点击按钮', { buttonId: 'submit' }, 'ComponentName');
  // ... 处理逻辑 ...
};
```

#### 记录性能指标

```typescript
const startTime = performance.now();
// ... 操作 ...
const duration = performance.now() - startTime;

logger.logPerformance('数据加载', duration, 'ComponentName', { dataSize: 100 });
```

#### 日志分组

```typescript
logger.group('复杂操作', 'ComponentName');
logger.debug('步骤 1');
logger.debug('步骤 2');
logger.groupEnd();
```

### 日志历史

```typescript
// 获取日志历史
const history = logger.getHistory('error', 10);  // 获取最近 10 条错误日志

// 导出日志历史（用于调试）
const exported = logger.exportHistory();

// 清空日志历史
logger.clearHistory();
```

### 环境行为

- **开发环境**: 输出所有级别的日志
- **生产环境**: 只输出 WARN 和 ERROR 级别的日志

## 日志级别说明

### DEBUG
- 用途：详细的调试信息
- 示例：函数参数、中间状态、详细的执行流程
- 生产环境：不输出

### INFO
- 用途：一般信息，记录正常流程
- 示例：请求处理、业务操作、状态变更
- 生产环境：输出

### WARN
- 用途：警告信息，可能的问题但不影响功能
- 示例：降级处理、备用方案、配置问题
- 生产环境：输出

### ERROR
- 用途：错误信息，需要关注的问题
- 示例：异常捕获、失败操作、系统错误
- 生产环境：输出

## 最佳实践

### 1. 使用合适的日志级别

```python
# ✅ 正确
logger.debug(f"处理用户请求: user_id={user_id}, data={data}")  # 详细调试信息
logger.info(f"用户档案创建成功: profile_id={profile_id}")  # 正常流程
logger.warning(f"GenAI 服务不可用，使用备用方案")  # 警告
logger.error(f"数据库操作失败", exc_info=True)  # 错误

# ❌ 错误
logger.info(f"循环变量 i={i}")  # 应该用 debug
logger.error(f"用户登录成功")  # 应该用 info
```

### 2. 包含足够的上下文信息

```python
# ✅ 正确
logger.info(f"生成路线故事: route_id={route_id}, narrative_style={narrative_style}, force_regenerate={force_regenerate}")

# ❌ 错误
logger.info("生成故事")  # 缺少上下文
```

### 3. 使用结构化日志

```python
# ✅ 正确
log_business_logic(
    logger,
    "创建",
    "用户档案",
    entity_id=profile_id,
    fitness=questionnaire.fitness,
    narrative=questionnaire.narrative
)

# ❌ 错误
logger.info(f"创建用户档案: {profile_id}, {questionnaire.fitness}, {questionnaire.narrative}")
```

### 4. 记录性能指标

```python
# ✅ 正确
start_time = time.time()
# ... 操作 ...
duration_ms = (time.time() - start_time) * 1000
logger.debug(f"操作耗时: {duration_ms:.2f}ms")
```

### 5. 错误日志包含堆栈跟踪

```python
# ✅ 正确
try:
    # ... 操作 ...
except Exception as e:
    logger.error(f"操作失败: {str(e)}", exc_info=True)  # 包含堆栈跟踪
```

### 6. 避免敏感信息

```python
# ❌ 错误
logger.info(f"用户密码: {password}")  # 不要记录敏感信息

# ✅ 正确
logger.info(f"用户登录: user_id={user_id}")  # 只记录必要信息
```

### 7. 前端日志组件标识

```typescript
// ✅ 正确
logger.info('操作成功', data, 'MyComponent', 'HANDLE_SUBMIT');

// ❌ 错误
logger.info('操作成功');  // 缺少组件和操作标识
```

## 常见场景示例

### 后端：API 端点

```python
@router.post("/api/profiles", response_model=ProfileCreateResponse)
async def submit_questionnaire(
    questionnaire: ProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> ProfileCreateResponse:
    import time
    start_time = time.time()
    
    logger.info("=" * 80)
    logger.info("📝 收到用户问卷提交")
    logger.debug(f"问卷数据: fitness={questionnaire.fitness}, type={questionnaire.type}")
    
    try:
        # ... 处理逻辑 ...
        duration_ms = (time.time() - start_time) * 1000
        log_request(logger, "POST", "/api/profiles", status_code=201, duration_ms=duration_ms)
        logger.info(f"✅ 用户档案创建成功: profile_id={new_profile.id}")
        return response
    except Exception as e:
        logger.error(f"❌ 创建用户档案失败: {str(e)}", exc_info=True)
        raise
```

### 前端：组件操作

```typescript
const handleSubmit = async () => {
  const startTime = performance.now();
  
  logger.logUserAction('提交表单', { formType: 'questionnaire' }, 'QuestionnaireForm');
  
  try {
    const response = await apiClient.post('/api/profiles', formData);
    
    const duration = performance.now() - startTime;
    logger.logPerformance('提交表单', duration, 'QuestionnaireForm');
    logger.logBusinessLogic('创建', '用户档案', response.id, { fitness: formData.fitness }, 'QuestionnaireForm');
    
    return response;
  } catch (error) {
    logger.error('提交表单失败', error, 'QuestionnaireForm', 'HANDLE_SUBMIT');
    throw error;
  }
};
```

## 调试技巧

### 1. 查看特定组件的日志

```typescript
// 前端：使用浏览器控制台过滤
// 在控制台输入：logger.getHistory().filter(log => log.component === 'MyComponent')
```

### 2. 查看错误日志

```bash
# 后端：查看错误日志文件
tail -f backend/logs/error.log

# 或使用 grep 过滤
grep "ERROR" backend/logs/app.log
```

### 3. 实时监控日志

```bash
# 后端：实时查看所有日志
tail -f backend/logs/app.log

# 只查看特定模块的日志
tail -f backend/logs/app.log | grep "app.api.v1.profiles"
```

### 4. 导出日志用于分析

```typescript
// 前端：在浏览器控制台
const logs = logger.exportHistory();
console.log(logs);
// 复制输出用于分析
```

## 总结

- 后端使用 `app.logger` 模块，支持文件和控制台输出
- 前端使用 `@/lib/logger` 模块，自动适配开发/生产环境
- 使用合适的日志级别和结构化日志
- 包含足够的上下文信息
- 记录性能指标和错误堆栈
- 避免记录敏感信息

更多示例请参考代码中的实际使用：
- 后端：`backend/app/api/v1/profiles.py`, `backend/app/services/genai_service.py`
- 前端：`frontend/components/route-recommendations.tsx`, `frontend/lib/api-client.ts`

