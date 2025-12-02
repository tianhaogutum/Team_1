# Souvenir System 开发计划

用前端 Canvas生层souvenir

## 📋 概述

当前Souvenir系统只在前端localStorage中存储数据，没有后端持久化。本计划将实现完整的后端API、数据同步、AI摘要生成等功能。

---

## 🎯 目标

1. **数据持久化**: 所有souvenirs保存到数据库
2. **AI集成**: 自动生成个性化souvenir摘要
3. **完整数据**: 显示详细的XP breakdown和路线信息
4. **用户体验**: 增强Gallery功能和交互

---

## 📝 开发计划

### Phase 1: 后端API开发（核心功能）

#### 1.1 创建Souvenir API Endpoints

**文件**: `backend/app/api/v1/souvenirs.py` (新建) 或 `backend/app/api/v1/routes.py` (扩展)

**方案A: 新建souvenirs.py (推荐)**
- `POST /api/profiles/{profile_id}/souvenirs` - 创建souvenir（完成路线时调用）
- `GET /api/profiles/{profile_id}/souvenirs` - 获取用户所有souvenirs
- `GET /api/profiles/{profile_id}/souvenirs/{souvenir_id}` - 获取单个souvenir详情

**方案B: 扩展routes.py (如果更符合RESTful设计)**
- `POST /api/routes/{route_id}/complete` - 完成路线并创建souvenir (已有schema支持)
- `GET /api/profiles/{profile_id}/souvenirs` - 获取用户所有souvenirs (需要在profiles.py或新建souvenirs.py)

**Schema需求**:
- ✅ `RouteCompleteRequest`: 已有 (route_id, completed_quest_ids)
- ✅ `RouteCompleteResponse`: 已有 (souvenir, xp_breakdown, total_xp_gained, new_level)
- ✅ `SouvenirResponse`: 已有
- ✅ `SouvenirListResponse`: 已有
- ⚠️ 需要创建: `SouvenirListRequest` (如果需要query参数)

**业务逻辑**:
1. 验证route和profile存在
2. 计算总XP（base_xp + quest_xp + multipliers）
3. 生成AI摘要（调用已有的`generate_post_run_summary`）
4. 创建Souvenir记录并保存到数据库
5. 更新用户profile的total_xp和level
6. 返回完整的souvenir信息（包含关联的route信息）

#### 1.2 AI摘要生成服务

**文件**: `backend/app/services/genai_service.py` (已有)

**现有函数**: `generate_post_run_summary(route_title, route_length_km, quests_completed, total_quests, user_level)`
- ✅ 已实现AI摘要生成
- ⚠️ 需要调整：接受Route和UserProfile对象，提取所需参数
- ⚠️ 需要添加fallback模板（当AI生成失败时）

#### 1.3 XP计算服务

**文件**: `backend/app/services/xp_calculator.py` (新建) 或直接在souvenirs.py中实现

**函数**:
- `calculate_route_completion_xp(route, completed_quest_ids, db_session) -> dict`
  - 查询route的base_xp_reward
  - 查询completed quests的总XP
  - 根据difficulty计算multiplier
  - 返回: `{"base": X, "quests": Y, "difficulty_multiplier": Z, "total": T}`
  
**参考**: `backend/scripts/calculate_route_xp.py` 中的计算逻辑

#### 1.4 更新Router注册

**文件**: `backend/app/main.py`

- 添加: `from .api.v1 import souvenirs`
- 添加: `app.include_router(souvenirs.router, prefix="/api")`

---

### Phase 2: 前端API集成

#### 2.1 更新API类型定义

**文件**: `frontend/lib/api-types.ts`

**添加**:
```typescript
export interface ApiSouvenir {
  id: number;
  demo_profile_id: number;
  route_id: number;
  completed_at: string;
  total_xp_gained: number;
  genai_summary: string | null;
  xp_breakdown_json: string | null;
  route?: ApiRoute;
}

export interface SouvenirCreateRequest {
  route_id: number;
  completed_quest_ids: number[];
  xp_breakdown?: {
    base_xp: number;
    quest_xp: number;
    difficulty_multiplier: number;
    total_xp: number;
  };
}

export interface SouvenirListResponse {
  souvenirs: ApiSouvenir[];
  total: number;
}
```

#### 2.2 添加API客户端方法

**文件**: `frontend/lib/api-client.ts`

**添加方法**:
- `createSouvenir(profileId: number, data: SouvenirCreateRequest)`
- `getSouvenirs(profileId: number)`
- `getSouvenir(profileId: number, souvenirId: number)`

