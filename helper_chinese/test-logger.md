# 前端日志系统使用说明

## 功能特性

✅ **localStorage 持久化**：所有 ERROR 和 WARN 级别的日志自动保存
✅ **自动发送到后端**：每 30 秒自动发送日志到后端 API
✅ **页面卸载时发送**：页面关闭前自动发送待发送的日志
✅ **日志导出**：可以导出日志为 JSON 文件

## 在浏览器控制台测试

```javascript
// 1. 测试错误日志（会自动保存到 localStorage 并发送到后端）
logger.error('测试错误信息', { errorCode: 500, details: 'Something went wrong' }, 'TestComponent', 'TEST_ERROR');

// 2. 测试警告日志
logger.warn('测试警告信息', { warning: 'This is a warning' }, 'TestComponent', 'TEST_WARN');

// 3. 查看所有持久化的日志
console.log(logger.getPersistedLogs());

// 4. 查看只查看错误日志
console.log(logger.getPersistedLogs('error'));

// 5. 导出日志为 JSON 文件（会自动下载）
logger.downloadPersistedLogs();

// 6. 手动发送待发送的日志到后端
await logger.sendLogsToBackend();

// 7. 清空持久化的日志
logger.clearPersistedLogs();
```

## 检查 localStorage

```javascript
// 查看保存的日志
const logs = localStorage.getItem('trailsaga-frontend-logs');
console.log(JSON.parse(logs));
```

## 检查后端日志

```bash
# 查看前端专用日志文件
tail -f backend/logs/frontend-logs.log

# 查看应用日志（包含前端错误）
tail -f backend/logs/app.log

# 查看错误日志
tail -f backend/logs/error.log
```

## 实际使用场景

当前端发生错误时，日志会自动：
1. 保存到 localStorage（即使页面刷新也不会丢失）
2. 每 30 秒自动发送到后端
3. 页面关闭前也会发送

这样你就能在后端日志文件中看到所有前端错误了！
