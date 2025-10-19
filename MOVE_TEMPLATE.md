# Cobblemon 技能模板（完整字段库）

> 此模板包含所有可能的技能字段和选项  
> AI根据用户需求删减不需要的部分，只保留相关字段

## 📋 完整技能结构

```javascript
{
  // === 基础信息（必需） ===
  num: -10001,                    // 技能编号（自定义技能用负数）
  name: "Move Name",              // 技能名称
  type: "TYPE",                   // 属性类型（见下方类型列表）
  category: "CATEGORY",           // 分类（见下方分类列表）
  
  // === 数值参数（必需） ===
  basePower: 0,                   // 威力（0-250，0表示变化技能）
  accuracy: 100,                  // 命中率（1-100，或true表示必中）
  pp: 10,                         // PP值（1-40）
  priority: 0,                    // 优先度（-7到+5，通常为0）
  
  // === 目标（必需） ===
  target: "TARGET",               // 目标类型（见下方目标列表）
  
  // === 标志位（可选） ===
  flags: {
    contact: 1,                   // 接触技能
    protect: 1,                   // 可被保护
    mirror: 1,                    // 可被魔法反射
    metronome: 1,                 // 可被挥指使用
    snatch: 1,                    // 可被抢夺
    reflectable: 1,               // 可被魔法反射
    heal: 1,                      // 回复技能
    sound: 1,                     // 声音技能
    punch: 1,                     // 拳类技能
    pulse: 1,                     // 波动技能
    bullet: 1,                    // 子弹技能
    bite: 1,                      // 啃咬技能
    dance: 1,                     // 舞蹈技能
    bypasssub: 1,                 // 无视替身
    allyanim: 1,                  // 队友动画
    wind: 1,                      // 风技能
    slicing: 1,                   // 切割技能
  },
  
  // === 追加效果（可选） ===
  secondary: {
    chance: 10,                   // 触发概率（1-100）
    
    // 选项1：状态异常（选一个）
    status: "STATUS",             // 状态类型（见下方状态列表）
    
    // 选项2：能力变化（可组合）
    boosts: {
      atk: 1,                     // 攻击（-6到+6）
      def: 1,                     // 防御
      spa: 1,                     // 特攻
      spd: 1,                     // 特防
      spe: 1,                     // 速度
      accuracy: 1,                // 命中率
      evasion: 1,                 // 回避率
    },
    
    // 选项3：其他效果
    volatileStatus: "VOLATILE",   // 临时状态
    pseudoWeather: "WEATHER",     // 伪天气
  },
  
  // === 特殊效果（可选，选一个） ===
  
  // 吸血效果
  drain: [1, 2],                  // 吸血比例 [分子, 分母]，表示1/2
  
  // 反伤效果
  recoil: [1, 3],                 // 反伤比例 [分子, 分母]，表示1/3
  
  // 回复效果
  heal: [1, 2],                   // 回复比例 [分子, 分母]，表示1/2
  
  // 连续攻击
  multihit: [2, 5],               // 攻击次数 [最小, 最大]
  // 或
  multihit: 3,                    // 固定3次
  
  // 蓄力技能
  onTryMove: function() { ... },  // 第一回合蓄力
  
  // 自爆技能
  selfdestruct: "always",         // 使用后自己濒死
  
  // 高会心率
  critRatio: 2,                   // 会心率倍率（1-3）
  
  // 畏缩效果
  secondary: {
    chance: 30,
    volatileStatus: "flinch",     // 畏缩
  },
  
  // 混乱效果
  secondary: {
    chance: 10,
    volatileStatus: "confusion",  // 混乱
  },
  
  // === 描述（推荐添加） ===
  shortDesc: "简短描述",           // 简短描述（推荐）
  desc: "详细描述",                // 详细描述（可选）
}
```

---

## 📚 字段选项参考

### **属性类型 (type)**

```
Normal, Fire, Water, Electric, Grass, Ice, Fighting, Poison,
Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, 
Steel, Fairy
```

### **分类 (category)**

```
Physical    - 物理攻击
Special     - 特殊攻击
Status      - 变化技能
```

### **状态异常 (status)**

```
par  - 麻痹 (Paralyze)
brn  - 灼伤 (Burn)
psn  - 中毒 (Poison)
tox  - 剧毒 (Toxic)
slp  - 睡眠 (Sleep)
frz  - 冰冻 (Freeze)
```

### **临时状态 (volatileStatus)**

```
flinch       - 畏缩
confusion    - 混乱
taunt        - 挑衅
leechseed    - 寄生种子
curse        - 诅咒
nightmare    - 恶梦
attract      - 迷人
lockedmove   - 锁定技能
```

