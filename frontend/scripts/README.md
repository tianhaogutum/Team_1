# XP 保存功能测试工具

## 问题描述
点击 "check it out in your Souvenir Gallery" 链接时，XP 应该保存但没有保存。只有点击 "Continue Exploring" 按钮才能保存 XP。

## 修复内容

### 1. 修复了 `completion-summary.tsx`
- 修改了 Gallery 链接的点击处理逻辑
- 现在点击 Gallery 链接时会：
  1. 先调用 `onClose()` 保存 XP
  2. 然后调用 `onViewSouvenirs()` 打开画廊

### 2. 修复了 `hiking-simulator.tsx`
- 添加了 `isRouteCompleted` 状态来防止重复保存
- `handleViewSouvenirs` 现在会先保存 XP 再打开画廊

## 测试工具

### 方法 1: 使用 HTML 测试页面（推荐）

1. 在浏览器中打开 `test-xp-save.html`
2. 在另一个标签页打开你的应用
3. 完成一条路线
4. 点击 "check it out in your Souvenir Gallery" 链接
5. 回到测试页面查看实时日志和统计

**功能：**
- ✅ 实时监控 localStorage 变化
- ✅ 显示 XP、等级、路线、纪念品统计
- ✅ 自动检测 XP 变化并记录日志
- ✅ 可视化状态变化

### 方法 2: 使用 JavaScript 测试脚本（控制台）

1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 复制 `test-xp-save.js` 文件中的全部内容
4. 粘贴到控制台并回车
5. 按照提示完成测试

**功能：**
- ✅ 监控 localStorage 变化
- ✅ 自动检测 XP 保存
- ✅ 拦截 console.log 来检测按钮点击
- ✅ 提供测试函数：`XPTest.check()`, `XPTest.getState()`, `XPTest.reset()`

### 方法 3: 手动测试步骤

查看 `test-xp-save-manual.md` 获取详细的手动测试步骤。

## 测试步骤

### 基本测试流程

1. **准备阶段**
   ```javascript
   // 在控制台记录初始状态
   const profile = JSON.parse(localStorage.getItem('trailsaga-profile') || '{}');
   console.log('初始 XP:', profile.xp || 0);
   ```

2. **完成路线**
   - 在应用中完成一条路线
   - 到达 CompletionSummary 界面

3. **测试 Gallery 链接**
   - 记录完成后的 XP 值（应该显示在界面上）
   - 点击 "check it out in your Souvenir Gallery" 链接
   - 立即检查 localStorage 中的 XP 是否增加

4. **验证结果**
   ```javascript
   const profile = JSON.parse(localStorage.getItem('trailsaga-profile') || '{}');
   console.log('点击 Gallery 链接后的 XP:', profile.xp || 0);
   console.log('纪念品数量:', (profile.souvenirs || []).length);
   ```

### 预期结果

✅ **成功的情况：**
- 点击 Gallery 链接后，XP 立即增加
- 新的纪念品被添加到列表中
- 路线被标记为已完成
- 控制台日志显示保存成功

❌ **失败的情况：**
- 点击 Gallery 链接后，XP 没有变化
- 没有新的纪念品
- 控制台可能有错误信息

## 调试信息

### 关键日志点

查看控制台中的以下日志来追踪执行流程：

1. `[v0] Souvenir link clicked` - Gallery 链接被点击
2. `[v0] Calling onClose to save XP` - 开始保存 XP
3. `[v0] handleViewSouvenirs called` - handleViewSouvenirs 被调用
4. `[v0] handleSaveCompletion called` - 开始保存完成状态
5. `[v0] Opening gallery` - 准备打开画廊

### 常见问题

**Q: XP 没有保存怎么办？**

A: 检查以下几点：
1. 查看控制台是否有错误信息
2. 确认 `handleSaveCompletion` 是否被调用
3. 确认 `onComplete` 回调是否正常工作
4. 检查 `isRouteCompleted` 状态是否正确

**Q: XP 被保存了两次怎么办？**

A: `isRouteCompleted` 标志应该防止重复保存。如果还是出现重复，检查：
1. 状态更新是否及时
2. 是否有多个 CompletionSummary 实例

**Q: 画廊没有打开怎么办？**

A: 检查：
1. `onViewSouvenirs` prop 是否被正确传递
2. `handleViewSouvenirsFromSimulator` 是否正常工作

## 代码变更摘要

### completion-summary.tsx
```typescript
// 修改前：只调用 onViewSouvenirs()
onClick={() => {
  if (onViewSouvenirs) {
    onViewSouvenirs();
  }
}}

// 修改后：先保存 XP，再打开画廊
onClick={() => {
  if (onClose) {
    onClose(); // 保存 XP
  }
  if (onViewSouvenirs) {
    setTimeout(() => {
      onViewSouvenirs(); // 打开画廊
    }, 100);
  }
}}
```

### hiking-simulator.tsx
```typescript
// 添加了状态标记和统一的保存逻辑
const [isRouteCompleted, setIsRouteCompleted] = useState(false);

const handleSaveCompletion = () => {
  if (!isRouteCompleted) {
    setIsRouteCompleted(true);
    onComplete(route, totalXpGained, completedQuests);
  }
};

const handleViewSouvenirs = () => {
  handleSaveCompletion(); // 先保存
  if (onViewSouvenirs) {
    onViewSouvenirs(); // 再打开画廊
  }
};
```

## 报告问题

如果测试发现问题，请提供：
1. 浏览器类型和版本
2. 控制台完整日志
3. localStorage 中的 profile 数据（去除敏感信息）
4. 测试步骤的详细描述
5. 预期行为和实际行为的对比

