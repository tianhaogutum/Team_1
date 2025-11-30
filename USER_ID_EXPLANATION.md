# 用户 ID 生成机制说明

## 当前系统设计

### 这是一个 Demo/原型系统
- **没有传统的账号密码登录系统**
- **没有用户注册流程**
- 用户通过填写**问卷（Onboarding Questionnaire）**来创建 profile

---

## 用户 ID 生成流程

### 1. 用户填写问卷
```
用户访问网站 → 点击 "BEGIN YOUR SAGA" → 填写问卷
```

### 2. 前端发送请求
```typescript
// frontend/components/onboarding-questionnaire.tsx
POST /api/profiles
{
  "fitness": "beginner",
  "type": ["history-culture"],
  "narrative": "adventure"
}
```

### 3. 后端创建用户记录
```python
# backend/app/api/v1/profiles.py
new_profile = DemoProfile(
    user_vector_json=json.dumps(user_vector),
    genai_welcome_summary=welcome_summary,
    total_xp=0,
    level=1,
)
db.add(new_profile)
await db.commit()
await db.refresh(new_profile)

# 数据库自动生成 ID（自增主键）
return ProfileCreateResponse(
    id=new_profile.id,  # ← 这就是用户 ID
    ...
)
```

### 4. 数据库自动分配 ID
```python
# backend/app/models/entities.py
class DemoProfile(Base):
    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        autoincrement=True  # ← 自动递增
    )
```

**工作原理：**
- SQLite 数据库自动为每条新记录分配一个递增的整数 ID
- 第一个用户：ID = 1
- 第二个用户：ID = 2
- 以此类推...

### 5. 前端保存 ID
```typescript
// frontend/components/onboarding-questionnaire.tsx
const profile: UserProfile = {
    id: String(backendProfileId),  // 保存后端返回的 ID
    ...
}
localStorage.setItem('trailsaga-profile', JSON.stringify(profile));
```

---

## 为什么没有账号密码？

### 当前系统特点：
1. **Demo/原型系统**：快速验证概念，不需要复杂的认证
2. **基于问卷的创建**：用户通过填写偏好问卷来创建 profile
3. **本地存储**：使用 localStorage 保存用户状态
4. **无状态后端**：后端只存储数据，不管理会话

### 优点：
- ✅ 快速开始，无需注册
- ✅ 简单直接，适合 demo
- ✅ 用户体验流畅

### 缺点：
- ❌ 无法跨设备同步
- ❌ 清除浏览器数据会丢失
- ❌ 没有账号密码保护

---

## 如果需要添加登录系统

可以添加以下功能：

### 选项 1：简单的用户名系统
- 用户填写用户名（不需要密码）
- 后端根据用户名查找或创建用户
- 适合 demo 场景

### 选项 2：完整的账号密码系统
- 用户注册（用户名 + 密码）
- 登录验证
- JWT token 认证
- 适合生产环境

### 选项 3：第三方登录
- Google OAuth
- GitHub OAuth
- 适合快速集成

---

## 当前用户识别方式

### 前端识别：
- **localStorage** 中存储的 `id` 字段
- 格式：字符串（如 `"1"`, `"2"`）

### 后端识别：
- **数据库主键** `id`
- 格式：整数（如 `1`, `2`）

### 验证流程：
1. 前端从 localStorage 读取 ID
2. 调用 `GET /api/profiles/{id}` 验证用户是否存在
3. 如果存在 → 正常使用
4. 如果不存在 → 清除 localStorage，返回欢迎页面

---

## 总结

**用户 ID 来源：**
- ✅ 数据库自动生成（自增主键）
- ✅ 通过填写问卷创建
- ✅ 无需账号密码
- ✅ 适合 demo/原型系统

**如果需要生产级别的登录系统，我可以帮你实现！**

