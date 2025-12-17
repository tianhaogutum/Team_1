# Remaining Features to be Implemented

## 🔴 High Priority

### AI Storytelling System ✅
- **Status**: API implemented but has unacceptable latency
- **Task**: Batch generate mock breakpoints data, then pre-generate:
  - Prologue for each route
  - Epilogue for each route
  - Story snippets for each breakpoint
- **Action**: Store pre-generated content in DB for fast FE display

### Feedback Loop (US-08)
- **Status**: Negative feedback API not implemented
- **Backend**: Missing API endpoint for negative feedback
- **Frontend**: Button exists but not calling any API
---

## 🟡 Medium Priority

### Souvenir System ✅
- **Backend**: 
  - Generation rules & DB schema/logic only partly thought through
- **Frontend**: 
  - Gallery page missing
  - Spotlight component missing
  - Wiring/connections still missing

### Gamification Logic 1号，实现lock的逻辑 
- **Route Locking/Unlocking**: 
  - Currently only mocked on FE
  - Need real XP-based locking logic
- **Achievements**: 
  - Currently mock data only
  - Need real rules and storage

---

## 🟢 Low Priority

### Side Quests / Quizzes
- **Backend**: 
  - No BE model yet
  - No GenAI logic yet
- **Frontend**: 
  - Only has placeholder UI

### Breakpoint Map Logic ✅ (使用 Mock Data 改进)
- **Status**: ✅ 已改进 - 使用 mock data 作为 fallback
- **Frontend 改进**:
  - ✅ 在 `Breakpoint` 接口中添加了 `latitude`、`longitude` 和 `orderIndex` 字段
  - ✅ 在 `mock-data.ts` 中为所有 breakpoint 添加了 mock 坐标数据
  - ✅ 更新了 `route-simulation-map.tsx` 使用真实坐标绘制地图路径（如果有）
  - ✅ 实现了坐标 fallback 逻辑：如果后端没有坐标，自动生成基于路线位置的 mock 坐标
  - ✅ 确保 breakpoint 按 `order_index` 正确排序
- **API Transform 改进**:
  - ✅ 在 `api-transforms.ts` 中添加了智能坐标生成逻辑
  - ✅ 根据路线位置（如 Munich、Berlin、Black Forest 等）生成合理的 mock 坐标
  - ✅ 自动按 `order_index` 排序 breakpoint
- **Backend**: 
  - 如果 DB 中有坐标，前端会优先使用真实坐标
  - 如果 DB 中没有坐标，前端会自动生成 mock 坐标，确保地图正常显示

---

## Notes
- Prioritize features based on user impact and technical complexity
- Consider batch processing for AI-generated content to improve performance
- Ensure FE and BE are properly wired before marking features as complete

暂定实现，未来实现的功能：
1. 登陆功能，数据的持久化