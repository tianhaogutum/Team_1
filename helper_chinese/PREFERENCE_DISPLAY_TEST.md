# 用户偏好显示功能测试指南

## 📋 功能概述

在用户Profile模态框的Statistics标签页中，现在会显示用户的详细偏好设置，包括：

1. **Difficulty Range** (难度范围)
2. **Distance Range** (距离范围)  
3. **Fitness Level** (健身等级)
4. **Preferred Interests** (偏好标签)

## 🚀 如何测试

### 前置条件

确保前端和后端服务都在运行：

```bash
# Terminal 1 - 后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000

# Terminal 2 - 前端  
cd frontend
npm run dev
```

### 测试步骤

1. **打开应用**
   - 访问 http://localhost:3000

2. **创建或登录Profile**
   - 如果是新用户，完成问卷调查创建profile
   - 选择健身等级 (beginner/intermediate/advanced)
   - 选择冒险类型 (history-culture/natural-scenery/family-fun)
   - 选择叙述风格

3. **打开Profile模态框**
   - 点击页面右上角的用户头像或Profile按钮
   - 应该会打开用户资料模态框

4. **查看Statistics标签页**
   - 默认应该在Statistics标签页
   - 向下滚动，在"Explorer Profile"和"Journey Statistics"之后
   - 会看到一个新的卡片："Your Preferences" 🎚️

5. **验证显示内容**

   应该看到以下内容（根据用户选择的不同而不同）：

   **Beginner用户示例：**
   - Difficulty Range: `0 - 1` (Beginner friendly)
   - Distance Range: `0.0 - 8.0 km`
   - Fitness Level: `beginner`
   - Preferred Interests: 根据选择的冒险类型显示标签

   **Intermediate用户示例：**
   - Difficulty Range: `1 - 2` (Intermediate level)
   - Distance Range: `5.0 - 20.0 km`
   - Fitness Level: `intermediate`
   - Preferred Interests: 对应的标签

   **Advanced用户示例：**
   - Difficulty Range: `2 - 3` (Advanced challenges)
   - Distance Range: `10.0 - 50.0 km`
   - Fitness Level: `advanced`
   - Preferred Interests: 对应的标签

## 🎯 偏好标签映射

不同的冒险类型对应不同的偏好标签：

| 冒险类型 | 偏好标签 |
|---------|---------|
| **history-culture** | culture, heritage, architecture, museum |
| **natural-scenery** | flora, fauna, panorama, scenic, geology |
| **family-fun** | suitableforfamilies, playground, dining, loopTour |

## 🔄 动态更新测试

用户偏好会根据反馈动态调整：

1. **提交路线反馈**
   - 在推荐路线中点击"Not for me"按钮
   - 选择反馈原因（too-hard, too-easy, too-far, not-interested）
   - 提交反馈

2. **查看偏好变化**
   - 重新打开Profile模态框
   - 查看Statistics标签页的"Your Preferences"
   - 偏好应该根据反馈原因进行了调整：
     - `too-hard` → 最大难度降低
     - `too-easy` → 最小难度提高
     - `too-far` → 最大距离减少
     - `not-interested` → 移除相关标签

## 🐛 故障排除

### 问题1: 偏好不显示

**症状**: "Your Preferences"卡片显示"No preference data available"

**可能原因**:
- Profile未正确创建
- user_vector_json为空

**解决方案**:
1. 检查浏览器控制台是否有错误
2. 验证后端API返回: `GET /api/profiles/{profile_id}`
3. 确认返回数据包含`user_vector_json`字段

### 问题2: 加载中一直显示

**症状**: 一直显示"Loading preferences..."

**可能原因**:
- 后端服务未运行
- API调用失败

**解决方案**:
1. 确认后端在 http://localhost:8000 运行
2. 检查浏览器控制台Network标签
3. 查看API请求是否成功

### 问题3: 偏好数值不正确

**症状**: 显示的偏好值与预期不符

**解决方案**:
1. 打开浏览器开发者工具
2. 在Console中输入: `localStorage.getItem('trailsaga-profile')`
3. 复制profile ID
4. 在浏览器访问: `http://localhost:8000/api/profiles/{profile_id}`
5. 检查返回的`user_vector_json`内容

## ✅ 测试检查清单

- [ ] Profile模态框可以正常打开
- [ ] Statistics标签页显示正常
- [ ] "Your Preferences"卡片出现在正确位置
- [ ] Difficulty Range显示正确的数值和描述
- [ ] Distance Range显示正确的范围
- [ ] Fitness Level显示正确的等级
- [ ] Preferred Interests标签正确显示
- [ ] 加载状态正常工作
- [ ] 无控制台错误
- [ ] 响应式布局在移动端正常显示

## 📸 预期效果截图位置

新的"Your Preferences"卡片应该显示在：
- Statistics标签页中
- "Explorer Profile"卡片之后
- "Journey Statistics"卡片之后  
- "Activity Breakdown"卡片之前

## 🎨 UI特性

- 使用`Sliders`图标 🎚️
- 卡片使用`border-2 border-border`样式
- 偏好项使用`bg-muted/50`背景
- 标签使用`Badge`组件显示
- 响应式网格布局 (md:grid-cols-2)

---

**实现日期**: 2025-12-17  
**实现者**: AI Assistant  
**相关文件**:
- `frontend/lib/api-client.ts` - 添加getProfile方法
- `frontend/components/user-profile-modal.tsx` - 添加偏好显示

