# 哈利波特主题故事与任务系统功能说明书

## 一、功能概述

将现有的徒步路线故事系统改造为哈利波特魔法世界主题，用户在完成路线时：
1. 体验以哈利波特为背景的探险故事（具有悬念性，每个 breakpoint 为 1000 单词的小说章节）
2. 在每个 breakpoint（检查点）触发小任务，增强互动性

## 二、核心功能

### 2.1 哈利波特主题故事生成

**修改位置：** `backend/app/services/story_generator.py`

**实现方式：**
- 在故事生成的 prompt 中加入哈利波特世界观设定
- 将路线元素映射为魔法世界元素：
  - 路线 → 魔法探险任务
  - 地点（POI）→ 魔法地点（如禁林、霍格沃茨城堡、对角巷等）
  - 难度 → 魔法任务难度等级
  - 距离 → 魔法旅程长度
- **结合历史背景**：使用 breakpoint 存储的历史背景信息来生成更真实、更有深度的故事

**故事结构：**
- **Prologue（序章）**：以哈利波特世界观开场，设定任务背景（如寻找魔法物品、探索神秘地点等）
- **Main Quest（主线任务）**：每个 breakpoint 生成约 1000 单词的小说章节，推进主线剧情，保持悬念和连续性
  - 故事要像小说章节一样，有情节发展、对话、环境描写、心理活动等
  - 必须结合 breakpoint 的历史背景、地理位置、POI 特征等信息
  - 保持悬念性，每个章节结尾留下悬念
- **Epilogue（尾声）**：完成魔法任务后的总结和感悟

**历史背景数据策略：**
- **真实数据路线**：仅对 "Traditional Costume and Shooting Parade Wiesn" (route_id: 1362610) 使用真实的历史背景数据
  - 需要为每个 breakpoint 准备详细的历史背景信息
  - 包括：历史事件、建筑背景、文化意义、相关人物等
- **Mock 数据路线**：其他路线使用 mock 数据
  - 可以基于 POI 类型和名称生成通用的历史背景描述

**故事风格要求：**
- 保持悬念性：每个 breakpoint 的故事应该留下悬念，推动用户继续探索
- 魔法元素：融入咒语、魔法生物、魔法物品等元素
- 角色代入：用户扮演霍格沃茨学生或魔法探险者
- 历史融合：将真实的历史背景巧妙地融入魔法故事中，让历史地点在魔法世界中焕发新的意义

### 2.2 Breakpoint 小任务系统

**修改位置：** 
- 后端：`backend/app/models/entities.py` (MiniQuest 模型已存在)
- 前端：`frontend/components/hiking-simulator.tsx`

**任务类型设计：**

1. **拍照任务（Photo Quest）**
   - 描述：在当前位置拍摄一张魔法主题照片
   - UI 展示：显示"📸 拍摄魔法瞬间"按钮
   - 完成方式：点击按钮即完成（无需真实拍照功能）
   - XP 奖励：10-20 XP

2. **观察任务（Observation Quest）**
   - 描述：观察并描述当前地点的魔法特征
   - UI 展示：显示"👁️ 观察魔法细节"按钮
   - 完成方式：点击按钮后显示一个简单的文本输入框（可选填写，点击确认即完成）
   - XP 奖励：15-25 XP

3. **收集任务（Collection Quest）**
   - 描述：收集魔法物品或线索
   - UI 展示：显示"🔮 收集魔法物品"按钮
   - 完成方式：点击按钮即完成，显示收集到的物品卡片
   - XP 奖励：20-30 XP

4. **解谜任务（Puzzle Quest）**
   - 描述：解开魔法谜题或密码
   - UI 展示：显示"🧩 解开魔法谜题"按钮
   - 完成方式：点击按钮后显示一个简单的选择题或填空题（点击确认即完成）
   - XP 奖励：25-35 XP

**任务生成逻辑：**
- 每个 breakpoint 随机分配 1-2 个小任务
- 任务描述使用哈利波特主题语言（如"用魔法相机记录这个神秘地点"）
- 任务难度与 breakpoint 顺序相关（越往后任务越难，XP 奖励越高）