### **目标类型 (target)**

```
normal              - 单个对手
allAdjacentFoes     - 所有相邻对手
allAdjacent         - 所有相邻宝可梦
adjacentFoe         - 相邻对手
adjacentAlly        - 相邻队友
self                - 自己
allyTeam            - 我方全体
foeSide             - 对方场地
allySide            - 我方场地
all                 - 全场
```

### **优先度参考 (priority)**

```
+5: 先发制人 (极少)
+4: 守护类技能
+3: 跟我来
+2: 看我嘛
+1: 先制攻击（最常见）
 0: 普通技能（默认）
-1: -
-3: 反击类
-4: 雪崩
-5: 急冻光线（后攻）
-6: 聚气爆发
-7: 报仇（极少）
```

---

## 💡 AI使用指南

### **步骤1：分析用户需求**

提取关键信息：
- 属性、分类、威力、命中、PP
- 优先度
- 追加效果类型
- 特殊机制

### **步骤2：删除不相关字段**

根据需求：
- **物理攻击** → 保留 `contact`, `protect`, `mirror` 等标志
- **无追加效果** → 删除 `secondary`
- **无特殊效果** → 删除 `drain`, `recoil` 等
- **普通优先度** → `priority: 0`

### **步骤3：填充具体数值**

- 根据用户描述填写 `name`, `basePower`, `accuracy` 等
- 根据效果类型选择对应字段（`status`, `boosts`, `drain` 等）
- 添加 `shortDesc` 描述效果

### **步骤4：验证完整性**

确保：
- ✅ 必需字段都存在
- ✅ 数值在合理范围
- ✅ 效果描述清晰
- ✅ 没有冲突的效果组合

---

## 📖 示例

### **示例1：简单物理攻击**

**用户需求：** "火系物理攻击，威力80，命中100，PP15，10%灼伤"

**AI生成：**
```javascript
{
  num: -10001,
  name: "Flame Strike",
  type: "Fire",
  category: "Physical",
  basePower: 80,
  accuracy: 100,
  pp: 15,
  priority: 0,
  flags: {contact: 1, protect: 1, mirror: 1, metronome: 1},
  secondary: {
    chance: 10,
    status: "brn"
  },
  target: "normal",
  shortDesc: "10% chance to burn the target."
}
```

### **示例2：高优先度技能**

**用户需求：** "电系物理攻击，威力90，命中100，PP15，优先度+1，10%麻痹"

**AI生成：**
```javascript
{
  num: -10002,
  name: "Thunder Strike",
  type: "Electric",
  category: "Physical",
  basePower: 90,
  accuracy: 100,
  pp: 15,
  priority: 1,              // 高优先度
  flags: {contact: 1, protect: 1, mirror: 1, metronome: 1},
  secondary: {
    chance: 10,
    status: "par"
  },
  target: "normal",
  shortDesc: "Usually goes first. 10% chance to paralyze."
}
```

### **示例3：吸血技能**

**用户需求：** "草系特殊攻击，威力75，命中100，吸血50%"

**AI生成：**
```javascript
{
  num: -10003,
  name: "Drain Leaf",
  type: "Grass",
  category: "Special",
  basePower: 75,
  accuracy: 100,
  pp: 10,
  priority: 0,
  flags: {protect: 1, mirror: 1, heal: 1, metronome: 1},
  drain: [1, 2],            // 吸血50%
  secondary: null,
  target: "normal",
  shortDesc: "User recovers 50% of the damage dealt."
}
```

### **示例4：能力提升**

**用户需求：** "变化技能，提升自己攻击和速度各1级"

**AI生成：**
```javascript
{
  num: -10004,
  name: "Power Rush",
  type: "Normal",
  category: "Status",
  basePower: 0,
  accuracy: true,           // 必中
  pp: 20,
  priority: 0,
  flags: {snatch: 1, metronome: 1},
  boosts: {                 // 直接提升能力（不是secondary）
    atk: 1,
    spe: 1
  },
  target: "self",
  shortDesc: "Raises the user's Attack and Speed by 1 stage."
}
```

---

## 🎯 关键要点

1. **删减原则**：只保留用户需求相关的字段
2. **必需字段**：`num`, `name`, `type`, `category`, `basePower`, `accuracy`, `pp`, `priority`, `target`
3. **效果互斥**：`secondary`、`drain`、`recoil` 等不能同时存在（除非特殊说明）
4. **描述重要**：务必添加 `shortDesc` 说明效果
5. **数值合理**：威力、命中、PP 要在合理范围内

---

**基于此模板，AI可以快速、准确地生成任何技能！** ✨

