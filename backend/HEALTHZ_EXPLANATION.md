# 为什么使用 `/healthz` 作为健康检查端点？

## 命名原因

### 1. **行业标准**
`/healthz` 是 Kubernetes 和云原生应用中的标准健康检查端点命名约定。

### 2. **避免与业务路由冲突**
- `/health` 可能被业务逻辑使用
- `/healthz` 明确表示这是一个系统监控端点
- 以 `z` 结尾的命名约定在云原生生态系统中广泛使用

### 3. **常见变体**
- `/healthz` - Kubernetes 标准（我们使用的）
- `/health` - 简单版本
- `/readyz` - 就绪检查（readiness probe）
- `/livez` - 存活检查（liveness probe）

## 在我们的项目中的使用

```python
# backend/app/main.py
@app.get("/healthz", tags=["health"])
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
```

### 用途：
1. **监控系统健康**：外部监控工具可以定期检查这个端点
2. **负载均衡器检查**：确保服务正常运行
3. **开发调试**：快速检查后端是否启动
4. **CI/CD 测试**：自动化测试中验证服务可用性

## 为什么不是 `/health`？

虽然 `/health` 更直观，但：
- `/healthz` 遵循 Kubernetes 约定
- 避免与可能的业务路由 `/health` 冲突
- 在云原生环境中更常见

## 可以改成 `/health` 吗？

当然可以！如果你想改成 `/health`，只需要修改：

```python
# backend/app/main.py
@app.get("/health", tags=["health"])  # 改成 /health
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
```

然后更新测试脚本和文档中的引用即可。

## 总结

- `/healthz` 是云原生标准命名
- 用于系统健康检查，不涉及业务逻辑
- 简单、快速、可靠
- 可以改成 `/health`，但 `/healthz` 更符合行业惯例