### 2.3 前端展示优化

**修改位置：** `frontend/components/hiking-simulator.tsx`

**UI 改进：**
1. **故事卡片样式**
   - 使用魔法主题配色（深蓝、金色、紫色）
   - 添加魔法元素图标（魔杖、魔法书、水晶球等）
   - 故事文本使用更具魔法感的字体样式

2. **任务卡片设计**
   - 每个任务显示为独立的卡片
   - 卡片包含：任务图标、任务描述、XP 奖励、完成按钮
   - 完成任务后显示动画效果（如魔法光芒、星星闪烁）

3. **Breakpoint 到达动画**
   - 到达 breakpoint 时播放魔法特效动画
   - 显示"✨ 发现魔法地点 ✨"提示

## 三、技术实现要点

### 3.1 后端修改

1. **数据库模型修改**
   - **移除 Side Plot**：从 `Breakpoint` 模型中移除 `side_plot_snippet` 字段
   - **扩展 Main Quest**：`main_quest_snippet` 字段改为存储约 1000 单词的长文本
   - **添加历史背景字段**（可选方案）：
     - 方案 A：在 `Breakpoint` 表中添加 `historical_context` 字段（Text 类型）
     - 方案 B：使用现有的 `poi_name` 和 `poi_type` 字段，并在生成故事时从外部数据源获取历史背景
   - **创建历史背景数据文件**：为 Wiesn 路线（route_id: 1362610）创建包含每个 breakpoint 历史背景的 JSON 文件

2. **故事生成 Prompt 修改**
   ```python
   # 在 story_generator.py 的 prompt 中：
   "You are creating a Harry Potter themed adventure story chapter. 
   The user is a wizard/witch exploring magical locations. 
   Each checkpoint represents a magical place in the wizarding world.
   
   Write a full chapter (approximately 1000 words) that:
   - Advances the main plot from the previous chapter
   - Incorporates the historical context and real-world significance of this location
   - Blends real history with magical elements
   - Includes dialogue, action, description, and character development
   - Ends with a cliffhanger or suspenseful moment
   
   Historical Context: [从数据库或数据文件获取的历史背景信息]
   Location Details: [POI 名称、类型、地理位置等]
   "
   ```

3. **故事生成逻辑调整**
   - **移除 Side Plot 生成**：不再生成 side_plot，只生成 main_quest
   - **增加字数要求**：将 main_quest 从 40-60 词改为约 1000 单词
   - **历史背景注入**：
     - 对于 Wiesn 路线：从历史背景数据文件读取真实信息
     - 对于其他路线：基于 POI 信息生成通用的历史背景描述
   - **调整 Token 限制**：由于故事更长，需要增加 `max_tokens` 参数（建议 2000-3000 tokens）

4. **任务生成逻辑**
   - 在生成故事时，同时为每个 breakpoint 生成 1-2 个小任务
   - 任务类型从预定义的任务池中随机选择
   - 任务描述使用 LLM 生成，确保与哈利波特主题一致

5. **API 响应调整**
   - `StoryGenerateResponse` 中每个 breakpoint 只包含 `main_quest`（不再有 `side_plot`）
   - 每个 breakpoint 包含 `mini_quests` 数组
   - 每个 mini_quest 包含：`task_type`, `task_description`, `xp_reward`

### 3.2 前端修改

1. **移除 Side Plot 相关代码**
   - 从 `api-transforms.ts` 中移除 `side_plot_snippet` 的处理逻辑
   - 从 `hiking-simulator.tsx` 中移除 side_plot 的显示
   - 更新 API 类型定义，移除 `side_plot_snippet` 字段

2. **长文本故事展示优化**
   - 由于故事文本从 40-60 词增加到约 1000 单词，需要优化展示方式：
     - 使用滚动容器显示完整故事
     - 添加章节标题和分页（可选）
     - 优化字体大小和行间距，提升阅读体验
     - 添加"继续阅读"按钮，支持分页或滚动

3. **任务展示组件**
   - 创建 `MiniQuestCard` 组件，展示单个任务
   - 在 `hiking-simulator.tsx` 中集成任务展示逻辑
   - 任务完成状态管理（已完成任务不再显示）

