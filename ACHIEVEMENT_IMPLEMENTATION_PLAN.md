# Achievement System Implementation Plan

## 概述
实现完整的成就系统，包括后端数据模型、API、解锁逻辑和前端集成。

## 成就列表（8个）

1. **First Steps** - Complete your first route
   - 条件：完成至少1条路线
   - Icon: 🥾

2. **Explorer** - Complete 3 different routes
   - 条件：完成至少3条不同的路线
   - Icon: 🗺️

3. **Trail Hiker** - Complete a hiking route
   - 条件：完成至少1条 hiking 类型的路线
   - Icon: ⛰️

4. **Trail Runner** - Complete a running route
   - 条件：完成至少1条 running 类型的路线
   - Icon: 🏃

5. **Cyclist** - Complete a cycling route
   - 条件：完成至少1条 cycling 类型的路线
   - Icon: 🚴

6. **Rising Star** - Reach Level 5
   - 条件：用户等级 >= 5
   - Icon: ⭐

7. **XP Collector** - Earn 1000 total XP
   - 条件：用户总 XP >= 1000
   - Icon: 💎

8. **Long Distance** - Travel 50km total
   - 条件：所有完成路线的总距离 >= 50km
   - Icon: 🎯

## 实现步骤

### Phase 1: 后端数据模型
1. 创建 `Achievement` 模型
   - id (primary key)
   - achievement_key (唯一标识符，如 'first-steps')
   - name (显示名称)
   - description (描述)
   - icon (emoji 图标)
   - condition_type (条件类型：route_count, route_type, level, xp, distance)
   - condition_value (条件值，JSON格式存储具体条件)

2. 创建 `ProfileAchievement` 模型（用户成就关联表）
   - id (primary key)
   - demo_profile_id (外键)
   - achievement_id (外键)
   - unlocked_at (解锁时间)

3. 创建数据库迁移

### Phase 2: 后端服务逻辑
1. 创建 `achievement_service.py`
   - `check_and_unlock_achievements()` - 检查并解锁成就
   - `get_user_achievements()` - 获取用户所有成就状态
   - `get_all_achievements()` - 获取所有成就定义

2. 成就检查逻辑
   - 在路线完成时触发检查（route completion）
   - 在用户等级/XP更新时触发检查
   - 支持批量检查所有成就

### Phase 3: 后端 API
1. 创建 `/api/v1/achievements.py`
   - `GET /api/v1/achievements` - 获取所有成就定义
   - `GET /api/v1/profiles/{profile_id}/achievements` - 获取用户成就状态
   - `POST /api/v1/profiles/{profile_id}/achievements/check` - 手动触发成就检查

2. 在路线完成 API 中集成成就检查
   - 修改 `POST /api/v1/profiles/{profile_id}/complete-route`
   - 完成后自动检查并解锁成就

### Phase 4: 前端集成
1. 更新 API types (`api-types.ts`)
   - 添加 `ApiAchievement` 接口
   - 添加 `ApiProfileAchievement` 接口

2. 更新 API client (`api-client.ts`)
   - 添加获取成就的方法

3. 更新 `user-profile-modal.tsx`
   - 从后端获取成就数据
   - 实时显示解锁状态
   - 支持成就解锁通知

### Phase 5: 测试
1. 单元测试
   - 测试成就检查逻辑
   - 测试各种解锁条件

2. 集成测试
   - 测试路线完成触发成就解锁
   - 测试 API 端点

3. 手动测试
   - 完成路线验证成就解锁
   - 验证 UI 显示正确

## 数据库 Schema

### achievements 表
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_key VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(10) NOT NULL,
    condition_type VARCHAR(20) NOT NULL,  -- route_count, route_type, level, xp, distance
    condition_value TEXT NOT NULL  -- JSON string
);
```

### profile_achievements 表
```sql
CREATE TABLE profile_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demo_profile_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (demo_profile_id) REFERENCES demo_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE,
    UNIQUE(demo_profile_id, achievement_id)
);
```

## 实现细节

### 成就条件类型
- `route_count`: 完成路线数量
- `route_type`: 完成特定类型的路线（hiking/running/cycling）
- `level`: 达到特定等级
- `xp`: 累计 XP 达到特定值
- `distance`: 累计距离达到特定值（km）

### 解锁时机
1. 路线完成时（自动检查）
2. 用户查看成就页面时（实时检查）
3. 手动触发检查 API

### 性能考虑
- 成就检查使用批量查询，避免 N+1 问题
- 缓存用户已解锁的成就列表
- 只在必要时触发检查（路线完成、等级变化）

