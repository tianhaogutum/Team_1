# XP 保存功能测试脚本

## 问题描述
点击 "check it out in your Souvenir Gallery" 时，XP 应该保存但实际没有保存。只有点击 "Continue Exploring" 才能保存。

## 测试步骤

### 方法 1: 浏览器控制台测试

1. 打开浏览器开发者工具 (F12)
2. 切换到 Console 标签
3. 在控制台运行以下代码来监控 localStorage 变化：

```javascript
// 监控 localStorage 变化
let lastProfile = null;
function monitorXP() {
    const profileStr = localStorage.getItem('trailsaga-profile');
    if (profileStr) {
        const profile = JSON.parse(profileStr);
        const currentXP = profile.xp || 0;
        
        if (lastProfile) {
            const xpDiff = currentXP - (lastProfile.xp || 0);
            if (xpDiff !== 0) {
                console.log(`✅ XP 已保存! ${lastProfile.xp} → ${currentXP} (+${xpDiff})`);
            } else {
                console.log(`❌ XP 未变化: ${currentXP}`);
            }
        }
        lastProfile = profile;
    }
}

// 每 500ms 检查一次
setInterval(monitorXP, 500);

// 记录当前 XP
const profile = JSON.parse(localStorage.getItem('trailsaga-profile') || '{}');
console.log(`当前 XP: ${profile.xp || 0}`);
console.log('开始监控 XP 变化...');
```

4. 在应用中完成一条路线
5. 记录完成前的 XP 值
6. 点击 "check it out in your Souvenir Gallery" 链接
7. 查看控制台输出，看 XP 是否增加

### 方法 2: 使用测试页面

1. 打开 `scripts/test-xp-save.html` 文件
2. 在浏览器中打开该 HTML 文件
3. 页面会自动监控 localStorage 变化
4. 在另一个标签页打开你的应用
5. 完成一条路线
6. 点击 Gallery 链接
7. 回到测试页面查看日志

### 方法 3: 手动验证步骤

1. **准备阶段**
   ```javascript
   // 在控制台运行
   const profile = JSON.parse(localStorage.getItem('trailsaga-profile') || '{}');
   console.log('开始测试 - 当前状态:');
   console.log('  XP:', profile.xp || 0);
   console.log('  完成的路线:', profile.completedRoutes || []);
   console.log('  纪念品数量:', (profile.souvenirs || []).length);
   ```

2. **完成路线前**
   - 记录当前的 XP 值
   - 记录当前完成的路线数量

3. **完成路线后（在 CompletionSummary 界面）**
   - 在控制台运行：
   ```javascript
   // 检查 CompletionSummary 是否显示了正确的 XP
   console.log('完成界面显示:');
   // 查看页面上显示的 XP 数值
   ```

4. **点击 Gallery 链接**
   - **立即**在控制台运行：
   ```javascript
   const profile = JSON.parse(localStorage.getItem('trailsaga-profile') || '{}');
   console.log('点击 Gallery 链接后:');
   console.log('  XP:', profile.xp || 0);
   console.log('  完成的路线:', profile.completedRoutes || []);
   console.log('  纪念品数量:', (profile.souvenirs || []).length);
   ```

5. **验证结果**
   - XP 应该增加了
   - 应该有一条新的纪念品记录
   - 路线应该被标记为已完成

## 预期行为

### 正确的行为：
- ✅ 点击 Gallery 链接 → XP 立即保存 → 打开画廊
- ✅ 点击 Continue 按钮 → XP 保存（如果还没保存）→ 返回路线列表
- ✅ 两个按钮都可以点击，不会重复保存

### 错误的行为（当前问题）：
- ❌ 点击 Gallery 链接 → XP 没有保存 → 打开画廊
- ❌ 只有点击 Continue 按钮才能保存 XP

## 调试检查点

### 1. 检查函数调用链

在 `completion-summary.tsx` 中，Gallery 链接的点击处理：

```typescript
onClick={() => {
  console.log('[v0] Souvenir link clicked, onViewSouvenirs:', onViewSouvenirs);
  if (onViewSouvenirs) {
    onViewSouvenirs();
  }
}}
```

在 `hiking-simulator.tsx` 中，`handleViewSouvenirs` 函数：

```typescript
const handleViewSouvenirs = () => {
  console.log('[v0] handleViewSouvenirs called');
  // Save XP first before viewing gallery (only if not already saved)
  handleSaveCompletion();
  // Then open gallery
  if (onViewSouvenirs) {
    onViewSouvenirs();
  }
};
```

**检查方法：**
1. 完成路线后，打开控制台
2. 点击 Gallery 链接
3. 查看控制台日志：
   - 应该看到 `[v0] Souvenir link clicked`
   - 应该看到 `[v0] handleViewSouvenirs called`
   - 如果没有看到这些日志，说明函数没有被调用

### 2. 检查状态变量

在 `hiking-simulator.tsx` 中：

```typescript
const [isRouteCompleted, setIsRouteCompleted] = useState(false);

const handleSaveCompletion = () => {
  if (!isRouteCompleted) {
    setIsRouteCompleted(true);
    onComplete(route, totalXpGained, completedQuests);
  }
};
```

**检查方法：**
- 在控制台无法直接访问组件内部状态
- 但可以通过观察 `onComplete` 是否被调用来判断

### 3. 检查 onComplete 回调

`onComplete` 应该调用 `handleCompleteRoute`，它会：
1. 创建 souvenir
2. 更新 XP
3. 保存到 localStorage

**检查方法：**
```javascript
// 在控制台运行，检查 handleCompleteRoute 是否被调用
// 可以通过检查 localStorage 的变化来判断
```

## 可能的修复方案

如果测试发现问题，可能的修复：

1. **确保 onViewSouvenirs 传递正确**
   - 检查 `HikingSimulator` 是否正确传递 `handleViewSouvenirs` 给 `CompletionSummary`

2. **在 CompletionSummary 中也调用 onClose**
   - 修改 Gallery 链接的处理，先调用 `onClose()` 再调用 `onViewSouvenirs()`

3. **添加调试日志**
   - 在关键点添加 console.log 来追踪执行流程

## 测试结果记录

请记录以下信息：

- [ ] 测试时间：___________
- [ ] 测试方法：___________
- [ ] 完成前的 XP：___________
- [ ] 点击 Gallery 链接后的 XP：___________
- [ ] 点击 Continue 按钮后的 XP：___________
- [ ] 控制台错误信息：___________
- [ ] 控制台日志输出：___________

## 下一步

根据测试结果：
1. 如果 XP 确实没有保存 → 需要修复代码
2. 如果 XP 已经保存 → 可能是显示问题
3. 如果出现错误 → 需要检查错误信息

