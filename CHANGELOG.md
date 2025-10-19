# CobbleSeer MCP Server - 更新日志

## v1.1.0 (2025-01-19)

### 🎉 重大优化

#### 1. 移除压缩包功能
- **移除**：不再生成 ZIP 压缩包
- **保留**：只生成文件夹格式数据包
- **原因**：
  - Minecraft 原生支持文件夹格式数据包
  - 避免 Windows 压缩的编码/路径问题
  - 生成速度更快（无压缩步骤）
  - 更方便开发者调试和修改

#### 2. 智能依赖检测
- **新增**：`Builder.detect_dependencies()` 方法
- **功能**：自动检测数据包所需的模组
  - 基础宝可梦 → `["Cobblemon"]`
  - 自定义技能/特性 → `["Cobblemon", "Mega Showdown"]`
- **体现**：在生成的 README.md 中自动添加"所需模组"部分

#### 3. 优化 README 生成
- **新增**：依赖信息显示
- **新增**：Mega Showdown 警告提示
- **改进**：时间戳精确到秒
- **格式**：
  ```markdown
  ## 📦 所需模组
  - **Cobblemon**
  - **Mega Showdown**
  
  **⚠️ 重要提示**：此数据包包含自定义技能或特性...
  ```

#### 4. 更新 MCP 工具接口
- **修改**：`build_package` 工具移除 `output_format` 参数
- **返回值新增**：
  - `format`: "folder"（固定）
  - `dependencies`: 所需模组列表
  
```python
# 旧版本
await build_package(project_name="test", files={}, output_format="zip")

# 新版本
await build_package(project_name="test", files={})
# 返回: {"success": True, "format": "folder", "dependencies": ["Cobblemon"]}
```

### 🗑️ 移除的文件
- `PACKAGE_FORMAT_GUIDE.md` - 格式指南（已过时）
- `FULL_FEATURE_TEST.md` - 完整测试文档（已过时）
- `services/builder.py` 中的 `_create_zip_package()` 方法

### 📝 文件更新
- `services/builder.py`:
  - 移除 `zipfile` 导入
  - 添加 `detect_dependencies()` 方法
  - 简化 `build_package()` 方法
  - 优化 `_create_folder_package()` 方法
- `server.py`:
  - 更新 `build_package` MCP 工具签名
  - 移除 `output_format` 参数
- `README.md`:
  - 添加"最新优化"章节
  - 更新功能列表
  - 更新工具说明
- `batch_generate_with_moves.py`:
  - 移除 `output_format="zip"` 调用
- `test_basic.py`:
  - 移除 `output_format="zip"` 调用

### 🎯 设计理念
采用"统一架构，功能分层"策略：
- ✅ 单一版本，无需选择
- ✅ 智能检测依赖，自动提示
- ✅ 原版功能 → 扩展功能平滑过渡
- ✅ 维护成本更低

### ⚠️ 破坏性变更
- **MCP 工具**: `build_package` 的 `output_format` 参数已移除
- **输出格式**: 不再支持 ZIP 压缩包

### 🔄 迁移指南
如果你的代码中使用了 `output_format` 参数：
```python
# 旧代码
result = builder.build_package("my_project", files, output_format="folder")

# 新代码（移除参数）
result = builder.build_package("my_project", files)
# result["format"] 永远是 "folder"
# result["dependencies"] 包含所需模组列表
```

---

## v1.0.0 (2025-01-18)

### 初始版本
- ✅ 创建宝可梦配置
- ✅ AI 生成技能
- ✅ AI 生成特性
- ✅ RAG 检索
- ✅ 文件验证
- ✅ 资源包构建（ZIP/文件夹）
- ✅ 规则引擎技能生成

