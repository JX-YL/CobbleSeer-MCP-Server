# CobbleSeer MCP Server - 完整功能测试

## 📋 测试目标

测试所有已实现的 MCP 工具功能，验证完整工作流程。

---

## 🧪 测试案例：创建三只完整的宝可梦

我们将创建三只不同属性的宝可梦，展示所有功能：

### 1️⃣ **Fire Dragon** - 火龙（火/飞行）
### 2️⃣ **Ice Phoenix** - 冰凤（冰/飞行）
### 3️⃣ **Water Serpent** - 水蛇（水）

---

## 🔧 测试步骤

### 步骤 0: 测试服务器连接

**工具**: `hello_world`

**调用**:
```json
{
  "name": "Tester"
}
```

**预期结果**:
```json
{
  "message": "Hello, Tester! CobbleSeer MCP Server is running!",
  "version": "1.0.0",
  "status": "ready"
}
```

---

### 步骤 1: 创建 Fire Dragon

**工具**: `create_pokemon`

**参数**:
```json
{
  "name": "fire_dragon",
  "dex": 2001,
  "primary_type": "Fire",
  "secondary_type": "Flying",
  "hp": 78,
  "attack": 130,
  "defence": 90,
  "special_attack": 105,
  "special_defence": 85,
  "speed": 102,
  "height": 2.5,
  "weight": 150.5,
  "base_friendship": 50
}
```

**预期结果**:
- ✅ 生成 6 个配置文件
- ✅ `species.json` 包含火/飞行双属性
- ✅ `spawn.json` 推断在沙漠/山地生成
- ✅ `lang_*.json` 键名为 `cobblemon.species.firedragon.name`

---

### 步骤 2: 创建 Ice Phoenix

**工具**: `create_pokemon`

**参数**:
```json
{
  "name": "ice_phoenix",
  "dex": 2002,
  "primary_type": "Ice",
  "secondary_type": "Flying",
  "hp": 90,
  "attack": 85,
  "defence": 75,
  "special_attack": 125,
  "special_defence": 100,
  "speed": 115,
  "height": 1.8,
  "weight": 45.0,
  "base_friendship": 70
}
```

**预期结果**:
- ✅ 生成冰/飞行双属性宝可梦
- ✅ `spawn.json` 推断在雪地/冰原生成
- ✅ 语言文件键名: `cobblemon.species.icephoenix.name`

---

### 步骤 3: 创建 Water Serpent

**工具**: `create_pokemon`

**参数**:
```json
{
  "name": "water_serpent",
  "dex": 2003,
  "primary_type": "Water",
  "hp": 95,
  "attack": 110,
  "defence": 95,
  "special_attack": 80,
  "special_defence": 70,
  "speed": 75,
  "height": 4.2,
  "weight": 220.0,
  "base_friendship": 60
}
```

**预期结果**:
- ✅ 生成纯水系宝可梦
- ✅ `spawn.json` 推断在海洋/河流生成
- ✅ 语言文件键名: `cobblemon.species.waterserpent.name`

---

### 步骤 4: 打包 Fire Dragon (ZIP 格式)

**工具**: `build_package`

**参数**:
```json
{
  "project_name": "fire_dragon",
  "files": {
    // 从步骤 1 获取的 files 对象
  },
  "output_format": "zip"
}
```

**预期结果**:
- ✅ 生成 `fire_dragon.zip`
- ✅ 包含 11 个文件
- ✅ 符合 `结构树.txt` 标准
- ✅ 包含完整 README.md

**验证清单**:
- [ ] `data/cobblemon/species/custom/fire_dragon.json`
- [ ] `data/cobblemon/spawn_pool_world/fire_dragon.json`
- [ ] `assets/cobblemon/bedrock/pokemon/models/fire_dragon/fire_dragon.geo.json`
- [ ] `assets/cobblemon/bedrock/pokemon/animations/fire_dragon/fire_dragon.animation.json`
- [ ] `assets/cobblemon/bedrock/pokemon/posers/fire_dragon.json`
- [ ] `assets/cobblemon/bedrock/pokemon/resolvers/0_fire_dragon_base.json`
- [ ] `assets/cobblemon/textures/pokemon/fire_dragon/README.txt`
- [ ] `assets/cobblemon/lang/zh_cn.json`
- [ ] `assets/cobblemon/lang/en_us.json`
- [ ] `pack.mcmeta`
- [ ] `README.md`