#### 2.3 创建Transform函数

**文件**: `frontend/lib/api-transforms.ts`

**添加**:
- `transformApiSouvenir(apiSouvenir: ApiSouvenir): DigitalSouvenir`
- `transformApiSouvenirs(apiSouvenirs: ApiSouvenir[]): DigitalSouvenir[]`

#### 2.4 更新路线完成逻辑

**文件**: `frontend/components/route-recommendations.tsx`

**修改 `handleCompleteRoute`**:
1. 调用后端API创建souvenir
2. 等待响应后再更新前端状态
3. 处理错误情况（fallback到localStorage）
4. 刷新souvenirs列表

**需要传递的数据**:
- route_id
- completed_quest_ids (从hiking-simulator获取)
- xp_breakdown (计算的详细breakdown)

#### 2.5 更新Hiking Simulator

**文件**: `frontend/components/hiking-simulator.tsx`

**修改**:
- `handleRouteCompletion`: 计算并记录completed quest IDs
- `handleCompletionClose`: 传递completed_quest_ids给onComplete

---

### Phase 3: Gallery功能增强

#### 3.1 后端数据加载

**文件**: `frontend/components/route-recommendations.tsx`

**添加**:
- `fetchSouvenirs()` 函数：从后端API加载souvenirs
- `useEffect` 在登录时自动加载
- 与localStorage同步（后端优先，localStorage作为fallback）

#### 3.2 Gallery组件增强

**文件**: `frontend/components/souvenir-gallery.tsx`

**新增功能**:
1. **AI Summary显示**
   - 如果souvenir有`genai_summary`，显示在卡片上
   - 添加"展开/收起"功能

2. **XP Breakdown详情**
   - 解析`xp_breakdown_json`
   - 显示: Base XP, Quest XP, Difficulty Multiplier, Total XP

3. **排序功能**
   - 默认: 最新优先
   - 可选: XP最多、距离最远、最旧优先

4. **筛选功能**
   - 按路线类型 (hiking/running/cycling)
   - 按难度 (easy/medium/hard/expert)
   - 按日期范围

5. **详情视图**
   - 点击souvenir卡片显示详情模态框
   - 显示完整信息：路线详情、AI摘要、XP breakdown、完成的quests

#### 3.3 新建Souvenir详情模态框组件

**文件**: `frontend/components/souvenir-detail-modal.tsx` (新建)

**功能**:
- 显示完整souvenir信息
- 显示关联的route详情
- 显示AI生成的摘要
- 显示详细的XP breakdown
- "重新挑战"按钮（跳转到route详情）

---

### Phase 4: AI摘要集成

#### 4.1 后端AI摘要生成

**文件**: `backend/app/services/genai_service.py`

**实现**:
```python
async def generate_post_run_summary(
    route: Route,
    user_profile: DemoProfile,
    xp_breakdown: dict,
    completed_quests_count: int
) -> str:
```

**Prompt内容**:
- 路线信息（名称、难度、距离、地点）
- 用户类型（explorer type）
- 完成的quest数量
- XP获得情况
- 生成个性化摘要和下一步建议

#### 4.2 在完成路线时调用

**文件**: `backend/app/api/v1/souvenirs.py`

- 在创建souvenir时自动调用
- 使用try/except处理AI生成失败
- 失败时使用模板摘要

---

### Phase 5: 数据迁移和兼容性

#### 5.1 迁移localStorage数据（可选）

**脚本**: `backend/scripts/migrate_local_souvenirs.py` (新建)

- 从localStorage格式转换为数据库格式
- 批量导入已有souvenirs
- 处理数据不完整的情况

#### 5.2 前端兼容性处理

**文件**: `frontend/components/route-recommendations.tsx`

- 首次加载时检查localStorage是否有souvenirs
- 如果有，尝试同步到后端（如果API可用）
- 保持localStorage作为offline支持

---

## 🗂️ 文件清单

### 新建文件
1. `backend/app/api/v1/souvenirs.py` - Souvenir API endpoints
2. `backend/app/services/xp_calculator.py` - XP计算服务
3. `frontend/components/souvenir-detail-modal.tsx` - Souvenir详情模态框
4. `backend/scripts/migrate_local_souvenirs.py` (可选) - 数据迁移脚本

