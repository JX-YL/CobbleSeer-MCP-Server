# 资源包格式选择指南

## 📦 `build_package` 的两种输出格式

`build_package` 工具支持两种输出格式，通过 `output_format` 参数控制。

---

## 格式对比

| 特性 | ZIP 格式 | 文件夹格式 |
|------|---------|-----------|
| **参数值** | `"zip"` (默认) | `"folder"` |
| **输出** | `.zip` 压缩包 | 完整目录结构 |
| **文件数** | 1 个 ZIP 文件 | 11 个独立文件 + 目录 |
| **可编辑性** | 需要解压缩 | 可直接编辑 |
| **分享** | ✅ 非常方便 | ⚠️ 需要打包整个文件夹 |
| **安装** | ✅ 直接拖入游戏 | ✅ 直接拖入游戏 |
| **调试** | ⚠️ 需要解压 | ✅ 即改即用 |
| **版本控制** | ⚠️ 二进制文件 | ✅ Git 友好 |
| **体积** | 小（压缩） | 大（未压缩） |

---

## 📦 ZIP 格式 (推荐用于发布)

### 使用方法

```python
# MCP 工具调用
mcp_cobbleseer_build_package(
    project_name="my_pokemon",
    files={...},
    output_format="zip"  # 👈 或省略（默认就是 zip）
)
```

### 输出示例

```
output/
└── my_pokemon.zip          # 单个 ZIP 文件
```

### 适用场景

✅ **发布到社区**
- CurseForge
- Modrinth
- GitHub Releases
- 论坛分享

✅ **最终交付**
- 给玩家使用
- 存档备份
- 长期保存

✅ **批量分发**
- 服务器资源包
- 模组包整合

### 优点

1. **用户友好**: 一个文件，拖入即用
2. **节省空间**: 压缩后体积小
3. **完整性**: 不会丢失文件
4. **专业**: 看起来更正式

### 缺点

1. **不能直接编辑**: 需要解压 → 修改 → 重新压缩
2. **调试麻烦**: 每次改动都要重新打包
3. **版本控制**: Git 无法追踪内部变化

---

## 📁 文件夹格式 (推荐用于开发)

### 使用方法

```python
# MCP 工具调用
mcp_cobbleseer_build_package(
    project_name="my_pokemon_dev",
    files={...},
    output_format="folder"  # 👈 显式指定 folder
)
```

### 输出示例

```
output/
└── my_pokemon_dev/              # 文件夹
    ├── pack.mcmeta
    ├── README.md
    ├── data/
    │   └── cobblemon/
    │       ├── species/custom/my_pokemon.json
    │       └── spawn_pool_world/my_pokemon.json
    └── assets/
        └── cobblemon/
            ├── bedrock/pokemon/...
            ├── textures/pokemon/...
            └── lang/...
```

### 适用场景

✅ **开发阶段**
- 频繁修改配置
- 调试问题
- 迭代测试

✅ **学习研究**
- 查看文件结构
- 理解配置逻辑
- 参考学习

✅ **版本控制**
- Git 仓库管理
- 团队协作开发
- 追踪变更历史

### 优点

1. **即改即用**: 修改 JSON → `/reload` → 立即生效
2. **调试便捷**: 快速定位和修复问题
3. **Git 友好**: 可以追踪每个文件的变化
4. **透明**: 所有文件一目了然

### 缺点

1. **分享不便**: 需要打包整个文件夹
2. **体积大**: 未压缩，占用更多空间
3. **易丢失**: 文件散落，可能缺失部分

---

## 🎯 推荐工作流程

### 开发阶段 (使用文件夹)

```python
# 1. 创建宝可梦
result = mcp_cobbleseer_create_pokemon(
    name="thunder_wolf",
    dex=1002,
    ...
)

# 2. 导出为文件夹（便于调试）
package = mcp_cobbleseer_build_package(
    project_name="thunder_wolf_dev",
    files=result["files"],
    output_format="folder"  # 👈 开发模式
)

# 3. 复制到游戏目录
# cp -r output/thunder_wolf_dev/ .minecraft/datapacks/

# 4. 游戏内测试
# /reload
# /pokespawn thunder_wolf

# 5. 修改文件（如果需要）
# 直接编辑 output/thunder_wolf_dev/data/cobblemon/species/custom/thunder_wolf.json
# 然后再次 /reload
```

### 发布阶段 (使用 ZIP)

```python
# 1. 确认测试无误后，打包为 ZIP
final_package = mcp_cobbleseer_build_package(
    project_name="thunder_wolf_v1.0",
    files=result["files"],
    output_format="zip"  # 👈 发布模式
)

# 2. 上传到社区
# output/thunder_wolf_v1.0.zip
```

---

## 🔄 两种格式互转

### 文件夹 → ZIP

**方法 1: 使用 MCP 重新打包**
```python
# 读取文件夹中的文件，重新调用 build_package
mcp_cobbleseer_build_package(
    project_name="thunder_wolf",
    files=original_files,  # 原始的 files 字典
    output_format="zip"
)
```

