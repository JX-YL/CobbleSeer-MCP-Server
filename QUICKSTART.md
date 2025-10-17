# 🚀 CobbleSeer MCP Server - 快速开始

> 5分钟快速上手指南

---

## ⚡ 最快开始方式

### Windows用户

```bash
# 1. 双击运行
start.bat

# 2. 选择模式
# 输入 1（Cursor调用）或 2（Web UI调用）
```

### Linux/Mac用户

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python server.py            # stdio模式
python server.py --http     # HTTP模式
```

---

## 🔧 首次配置

### 选项1：云端AI（推荐）

**适合人群**：所有用户（无硬件要求）

1. **获取Claude API Key**
   - 访问：https://console.anthropic.com/
   - 注册/登录
   - 创建API Key（格式：sk-ant-xxx）

2. **编辑配置文件**
   ```yaml
   # config.yaml
   ai:
     mode: "cloud"
     cloud:
       api_key: "sk-ant-YOUR_API_KEY_HERE"  # 填入你的API Key
   ```

3. **启动服务**
   ```bash
   python server.py --http
   ```

4. **测试**
   - 浏览器访问：http://127.0.0.1:8765
   - 或在Cursor中添加MCP配置

### 选项2：本地AI

**硬件要求**：≥32GB运存，≥8GB显存

1. **安装Ollama**
   - 访问：https://ollama.ai/
   - 下载安装

2. **下载模型**
   ```bash
   ollama pull qwen3:7b            # 7B版本（12GB运存）
   ollama pull qwen3-embedding     # 嵌入模型
   ```

3. **编辑配置文件**
   ```yaml
   # config.yaml
   ai:
     mode: "local"
     local:
       model: "qwen3:7b"
   ```

4. **启动服务**
   ```bash
   python server.py --http
   ```

### 选项3：混合模式（灵活）

**适合人群**：有高配电脑，但也想使用云端AI

```yaml
# config.yaml
ai:
  mode: "hybrid"
  cloud:
    api_key: "sk-ant-xxx"
  local:
    model: "qwen3:7b"
```

---

## 🎯 在Cursor中使用

### 1. 添加MCP配置

**Windows**: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`

**Mac/Linux**: `~/.config/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

```json
{
  "mcpServers": {
    "cobbleseer": {
      "command": "python",
      "args": [
        "E:/AI Super Personal Studio/Workspace/Cobblemon/Cobblemon_mcp_server/server.py"
      ]
    }
  }
}
```

### 2. 重启Cursor

### 3. 测试工具

在Cursor中输入：

```
请调用 hello_world 工具测试连接
```

### 4. 开始使用

```
请帮我创建一只火系宝可梦，图鉴号10001，名称fire_dragon
```

---

## 🌐 在Web UI中使用

### 1. 启动HTTP模式

```bash
python server.py --http
```

### 2. 访问服务

浏览器打开：http://127.0.0.1:8765

### 3. API文档

访问：http://127.0.0.1:8765/docs

---

## ✅ 验证安装

### 测试脚本

创建 `test.py`：

```python
import asyncio
from server import mcp

async def test():
    # 测试hello_world
    result = await mcp.tools["hello_world"](name="Test")
    print(result)
    
    # 测试create_pokemon
    from server import PokemonFormData
    
    pokemon = PokemonFormData(
        name="test_pokemon",
        dex=99999,
        primary_type="Fire",
        stats={
            "hp": 100,
            "attack": 110,
            "defence": 90,
            "special_attack": 120,
            "special_defence": 95,
            "speed": 105
        }
    )
    
    result = await mcp.tools["create_pokemon"](form_data=pokemon)
    print(result)

asyncio.run(test())
```

运行：

```bash
python test.py
```

---

## 🐛 常见问题

### Q1: `ModuleNotFoundError: No module named 'fastmcp'`

**解决**：
```bash
pip install -r requirements.txt
```

### Q2: Claude API Key无效

**解决**：
1. 检查API Key格式（应以 `sk-ant-` 开头）
2. 确认API Key有效且有额度
3. 检查网络连接

### Q3: Ollama连接失败

**解决**：
1. 确认Ollama已启动：`ollama list`
2. 检查模型是否已下载：`ollama pull qwen3:7b`
3. 检查端口：`http://localhost:11434`

### Q4: ChromaDB初始化失败

**解决**：
```bash
pip install chromadb sentence-transformers
```

### Q5: 启动后无响应

**解决**：
1. 查看日志：`logs/cobbleseer.log`
2. 尝试调试模式：`python server.py --http --reload`
3. 检查端口占用：`netstat -ano | findstr 8765`

---

## 📚 下一步

- [ ] 阅读完整文档：[README.md](./README.md)
- [ ] 查看技术方案：[核心方案（精简版）](../../../Plan/01-核心方案-精简版.md)
- [ ] 开发Web UI
- [ ] 索引参考数据（RAG）

---

## 💡 小技巧

### 调试模式

```bash
# 显示详细日志 + 自动重载
python server.py --http --reload
```

### 查看可用工具

```python
from server import mcp
print(mcp.list_tools())
```

### 修改配置后重启

```bash
# Windows
Ctrl + C
start.bat

# Linux/Mac
Ctrl + C
python server.py --http
```

---

**祝你使用愉快！** 🎉

有问题？查看 [README.md](./README.md) 或提Issue

---

**制作者**：江下犹泷

