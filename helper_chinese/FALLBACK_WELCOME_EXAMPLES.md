# `generate_fallback_welcome` 输入输出对照表

## 输入参数说明

```python
ProfileCreate(
    fitness: str,        # "beginner" | "intermediate" | "advanced"
    type: list[str],     # ["history-culture", "natural-scenery", "family-fun"] 的组合
    narrative: str       # "adventure" | "mystery" | "playful"
)
```

---

## 一、探索者称号（Explorer Title）组合

### 称号映射表

| Fitness | Narrative | 称号 (Title) |
|---------|-----------|-------------|
| **beginner** | adventure | Novice Explorer |
| **beginner** | mystery | Urban Detective |
| **beginner** | playful | Joyful Wanderer |
| **intermediate** | adventure | Skilled Wanderer |
| **intermediate** | mystery | Secret Seeker |
| **intermediate** | playful | Energetic Explorer |
| **advanced** | adventure | Elite Pathfinder |
| **advanced** | mystery | Legendary Adventurer |
| **advanced** | playful | Peak Conqueror |

**总计：3 × 3 = 9 种称号组合**

---

## 二、冒险类型（Adventure Type）组合

### 类型映射表

| 输入值 | 输出描述 |
|--------|---------|
| "history-culture" | "history and culture" |
| "natural-scenery" | "natural scenery" |
| "family-fun" | "family-friendly adventures" |

### 可能的组合（8种）

| type 输入 | adventure_description 输出 |
|-----------|---------------------------|
| `[]` | "exploration" |
| `["history-culture"]` | "history and culture" |
| `["natural-scenery"]` | "natural scenery" |
| `["family-fun"]` | "family-friendly adventures" |
| `["history-culture", "natural-scenery"]` | "history and culture and natural scenery" |
| `["history-culture", "family-fun"]` | "history and culture and family-friendly adventures" |
| `["natural-scenery", "family-fun"]` | "natural scenery and family-friendly adventures" |
| `["history-culture", "natural-scenery", "family-fun"]` | "history and culture and natural scenery and family-friendly adventures" |

---

## 三、叙事风格（Narrative Style）映射

| narrative 输入 | narrative_style 输出 |
|----------------|---------------------|
| "adventure" | "epic adventures" |
| "mystery" | "mysterious discoveries" |
| "playful" | "playful journeys" |

---

## 四、完整输出示例

### 示例 1：初级 + 冒险 + 历史文化

**输入：**
```python
{
    "fitness": "beginner",
    "type": ["history-culture"],
    "narrative": "adventure"
}
```

**输出：**
```
Welcome, Novice Explorer!

You're passionate about history and culture. 
We've prepared a collection of epic adventures tailored just for you!

Ready to begin your legendary saga?
```

---

### 示例 2：中级 + 神秘 + 自然风景

**输入：**
```python
{
    "fitness": "intermediate",
    "type": ["natural-scenery"],
    "narrative": "mystery"
}
```

**输出：**
```
Welcome, Secret Seeker!

You're passionate about natural scenery. 
We've prepared a collection of mysterious discoveries tailored just for you!

Ready to begin your legendary saga?
```

---

### 示例 3：高级 + 有趣 + 多种类型

**输入：**
```python
{
    "fitness": "advanced",
    "type": ["history-culture", "natural-scenery", "family-fun"],
    "narrative": "playful"
}
```

**输出：**
```
Welcome, Peak Conqueror!

You're passionate about history and culture and natural scenery and family-friendly adventures. 
We've prepared a collection of playful journeys tailored just for you!

Ready to begin your legendary saga?
```

---

### 示例 4：中级 + 冒险 + 无类型（空列表）

**输入：**
```python
{
    "fitness": "intermediate",
    "type": [],
    "narrative": "adventure"
}
```

**输出：**
```
Welcome, Skilled Wanderer!

You're passionate about exploration. 
We've prepared a collection of epic adventures tailored just for you!

Ready to begin your legendary saga?
```

---

## 五、所有可能的组合统计

### 总组合数

- **Fitness**: 3 种
- **Narrative**: 3 种  
- **Type**: 8 种（包括空列表）

**总计：3 × 3 × 8 = 72 种可能的输出组合**

---

## 六、输出格式模板

所有输出都遵循相同的格式：

```
Welcome, {title}!

You're passionate about {adventure_description}. 
We've prepared a collection of {narrative_style} tailored just for you!

Ready to begin your legendary saga?
```

其中：
- `{title}`: 9 种可能（见称号映射表）
- `{adventure_description}`: 8 种可能（见类型组合表）
- `{narrative_style}`: 3 种可能（见叙事风格映射表）

---

## 七、特殊情况处理

### 1. 无效的 fitness 值

**输入：**
```python
{
    "fitness": "invalid",  # 不在映射表中
    "type": ["history-culture"],
    "narrative": "adventure"
}
```

**处理：**
```python
fitness_titles = explorer_titles.get("invalid", explorer_titles["beginner"])
# → 默认使用 "beginner"
```

**输出：**
```
Welcome, Novice Explorer!  # 使用 beginner 的默认值
...
```

---

### 2. 无效的 narrative 值

**输入：**
```python
{
    "fitness": "intermediate",
    "type": ["natural-scenery"],
    "narrative": "invalid"  # 不在映射表中
}
```

**处理：**
```python
title = fitness_titles.get("invalid", fitness_titles["adventure"])
# → 默认使用 "adventure"
narrative_style = narrative_styles.get("invalid", "adventures")
# → 默认使用 "adventures"
```

**输出：**
```
Welcome, Skilled Wanderer!  # 使用 adventure 的默认值
...
We've prepared a collection of adventures tailored just for you!
```

---

### 3. 无效的 type 值

**输入：**
```python
{
    "fitness": "beginner",
    "type": ["unknown-type"],  # 不在映射表中
    "narrative": "playful"
}
```

**处理：**
```python
adventure_names = [adventure_type_names.get("unknown-type", "unknown-type")]
# → 保持原值 "unknown-type"
adventure_description = "unknown-type"
```

**输出：**
```
Welcome, Joyful Wanderer!

You're passionate about unknown-type. 
...
```

---

## 八、快速查找表

### 根据输入快速查找输出

| Fitness | Narrative | Type | Title | Adventure Desc | Narrative Style |
|---------|-----------|------|-------|----------------|-----------------|
| beginner | adventure | [] | Novice Explorer | exploration | epic adventures |
| beginner | adventure | [history] | Novice Explorer | history and culture | epic adventures |
| beginner | mystery | [natural] | Urban Detective | natural scenery | mysterious discoveries |
| intermediate | playful | [family] | Energetic Explorer | family-friendly adventures | playful journeys |
| advanced | adventure | [all] | Elite Pathfinder | history and culture and natural scenery and family-friendly adventures | epic adventures |

---

## 总结

- **输入维度**: 3 个（fitness, narrative, type）
- **可能组合**: 72 种（3 × 3 × 8）
- **输出格式**: 固定模板，3 个变量部分
- **降级处理**: 所有无效输入都有默认值