**方法 2: 手动压缩**
```bash
# Windows
Compress-Archive -Path "output/my_pokemon_dev/*" -DestinationPath "output/my_pokemon.zip"

# Linux/Mac
cd output/my_pokemon_dev
zip -r ../my_pokemon.zip *
```

### ZIP → 文件夹

**方法 1: 使用 MCP 重新打包**
```python
mcp_cobbleseer_build_package(
    project_name="thunder_wolf_unpack",
    files=original_files,
    output_format="folder"
)
```

**方法 2: 手动解压**
```bash
# Windows
Expand-Archive -Path "output/my_pokemon.zip" -DestinationPath "output/my_pokemon_unpacked"

# Linux/Mac
unzip output/my_pokemon.zip -d output/my_pokemon_unpacked
```

---

## 📊 实际测试对比

### 测试案例（来自 TEST_REPORT.md）

| 宝可梦 | 格式 | 输出 | 大小 | 用途 |
|--------|------|------|------|------|
| Thunder Wolf | ZIP | `thunder_wolf_fixed.zip` | 4.7 KB | 发布版 |
| Fire Dragon | ZIP | `fire_dragon.zip` | 4.7 KB | 发布版 |
| Ice Phoenix | **Folder** | `ice_phoenix_datapack/` | ~15 KB | 开发版 |
| Water Serpent | ZIP | `water_serpent.zip` | 4.8 KB | 发布版 |

**为什么 Ice Phoenix 是文件夹？**
在完整功能测试中，我故意使用了 `output_format="folder"` 来演示文件夹格式的功能。这不是随机的，也不是 bug，而是**完全可控的功能**。

---

## 🎯 快速决策

### 选择 ZIP 格式 (`output_format="zip"`)

如果你：
- ✅ 要发布给其他人使用
- ✅ 已经完成开发和测试
- ✅ 需要分享到社区
- ✅ 想要整洁的单文件
- ✅ 不需要频繁修改

### 选择文件夹格式 (`output_format="folder"`)

如果你：
- ✅ 正在开发或调试
- ✅ 需要频繁修改配置
- ✅ 使用 Git 版本控制
- ✅ 需要查看文件结构
- ✅ 团队协作开发

---

## ⚙️ 默认值

如果省略 `output_format` 参数，**默认使用 ZIP 格式**：

```python
# 这两个调用是等价的
mcp_cobbleseer_build_package(project_name="my_pokemon", files={...})
mcp_cobbleseer_build_package(project_name="my_pokemon", files={...}, output_format="zip")
```

---

## 💡 最佳实践

### 开发时

```python
# 使用描述性的项目名 + _dev 后缀
mcp_cobbleseer_build_package(
    project_name="thunder_wolf_dev",
    files=files,
    output_format="folder"
)
```

### 发布时

```python
# 使用版本号
mcp_cobbleseer_build_package(
    project_name="thunder_wolf_v1.0.0",
    files=files,
    output_format="zip"
)
```

### Git 仓库

```
project/
├── src/                    # 源文件（文件夹格式）
│   └── thunder_wolf_dev/
├── releases/               # 发布版本（ZIP 格式）
│   ├── thunder_wolf_v1.0.0.zip
│   └── thunder_wolf_v1.1.0.zip
└── .gitignore              # 忽略 *.zip
```

---

## 🔧 故障排除

### Q: 为什么我的资源包是文件夹？
**A**: 检查你的 `output_format` 参数，如果设置为 `"folder"` 则会生成文件夹。

### Q: 如何改为 ZIP 格式？
**A**: 将 `output_format` 改为 `"zip"` 或省略该参数。

### Q: 文件夹格式能直接拖入游戏吗？
**A**: 可以！Minecraft 支持两种格式的数据包：
- `.zip` 文件
- 未压缩的文件夹

### Q: 哪种格式更快？
**A**: 
- **生成速度**: 文件夹格式稍快（无需压缩）
- **加载速度**: 两者相同（游戏都会读取）
- **修改速度**: 文件夹格式快得多（无需解压/压缩）

---

## 📝 总结

| 场景 | 推荐格式 | 原因 |
|------|---------|------|
| 🔧 开发调试 | **文件夹** | 即改即用，快速迭代 |
| 🌐 社区发布 | **ZIP** | 易于分享，用户友好 |
| 👥 团队协作 | **文件夹** | Git 版本控制 |
| 📦 最终交付 | **ZIP** | 专业、整洁、完整 |
| 📚 学习研究 | **文件夹** | 透明、可查看 |
| 💾 长期存储 | **ZIP** | 节省空间 |

---

**记住**: 这不是 bug，而是设计好的功能！根据你的需求选择合适的格式。

---

*本文档版本*: v1.0.0  
*作者*: 江下犹泷 (JX_YL)  
*日期*: 2025-10-17

