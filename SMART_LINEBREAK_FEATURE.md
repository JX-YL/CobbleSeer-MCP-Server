# 智能换行功能 - 语言文件格式化

## 📅 最后更新
2025-01-19

## 🎯 问题与解决方案

### 问题
生成的语言文件在游戏中显示时，长文本可能显示不完全或被截断。

### 原理
Minecraft/Cobblemon 使用**空格作为软换行点**，游戏会根据显示宽度自动在空格处换行。

### 解决方案
CobbleSeer 的 Builder 会**自动添加软换行点**，在合适的位置插入空格。

## ✅ 当前实现（v1.1.1）

### 自动格式化规则

#### 中文文本
1. **标点符号后**添加空格：`。` `，` `！` `？` `；` `：`
2. **常见词后**添加空格：
   - 动词：`攻击` `进行` `提高` `降低` `回复` `给予` `使出` `发射` `释放`
   - 介词/连词：`从而` `并且` `同时` `然后` `接着` `之后`
   - 其他：`对手` `自己` `宝可梦` `招式` `能力` `伤害` `状态`

#### 英文文本
- 标点符号后添加**双空格**：`. ` `, ` `! ` `? ` `; ` `: `

### 示例效果

**原文**：
```
用电击攻击对手。有时会让对手陷入麻痹状态。
```

**格式化后**：
```
用电击 攻击 对手。 有时会让对手 陷入麻痹状态。
```

## 🔧 使用方式

### 自动应用（默认）
```python
builder = Builder(config)
files = builder.build_all(pokemon_data)
# lang_zh 和 lang_en 已自动格式化
```

### 手动调用
```python
from services.builder import Builder

# 格式化中文
text_zh = "用电击攻击对手。有时会让对手陷入麻痹状态。"
formatted = Builder.format_text_for_display(text_zh, is_chinese=True)

# 格式化英文
text_en = "Attacks the target. May also paralyze the target."
formatted = Builder.format_text_for_display(text_en, is_chinese=False)
```

## 📊 效果对比

### Before（无空格）
```json
{
  "cobblemon.move.testthundershock.desc": "用电击攻击对手。有时会让对手陷入麻痹状态。"
}
```
**问题**：游戏可能在任意位置强制截断

### After（自动格式化）
```json
{
  "cobblemon.move.testthundershock.desc": "用电击 攻击 对手。 有时会让对手 陷入麻痹状态。"
}
```
**优势**：游戏在空格处自动换行，显示更完整

## 🎮 实际应用

所有通过 Builder 生成的数据包都已自动应用此功能：
- `create_pokemon` MCP工具
- `build_all()` 方法
- 所有语言文件（zh_cn.json, en_us.json）

## 📝 注意事项

### 1. 不是完美匹配
当前实现基于规则引擎，不能完全匹配Cobblemon官方的手工格式。

**原因**：官方格式经过人工精心设计，考虑了语义和节奏。完美复制需要完整的NLP分词系统。

### 2. 足够大部分场景
自动格式化已经覆盖了大部分常见情况，避免了文本显示问题。

### 3. 可手动调整
如需完美显示效果，可在生成后手动编辑语言文件：
```
生成数据包 → 游戏测试 → 手动调整空格 → 重新测试
```

## 🧪 测试结果

### 测试文件
- `test_text_formatting.py` - 基础测试（标点格式化）
- `test_improved_formatting.py` - 改进测试（语义断点）

### 测试状态
- ✅ 标点后空格：通过
- ✅ 常见词后空格：通过
- ⚠️ 完美匹配参考：部分通过（预期行为）

## 📁 相关文件

### 核心实现
- `services/builder.py` - `format_text_for_display()` 方法

### 文档
- `LINEBREAK_GUIDE.md` - 详细换行指南
- `LINEBREAK_SOLUTION.txt` - 快速参考

### 测试
- `test_text_formatting.py` - 基础测试
- `test_improved_formatting.py` - 改进测试

### 应用
- `output/step2_with_moves/` - 已应用格式化的测试数据包
- `output/Testmon_Complete_DataPack/` - 完整数据包
- `output/Testmon_Final_With_Linebreak/` - 最终版本

## 💡 设计理念

### 平衡自动化与质量
- **自动化**：无需手动处理，开箱即用
- **质量**：覆盖常见场景，避免显示问题
- **灵活性**：支持手动调整以获得最佳效果

### 最小依赖
- 不依赖外部NLP库
- 使用Python标准库（re模块）
- 轻量级，快速执行

## 🔮 未来扩展（可选）

如需更精确的格式化，可考虑：
1. 集成 jieba 中文分词库
2. 基于机器学习的断点预测
3. 可配置的断点词库
4. 实时游戏内预览

## ✨ 特性总结

- ✅ **自动化**：Builder自动应用，无需手动处理
- ✅ **智能化**：在标点和语义断点添加空格
- ✅ **双语支持**：中文单空格，英文双空格
- ✅ **向后兼容**：不影响现有功能
- ✅ **轻量级**：无额外依赖
- ⚠️ **基础实现**：足够大部分场景，支持手动优化

## 📖 用户建议

### 快速开发
直接使用自动格式化，无需调整。

### 追求完美
1. 使用Builder生成数据包
2. 进入游戏测试显示效果
3. 如有需要，手动调整 `zh_cn.json`
4. 重新测试直到满意

### 批量生成
接受自动格式化结果，提高效率。

---

**制作者**：江下犹泷  
**版本**：v1.1.1  
**日期**：2025-01-19  
**状态**：✅ 已实现并集成