### 修改文件
1. `backend/app/main.py` - 注册souvenirs router
2. `backend/app/services/genai_service.py` - 添加post-run summary生成
3. `backend/app/api/schemas.py` - 添加SouvenirCreateRequest等schemas
4. `frontend/lib/api-types.ts` - 添加API类型定义
5. `frontend/lib/api-client.ts` - 添加API客户端方法
6. `frontend/lib/api-transforms.ts` - 添加transform函数
7. `frontend/lib/mock-data.ts` - 更新DigitalSouvenir接口（添加后端字段）
8. `frontend/components/route-recommendations.tsx` - 更新完成路线逻辑
9. `frontend/components/hiking-simulator.tsx` - 传递quest信息
10. `frontend/components/souvenir-gallery.tsx` - 增强功能
11. `frontend/components/completion-summary.tsx` - 确保onViewSouvenirs正常工作

---

## 🔄 开发顺序建议

### Step 1: 后端基础API (1-2小时)
1. 创建 `souvenirs.py` API文件
2. 实现基础的POST和GET endpoints
3. 测试API是否工作

### Step 2: XP计算和摘要生成 (1-2小时)
1. 创建/扩展XP计算服务
2. 实现AI摘要生成（或先使用模板）
3. 在创建souvenir时集成

### Step 3: 前端API集成 (1-2小时)
1. 添加API类型和客户端方法
2. 更新handleCompleteRoute调用后端API
3. 测试创建souvenir流程

### Step 4: Gallery数据加载 (1小时)
1. 实现从后端加载souvenirs
2. 替换localStorage数据源
3. 测试数据同步

### Step 5: Gallery功能增强 (2-3小时)
1. 添加排序和筛选
2. 显示AI摘要和XP breakdown
3. 创建详情模态框

### Step 6: 测试和优化 (1小时)
1. 端到端测试完整流程
2. 错误处理测试
3. UI/UX优化

**总预估时间**: 6-10小时

---

## 🎨 UI/UX改进建议

### Gallery界面增强

1. **排序选项** (dropdown)
   - 最新优先 (默认)
   - 最旧优先
   - XP最多
   - XP最少
   - 距离最长
   - 距离最短

2. **筛选选项** (多选tags)
   - 按路线类型: 🏔️ Hiking | 🏃 Running | 🚴 Cycling
   - 按难度: Easy | Medium | Hard | Expert
   - 按月份/年份

3. **搜索功能**
   - 搜索路线名称或地点

4. **统计面板**
   - 总souvenirs数量
   - 总XP获得
   - 总距离
   - 最常访问的地点
   - 最喜欢的路线类型

5. **交互改进**
   - 点击souvenir卡片显示详情模态框
   - 悬停效果增强
   - 加载动画
   - 空状态优化

### Souvenir卡片增强

显示更多信息：
- ✅ AI生成的摘要（如果存在）
- ✅ XP breakdown详情（展开/收起）
- ✅ 完成的quests列表
- ✅ 路线难度徽章
- ✅ 完成时间（相对时间："2 days ago"）
- ✅ 路线标签

---

## 📊 数据流图

```
用户完成路线
    ↓
HikingSimulator: handleRouteCompletion()
    ↓
计算XP和quest信息
    ↓
CompletionSummary显示
    ↓
用户点击"Continue Exploring"
    ↓
route-recommendations: handleCompleteRoute()
    ↓
[新] 调用 POST /api/profiles/{id}/souvenirs
    ↓
后端: 创建Souvenir记录
    ├─ 计算XP breakdown
    ├─ 生成AI摘要
    ├─ 保存到数据库
    └─ 更新用户profile
    ↓
返回SouvenirResponse
    ↓
前端: 更新localStorage和state
    ↓
刷新Gallery显示新souvenir
```

---

## 🔧 技术债务和后续优化

### Phase 1完成后可以考虑

1. **批量导入**: 从localStorage批量迁移souvenirs到数据库
2. **图片优化**: 为每个souvenir生成独特的卡片图片
3. **分享功能**: 生成可分享的souvenir卡片图片
4. **导出功能**: 导出souvenirs为JSON/CSV
5. **成就系统**: 基于souvenirs解锁特殊成就
6. **社交功能**: 查看其他用户的public souvenirs（如果未来有）

---

## ⚠️ 风险点和注意事项

1. **数据迁移**: localStorage中的souvenirs可能缺少route_id（如果route已被删除）
2. **性能**: 如果用户有大量souvenirs，考虑分页或虚拟滚动
3. **AI生成延迟**: 可能增加完成路线后的等待时间（需要loading状态）
4. **并发**: 如果用户快速完成多个路线，需要处理并发创建souvenir的情况
5. **数据一致性**: 确保前端localStorage和后端数据库保持同步

---

## ⚠️ 注意事项