---

### 步骤 5: 打包 Ice Phoenix (文件夹格式)

**工具**: `build_package`

**参数**:
```json
{
  "project_name": "ice_phoenix_datapack",
  "files": {
    // 从步骤 2 获取的 files 对象
  },
  "output_format": "folder"
}
```

**预期结果**:
- ✅ 生成 `ice_phoenix_datapack/` 文件夹
- ✅ 完整的目录结构
- ✅ 所有文件可独立编辑

---

### 步骤 6: 打包 Water Serpent (ZIP 格式)

**工具**: `build_package`

**参数**:
```json
{
  "project_name": "water_serpent",
  "files": {
    // 从步骤 3 获取的 files 对象
  },
  "output_format": "zip"
}
```

**预期结果**:
- ✅ 生成 `water_serpent.zip`
- ✅ 与前两个结构一致

---

## 📊 测试验证

### 自动验证

| 工具 | 测试次数 | 预期结果 | 状态 |
|------|---------|---------|------|
| `hello_world` | 1 | 返回欢迎消息 | ⏳ 待测试 |
| `create_pokemon` | 3 | 每次生成 6 个文件 | ⏳ 待测试 |
| `build_package` (ZIP) | 2 | 生成 11 个文件的 ZIP | ⏳ 待测试 |
| `build_package` (Folder) | 1 | 生成完整目录结构 | ⏳ 待测试 |

### 游戏内验证

1. **安装全部三个资源包**:
   ```bash
   cp fire_dragon.zip .minecraft/datapacks/
   cp ice_phoenix_datapack/ .minecraft/datapacks/
   cp water_serpent.zip .minecraft/datapacks/
   ```

2. **重载游戏**:
   ```
   /reload
   ```

3. **验证宝可梦**:
   ```
   /pokespawn fire_dragon
   /pokespawn ice_phoenix
   /pokespawn water_serpent
   ```

4. **检查项目**:
   - [ ] 名称正确显示（不是键名）
   - [ ] 图鉴号正确（2001, 2002, 2003）
   - [ ] 属性正确显示
   - [ ] 能力值正确
   - [ ] 3D 模型加载（占位符）
   - [ ] 在正确的生物群系生成

---

## 🎯 性能指标

### 生成速度
- **单个宝可梦**: < 1 秒
- **打包 ZIP**: < 2 秒
- **总测试时间**: < 15 秒

### 文件大小
- **每个 ZIP**: ~4-5 KB（无模型/纹理）
- **完整包含模型/纹理**: 预计 50-200 KB

---

## 🐛 已知限制

1. ⚠️ **模型和纹理**: 仅生成占位符，需手动添加
2. ⚠️ **AI 功能**: `generate_moves` 和 `generate_abilities` 未完全实现
3. ⚠️ **验证功能**: `validate_package` 始终返回 valid
4. ⚠️ **RAG 搜索**: `search_reference` 返回模拟数据

---

## 🚀 下一步计划

### Phase 2: AI 增强功能
- [ ] 实现 RAG 向量搜索
- [ ] 集成 Ollama + Qwen3 本地 AI
- [ ] 自动生成技能代码
- [ ] 自动生成特性代码

### Phase 3: 完善验证
- [ ] JSON Schema 验证
- [ ] 文件完整性检查
- [ ] 命名冲突检测

---

## 📝 测试报告模板

```markdown
## 测试报告 - [日期]

### 测试环境
- Minecraft 版本: 1.21.1
- Cobblemon 版本: [版本号]
- MCP Server 版本: 1.0.0

### 测试结果
- [ ] Fire Dragon 创建成功
- [ ] Ice Phoenix 创建成功
- [ ] Water Serpent 创建成功
- [ ] ZIP 打包成功
- [ ] 文件夹打包成功
- [ ] 游戏内加载成功
- [ ] 名称正确显示

### 发现的问题
1. [问题描述]
2. [问题描述]

### 建议改进
1. [建议]
2. [建议]
```

---

*测试文档版本*: v1.0.0  
*创建日期*: 2025-10-17  
*更新日期*: 2025-10-17

