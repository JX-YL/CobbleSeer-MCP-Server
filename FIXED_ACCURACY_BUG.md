# 必中技能修复说明

## 🐛 问题描述

**用户反馈**: "必中技能好像写成了避中"

## 🔍 问题分析

**原始代码** (`move_generator.py` 第86行):
```python
'accuracy': accuracy if accuracy <= 100 else True,
```

**问题**：
- 当 `accuracy=0`（表示必中）时，保留为数字 `0`
- 正确的Showdown格式：必中技能应该使用布尔值 `true`

**错误输出**：
```javascript
{
  accuracy: 0,  // ❌ 错误：0在某些实现中可能被解释为"一定不命中"
  ...
}
```

**正确输出**：
```javascript
{
  accuracy: true,  // ✅ 正确：布尔值true表示必中
  ...
}
```

## ✅ 修复方案

**修复后的代码**:
```python
'accuracy': True if accuracy == 0 else accuracy,  # 0表示必中
```

**修复逻辑**：
- `accuracy == 0` → `True`（必中）
- `accuracy > 0` → 保持原值（正常命中率）

## 🧪 验证结果

**测试技能**: `demoaura`（必中技能）

**修复前**:
```javascript
{
  num: -10001,
  name: "demoaura",
  type: "Psychic",
  category: "Special",
  basePower: 80,
  accuracy: 0,  // ❌
  pp: 20,
  ...
}
```

**修复后**:
```javascript
{
  num: -10001,
  name: "demoaura",
  type: "Psychic",
  category: "Special",
  basePower: 80,
  accuracy: true,  // ✅
  pp: 20,
  ...
}
```

## 📝 影响范围

**受影响的技能**：
- `demoaura`（必中技能）

**已修复**：✅  
**已重新生成资源包**：✅  
**已验证修复效果**：✅

## 🎯 相关说明

在Pokémon Showdown格式中：
- `accuracy: true` = 必中（Never miss）
- `accuracy: 数字` = 正常命中率（如100, 85等）
- `accuracy: 0` = 可能被误解为"永不命中"

**参考技能**（宝可梦官方必中技能）：
- Aerial Ace（燕返）：`accuracy: true`
- Aura Sphere（波导弹）：`accuracy: true`
- Swift（高速星星）：`accuracy: true`

---

**修复日期**: 2025-10-19  
**修复文件**: `services/move_generator.py`  
**相关资源包**: `DemoMon_Complete_Package`