1. **向后兼容**: 保持localStorage支持作为fallback
2. **错误处理**: API失败时不应阻塞用户体验
3. **AI生成**: 如果Ollama不可用，使用模板摘要
4. **数据验证**: 确保route_id、profile_id存在
5. **性能**: 批量加载souvenirs时考虑分页（如果数量很多）

---

## ✅ 验收标准

- [ ] 完成路线后souvenir保存到数据库
- [ ] 可以从后端API获取souvenirs列表
- [ ] Gallery显示AI生成的摘要
- [ ] Gallery显示详细的XP breakdown
- [ ] 支持排序和筛选
- [ ] 点击"check it out in your Souvenir Gallery"能正常打开gallery
- [ ] 数据持久化，刷新页面不丢失
- [ ] API失败时有fallback机制

---

## 📝 详细实现说明

### API Endpoint 详细设计

#### POST /api/profiles/{profile_id}/souvenirs

**请求体**:
```json
{
  "route_id": 1362328,
  "completed_quest_ids": [1, 2, 3],
  "xp_breakdown": {
    "base_xp": 100,
    "quest_xp": 50,
    "difficulty_multiplier": 1.2,
    "total_xp": 180
  }
}
```

**响应**:
```json
{
  "id": 42,
  "demo_profile_id": 1,
  "route_id": 1362328,
  "completed_at": "2025-01-20T10:30:00Z",
  "total_xp_gained": 180,
  "genai_summary": "Congratulations on conquering...",
  "xp_breakdown_json": "{\"base\": 100, \"quests\": 50, \"multiplier\": 1.2, \"total\": 180}",
  "route": {
    "id": 1362328,
    "title": "Route Name",
    ...
  }
}
```

**实现逻辑**:
1. 验证profile_id和route_id存在
2. 计算XP breakdown（如果没有提供）
3. 调用`generate_post_run_summary`生成AI摘要
4. 创建Souvenir记录
5. 更新DemoProfile的total_xp和level
6. 使用selectinload加载route关联信息
7. 返回SouvenirResponse

#### GET /api/profiles/{profile_id}/souvenirs

**查询参数**:
- `limit`: 返回数量限制（默认20）
- `offset`: 分页偏移（默认0）
- `sort`: 排序方式 ("newest", "oldest", "xp_high", "xp_low")

**响应**:
```json
{
  "souvenirs": [...],
  "total": 15
}
```

**实现逻辑**:
1. 查询该用户的所有souvenirs
2. 使用selectinload预加载route信息
3. 应用排序和分页
4. 返回列表

---

## 🔍 关键实现细节

### XP计算逻辑

参考`backend/scripts/calculate_route_xp.py`:
- Base XP来自route.base_xp_reward
- Quest XP = 每个完成的quest的xp_reward之和
- Difficulty multiplier:
  - easy: 1.0
  - medium: 1.2
  - hard: 1.5
  - expert: 2.0
- Total = (base_xp + quest_xp) * difficulty_multiplier

### AI摘要生成

使用已有的`generate_post_run_summary`函数，需要传递：
- route_title (从route.title获取)
- route_length_km (从route.length_meters / 1000获取)
- quests_completed (从completed_quest_ids.length获取)
- total_quests (从route.breakpoints中统计有quest的数量)
- user_level (从profile.level获取)

### 错误处理

1. **AI生成失败**: 使用模板摘要
   ```python
   fallback_summary = f"Congratulations on completing {route.title}! You earned {total_xp} XP. Keep exploring!"
   ```

2. **API调用失败**: 前端fallback到localStorage
3. **Route不存在**: 返回404
4. **Profile不存在**: 返回404

---

## 💻 代码示例

### 后端API实现示例

