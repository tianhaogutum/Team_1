# Alembic Migration 文件说明

## 📁 这个目录是什么？

`alembic/versions/` 目录存储的是**数据库版本迁移脚本**。每个文件代表数据库结构的一次变更历史。

## 🔍 文件结构解析

以 `78e3383a93f8_initial_migration_create_all_entities.py` 为例：

### 1. **文件命名规则**

```
{revision_id}_{描述性名称}.py
```

- `78e3383a93f8` = 唯一修订 ID（Alembic 自动生成）
- `initial_migration_create_all_entities` = 人类可读的描述

### 2. **关键字段**

```python
revision: str = '78e3383a93f8'          # 当前 migration 的唯一 ID
down_revision: Union[str, None] = None   # 上一个 migration 的 ID（None 表示这是第一个）
branch_labels: Union[str, Sequence[str], None] = None  # 分支标签（用于并行开发）
depends_on: Union[str, Sequence[str], None] = None     # 依赖的其他 migration
```

### 3. **核心函数**

#### `upgrade()` - 升级函数

- **作用**：将数据库从旧版本升级到新版本
- **执行时机**：运行 `alembic upgrade head` 时
- **内容**：创建表、添加列、修改约束等

#### `downgrade()` - 降级函数

- **作用**：将数据库从新版本回退到旧版本
- **执行时机**：运行 `alembic downgrade -1` 时
- **内容**：删除表、移除列、恢复约束等（与 upgrade 相反的操作）

## 🔗 Migration 链式结构

Migrations 形成一个**链式结构**，通过 `down_revision` 连接：

```
None (初始状态)
  ↓
78e3383a93f8 (创建所有表)
  ↓
abc123def456 (添加新字段)
  ↓
xyz789ghi012 (创建索引)
  ↓
... (更多 migrations)
```

## ⚠️ 开发注意事项

### ✅ **应该做的**

1. **每次修改模型后创建新 migration**

   ```bash
   alembic revision --autogenerate -m "描述性消息"
   ```

2. **检查自动生成的 migration**

   - 自动生成可能不完美，需要人工检查
   - 确保 `upgrade()` 和 `downgrade()` 逻辑正确

3. **使用有意义的描述**

   ```bash
   # ✅ 好的
   alembic revision -m "add_user_email_field"
   alembic revision -m "create_breakpoint_indexes"

   # ❌ 不好的
   alembic revision -m "update"
   alembic revision -m "fix"
   ```

4. **测试 migration**

   ```bash
   # 升级
   alembic upgrade head

   # 降级（测试回滚）
   alembic downgrade -1

   # 再升级回来
   alembic upgrade head
   ```

5. **提交 migration 文件到 Git**
   - Migration 文件是项目的一部分
   - 团队成员需要相同的数据库结构

### ❌ **不应该做的**

1. **不要手动修改已提交的 migration**

   - 如果 migration 已经运行在生产环境，不要修改它
   - 应该创建新的 migration 来修复问题

2. **不要删除 migration 文件**

   - 除非确定从未在生产环境运行过
   - 删除会破坏 migration 链

3. **不要在 migration 中写业务逻辑**

   ```python
   # ❌ 不好：包含业务逻辑
   def upgrade():
       op.add_column('users', sa.Column('email', sa.String()))
       # 不要在这里做数据迁移或业务处理
       session.execute("UPDATE users SET email = ...")

   # ✅ 好：只做结构变更
   def upgrade():
       op.add_column('users', sa.Column('email', sa.String()))
   ```

4. **不要在生产环境直接运行 migration**

   - 先在开发/测试环境验证
   - 生产环境需要备份数据库

5. **不要忽略 `downgrade()` 函数**
   - 必须实现，用于回滚
   - 确保 `downgrade()` 能完全撤销 `upgrade()` 的操作

## 📋 常见工作流程

### 场景 1：添加新字段到 Route 模型

```python
# 1. 修改 models/entities.py
class Route(Base):
    # ... 现有字段 ...
    new_field: Mapped[str | None] = mapped_column(String(100), nullable=True)

# 2. 生成 migration
alembic revision --autogenerate -m "add_new_field_to_routes"

# 3. 检查生成的 migration 文件
# 4. 运行 migration
alembic upgrade head
```

### 场景 2：创建新表

```python
# 1. 在 models/entities.py 中定义新模型
class NewTable(Base):
    __tablename__ = "new_table"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # ...

# 2. 确保在 alembic/env.py 中导入
from app.models import entities  # noqa: F401

# 3. 生成 migration
alembic revision --autogenerate -m "create_new_table"

# 4. 运行 migration
alembic upgrade head
```

### 场景 3：回滚到上一个版本

```bash
# 回滚一个版本
alembic downgrade -1

# 回滚到特定版本
alembic downgrade 78e3383a93f8

# 回滚所有（危险！）
alembic downgrade base
```

## 🔍 查看 Migration 状态

```bash
# 查看当前数据库版本
alembic current

# 查看所有 migrations 历史
alembic history

# 查看需要应用的 migrations
alembic heads
```

## 🎯 最佳实践总结

1. **小步快跑**：频繁创建小的 migration，而不是一次大改动
2. **可逆性**：确保每个 migration 都可以回滚
3. **测试优先**：在开发环境充分测试 migration
4. **文档化**：在 migration 注释中说明为什么做这个变更
5. **团队协作**：团队成员应该定期同步 migration 状态

## 📚 相关命令速查

```bash
# 创建新的 migration（自动检测变更）
alembic revision --autogenerate -m "描述"

# 创建空的 migration（手动编写）
alembic revision -m "描述"

# 升级到最新版本
alembic upgrade head

# 升级一个版本
alembic upgrade +1

# 降级一个版本
alembic downgrade -1

# 查看当前版本
alembic current

# 查看历史
alembic history

# 查看 SQL（不实际执行）
alembic upgrade head --sql
```