4. **交互逻辑**
   - 点击任务按钮后，显示任务完成动画
   - 更新用户 XP（调用后端 API）
   - 标记任务为已完成

5. **样式主题**
   - 添加哈利波特主题的 CSS 变量
   - 使用魔法主题的图标和动画

## 四、数据流程

1. **用户开始路线** → 调用 `/routes/{route_id}/generate-story`
2. **后端生成故事**：
   - 检查路线 ID，如果是 Wiesn 路线（1362610），加载真实历史背景数据
   - 否则，基于 POI 信息生成通用历史背景描述
   - LLM 生成哈利波特主题故事章节（约 1000 单词）+ 小任务
   - 故事必须结合历史背景信息
3. **保存到数据库** → Route 表保存故事，Breakpoint 表只保存 `main_quest_snippet`（不再保存 `side_plot_snippet`），MiniQuest 表保存任务
4. **前端获取数据** → 调用 `/routes/{route_id}/story` 获取完整故事和任务
5. **用户到达 Breakpoint** → 显示长文本故事内容（约 1000 单词）+ 可用任务列表
6. **用户完成任务** → 调用任务完成 API，更新 XP，标记任务完成

## 五、注意事项

1. **不需要实现真实功能**
   - 拍照任务：只需点击按钮即完成，不需要调用相机 API
   - 观察任务：文本输入框可选，点击确认即完成
   - 解谜任务：答案可以预设或随机，主要目的是互动体验

2. **故事连贯性**
   - 确保每个 breakpoint 的故事与前后 breakpoint 连贯
   - 主线任务要有明确的推进感
   - 在故事中适当埋下悬念，吸引用户继续

3. **任务多样性**
   - 避免每个 breakpoint 都是相同类型的任务
   - 根据 breakpoint 的位置和特点，选择合适类型的任务
   - 任务描述要与当前故事内容相关

4. **性能考虑**
   - 故事生成可能需要 10-15 秒，需要显示加载状态
   - 任务完成动画要流畅，不影响用户体验

## 六、开发优先级

1. **Phase 1：数据库和模型调整**
   - 创建数据库迁移：移除 `side_plot_snippet` 字段
   - 为 Wiesn 路线准备历史背景数据文件（JSON 格式）
   - 更新 Breakpoint 模型和相关 Schema

2. **Phase 2：故事生成逻辑改造**
   - 修改 story_generator.py：
     - 移除 side_plot 生成逻辑
     - 将 main_quest 从 40-60 词改为约 1000 单词
     - 添加历史背景数据加载逻辑
     - 更新 prompt，要求生成小说章节风格的长文本
     - 调整 token 限制
   - 测试故事生成效果（特别是 Wiesn 路线）

3. **Phase 3：前端适配**
   - 移除 side_plot 相关代码
   - 优化长文本故事展示（滚动、分页等）
   - 更新 API 类型定义

4. **Phase 4：任务系统后端**
   - 实现任务生成逻辑
   - 创建任务完成 API

5. **Phase 5：前端任务展示**
   - 创建任务卡片组件
   - 集成到 hiking-simulator
   - 实现任务完成交互

6. **Phase 6：UI 优化**
   - 添加魔法主题样式
   - 实现动画效果
   - 优化用户体验

## 七、示例

### Wiesn 路线历史背景数据示例

```json
{
  "route_id": 1362610,
  "breakpoints": [
    {
      "order_index": 0,
      "poi_name": "Theresienwiese Gate",
      "historical_context": "Theresienwiese (Theresa's Meadow) is named after Princess Therese of Saxe-Hildburghausen, who married Crown Prince Ludwig (later King Ludwig I) here in 1810. This wedding celebration is considered the first Oktoberfest. The meadow has been the site of the annual Oktoberfest since then, making it one of the world's largest and most famous folk festivals. The area covers 42 hectares and hosts millions of visitors each year."
    },
    {
      "order_index": 1,
      "poi_name": "Bavaria Statue Steps",
      "historical_context": "The Bavaria statue, completed in 1850, is a monumental bronze statue representing Bavaria, the female personification of the Bavarian homeland. Designed by Ludwig Schwanthaler and cast by Ferdinand von Miller, it stands 18.52 meters tall and weighs approximately 87.36 tons. The statue was a symbol of Bavarian identity and strength during the 19th century. Visitors can climb the internal staircase to reach the head, offering panoramic views of Munich."
    }
    // ... 更多 breakpoint 的历史背景
  ]
}
```