```python
# backend/app/api/v1/souvenirs.py

@router.post("/profiles/{profile_id}/souvenirs", response_model=RouteCompleteResponse)
async def create_souvenir(
    profile_id: int,
    request: RouteCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Complete a route and create a souvenir record.
    
    1. Validates route and profile exist
    2. Calculates XP breakdown
    3. Generates AI summary
    4. Creates Souvenir record
    5. Updates user profile
    """
    # 1. Validate profile
    profile = await db.get(DemoProfile, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    
    # 2. Validate and load route with breakpoints
    route_result = await db.execute(
        select(Route)
        .where(Route.id == request.route_id)
        .options(selectinload(Route.breakpoints))
    )
    route = route_result.scalar_one_or_none()
    if not route:
        raise HTTPException(404, "Route not found")
    
    # 3. Calculate XP breakdown
    xp_breakdown = calculate_route_completion_xp(route, request.completed_quest_ids, db)
    
    # 4. Generate AI summary
    try:
        genai_summary = await generate_post_run_summary(
            route_title=route.title,
            route_length_km=(route.length_meters / 1000) if route.length_meters else 0,
            quests_completed=len(request.completed_quest_ids),
            total_quests=sum(1 for bp in route.breakpoints if bp.mini_quests),
            user_level=profile.level
        )
    except Exception as e:
        logger.warning(f"AI summary generation failed: {e}")
        genai_summary = f"Congratulations on completing {route.title}! You earned {xp_breakdown['total']} XP."
    
    # 5. Create Souvenir
    new_souvenir = Souvenir(
        demo_profile_id=profile_id,
        route_id=request.route_id,
        total_xp_gained=xp_breakdown['total'],
        genai_summary=genai_summary,
        xp_breakdown_json=json.dumps(xp_breakdown)
    )
    db.add(new_souvenir)
    
    # 6. Update profile
    old_level = profile.level
    profile.total_xp += xp_breakdown['total']
    profile.level = calculate_level_from_xp(profile.total_xp)
    new_level = profile.level
    
    await db.commit()
    await db.refresh(new_souvenir)
    
    # 7. Load route relationship
    await db.refresh(new_souvenir, ['route'])
    
    # 8. Return response
    souvenir_dict = SouvenirResponse.model_validate(new_souvenir).model_dump()
    return RouteCompleteResponse(
        souvenir=SouvenirResponse(**souvenir_dict),
        xp_breakdown=xp_breakdown,
        total_xp_gained=xp_breakdown['total'],
        new_level=new_level
    )
```

### 前端API调用示例

```typescript
// frontend/lib/api-client.ts (添加方法)

async createSouvenir(
  profileId: number,
  routeId: number,
  completedQuestIds: number[]
): Promise<RouteCompleteResponse> {
  return this.post<RouteCompleteResponse>(
    `api/profiles/${profileId}/souvenirs`,
    {
      route_id: routeId,
      completed_quest_ids: completedQuestIds
    }
  );
}

async getSouvenirs(profileId: number): Promise<SouvenirListResponse> {
  return this.get<SouvenirListResponse>(
    `api/profiles/${profileId}/souvenirs`
  );
}
```

### 前端完成路线更新示例

```typescript
// frontend/components/route-recommendations.tsx

const handleCompleteRoute = async (route: Route, xpGained: number, completedQuestIds: string[] = []) => {
  if (!isLoggedIn || !userProfile.id) {
    // Fallback to localStorage for guest users
    const newSouvenir = { ... };
    // existing localStorage logic
    return;
  }
  
  try {
    const profileIdNum = parseInt(userProfile.id, 10);
    const questIdsNum = completedQuestIds.map(id => parseInt(id, 10));
    
    // Call backend API
    const response = await apiClient.createSouvenir(
      profileIdNum,
      parseInt(route.id, 10),
      questIdsNum
    );
    
    // Transform API response to frontend format
    const newSouvenir = transformApiSouvenir(response.souvenir);
    
    // Update profile state
    const updatedProfile = {
      ...userProfile,
      xp: userProfile.xp + response.total_xp_gained,
      level: response.new_level,
      completedRoutes: [...userProfile.completedRoutes, route.id],
      souvenirs: [newSouvenir, ...userProfile.souvenirs],
    };
    
    onUpdateProfile(updatedProfile);
    localStorage.setItem("trailsaga-profile", JSON.stringify(updatedProfile));
    
  } catch (error) {
    console.error("Failed to create souvenir:", error);
    // Fallback to localStorage
    const newSouvenir = { ... };
    // existing localStorage logic
  }
  
  setActiveRoute(null);
};
```

---

## 🚀 快速开始

### 第一步：创建后端API

1. 创建 `backend/app/api/v1/souvenirs.py`
2. 实现POST endpoint（创建souvenir）
3. 在main.py中注册router
4. 测试：`curl -X POST http://localhost:8000/api/profiles/1/souvenirs ...`

### 第二步：更新前端

1. 添加API类型定义
2. 更新handleCompleteRoute调用API
3. 测试创建流程

### 第三步：完善功能

1. 添加AI摘要生成
2. 增强Gallery功能
3. 测试完整流程

---

## 📚 参考实现

可以参考以下文件的实现模式：
- `backend/app/api/v1/profiles.py` - Profile API实现模式
- `backend/app/api/v1/routes.py` - Route API实现模式
- `frontend/components/route-recommendations.tsx` - 数据获取模式