### 故事示例

- **Prologue**: "你收到了一封来自霍格沃茨的信，信中提到了一个神秘的魔法物品隐藏在慕尼黑啤酒节的深处。作为新晋的魔法探险者，你决定踏上这段充满未知的旅程..."

- **Breakpoint 1 Main Quest** (约 1000 单词的小说章节):
  ```
  你站在特蕾西娅草坪的入口处，古老的石拱门在月光下显得格外神秘。这里曾经是 1810 年路德维希王储和特蕾西娅公主举行婚礼的地方，而如今，在魔法世界的视角下，这片土地隐藏着更深层的秘密。
  
  你拿出魔杖，轻声念出"荧光闪烁"。魔杖尖端的光芒照亮了前方的道路，但你注意到，在普通麻瓜眼中，这里只是一个普通的节日场地，而在你眼中，空气中弥漫着古老的魔法气息。
  
  一个声音在你身后响起："你也收到了那封信？"你转身，看到一个穿着霍格沃茨校袍的年轻女巫，她的眼睛在月光下闪闪发光。
  
  "是的，"你回答，"关于那个失落的魔法物品..."
  
  "嘘！"她急忙打断你，"这里不是说话的地方。跟我来，我知道一个安全的地方。"
  
  她带你穿过人群，来到巴伐利亚雕像的脚下。这座 1850 年建成的巨大雕像在魔法世界中有着特殊的意义——它不仅是巴伐利亚的象征，更是一个古老的魔法标记点。
  
  "看这里，"她指着雕像底座上的一个几乎看不见的符号，"这是古代德鲁伊留下的标记。传说中，每隔一百年，当月亮处于特定位置时，这里会出现一个通往隐藏魔法世界的入口。"
  
  你仔细观察那个符号，它似乎在你眼前微微发光。突然，你感觉到有什么东西在注视着你。你抬头看向雕像的头部，但那里空无一物。
  
  "我们必须小心，"女巫低声说，"不是所有人都希望我们找到那个物品。有人在监视我们。"
  
  就在这时，你听到远处传来一阵奇怪的声音，像是某种魔法生物的叫声。你握紧了魔杖，准备迎接即将到来的挑战...
  ```

### 任务示例
- **拍照任务**: "📸 用魔法相机记录这个神秘地点 - 奖励 15 XP"
- **观察任务**: "👁️ 仔细观察并描述你看到的魔法特征 - 奖励 20 XP"
- **收集任务**: "🔮 收集这片区域的魔法线索 - 奖励 25 XP"

## 八、技术细节

### 8.1 历史背景数据存储

**方案选择：**
- **推荐方案**：创建独立的历史背景数据文件 `backend/data/historical_context/wiesn_route.json`
- 文件结构包含 route_id 和每个 breakpoint 的详细历史背景
- 在故事生成时，如果是 Wiesn 路线，从文件加载历史背景
- 其他路线使用基于 POI 信息的通用描述

### 8.2 故事长度控制

- **目标长度**：约 1000 单词（约 150-200 个句子）
- **Token 估算**：1000 单词 ≈ 1300-1500 tokens（英文）
- **LLM 参数调整**：
  - `max_tokens`: 设置为 2000-3000（为 JSON 格式和可能的额外内容留出空间）
  - `temperature`: 0.7-0.8（保持创意性，同时确保连贯性）

### 8.3 数据库迁移

需要创建 Alembic 迁移文件：
```python
# 移除 side_plot_snippet 字段
op.drop_column('breakpoints', 'side_plot_snippet')
```

### 8.4 性能考虑

- **生成时间**：1000 单词的故事生成可能需要 30-60 秒
- **缓存策略**：生成后的故事保存在数据库中，避免重复生成
- **前端加载**：显示加载动画和进度提示

