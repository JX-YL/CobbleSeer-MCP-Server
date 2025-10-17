# CobbleSeer MCP Server

> AI驱动的Cobblemon资源包生成器 - MCP Server后端

## 📖 简介

这是一个基于 **MCP (Model Context Protocol)** 的后端服务，为Cobblemon资源包生成提供智能工具支持。

### 核心功能

- 🎯 **创建宝可梦**：自动生成完整的species/spawn/poser/resolver文件
- 🤖 **AI生成技能**：基于自然语言描述生成Showdown格式技能代码
- 🔮 **AI生成特性**：智能生成特性JavaScript代码
- 📚 **RAG检索**：自动从参考库检索相似内容
- ✅ **文件验证**：JSON Schema验证确保文件正确性
- 📦 **资源包构建**：一键打包ZIP

## 🏗️ 技术栈

- **框架**: fastmcp (简化的MCP实现)
- **Web Server**: FastAPI + uvicorn
- **AI**: Claude API (云端) / Ollama (本地可选)
- **RAG**: ChromaDB + sentence-transformers
- **数据库**: SQLite (项目数据)
- **验证**: Pydantic + JSON Schema

## 📂 项目结构

```
cobblemon_mcp_server/
├── server.py                    # fastmcp主入口
├── config.yaml                  # 配置文件
├── requirements.txt             # Python依赖
├── pyproject.toml              # 项目配置
│
├── services/                    # 核心服务
│   ├── __init__.py
│   ├── ai_generator.py         # AI生成服务（混合模式）
│   ├── rag_service.py          # RAG检索服务
│   ├── builder.py              # 文件构建服务
│   └── validator.py            # 文件验证服务
│
├── models/                      # 数据模型
│   ├── __init__.py
│   ├── pokemon.py              # 宝可梦数据模型
│   └── schemas.py              # JSON Schema定义
│
├── utils/                       # 工具函数
│   ├── __init__.py
│   ├── logger.py               # 日志工具
│   └── helpers.py              # 辅助函数
│
└── data/                        # 运行时数据（.gitignore）
    ├── chroma_db/              # 向量数据库
    ├── projects.db             # 项目数据库
    └── cache/                  # 缓存目录
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.11+
- (可选) Ollama（如需本地AI）

### 2. 安装依赖

```bash
cd Cobblemon_mcp_server
pip install -r requirements.txt
```

### 3. 配置

首次运行会自动创建 `config.yaml`，或手动编辑：

```yaml
ai:
  mode: "cloud"  # cloud | local | hybrid
  cloud:
    api_key: "your-api-key"
    model: "claude-3-5-sonnet-20241022"
```

### 4. 启动服务

**stdio模式**（Cursor调用）：
```bash
python server.py
```

**HTTP模式**（Web UI调用）：
```bash
python server.py --http
```

## 🔧 MCP工具列表

### 1. create_pokemon
创建完整的宝可梦配置文件

**输入**：
```json
{
  "name": "example_pokemon",
  "dex": 10001,
  "primary_type": "Fire",
  "stats": {"hp": 80, "attack": 90, ...}
}
```

**输出**：
```json
{
  "success": true,
  "files": {
    "species": {...},
    "spawn": {...},
    "poser": {...}
  }
}
```

### 2. generate_moves
AI生成技能代码

**输入**：
```json
{
  "descriptions": [
    "火系物理攻击，威力90，命中100，有10%几率灼伤"
  ]
}
```

**输出**：
```json
[
  {
    "description": "...",
    "code": "{ num: -10001, ... }",
    "valid": true
  }
]
```

### 3. generate_abilities
AI生成特性代码

### 4. search_reference
从参考库搜索相似内容

### 5. validate_package
验证生成的文件

### 6. build_package
构建并打包资源包

## 🤖 AI模式说明

### 云端模式（推荐）
- ✅ 无硬件要求
- ✅ 速度快（5-10秒）
- ✅ 质量高（95%）
- 💰 需要API Key

### 本地模式
- ⚠️ 需要32GB+运存
- ⚠️ 速度慢（15-25秒）
- ✅ 完全离线
- ✅ 无API成本

### 混合模式
- ✅ 智能切换
- ✅ 简单任务用本地
- ✅ 复杂任务用云端

## 📝 配置文件示例

```yaml
# config.yaml
ai:
  mode: "hybrid"
  
  cloud:
    provider: "claude"
    api_key: "${COBBLESEER_API_KEY}"
    model: "claude-3-5-sonnet-20241022"
  
  local:
    model: "qwen3:7b"
    embedding_model: "qwen3-embedding"
    ollama_host: "http://localhost:11434"

rag:
  enabled: true
  collection_name: "cobblemon_reference"
  top_k: 5

database:
  url: "sqlite:///data/projects.db"

server:
  host: "127.0.0.1"
  port: 8765
  cors_origins: ["http://localhost:5173"]
```

## 🔍 开发调试

### 查看日志

```bash
python server.py --debug
```

### 测试单个工具

```python
# test.py
from server import mcp
import asyncio

async def test():
    result = await mcp.tools["create_pokemon"](
        name="test_mon",
        dex=99999,
        primary_type="Fire",
        stats={"hp": 100, "attack": 100}
    )
    print(result)

asyncio.run(test())
```

## 📚 相关文档

- [技术方案（精简版）](../../../Plan/01-核心方案-精简版.md)
- [技术方案（详细版）](../../../Plan/01-完整方案-详细版.md)
- [文档导航](../../../Plan/README-文档导航.md)

## 🤝 贡献

这是 **江下犹泷** 的项目，欢迎反馈和建议！

## 📄 许可

MIT License

---

**制作者**：江下犹泷  
**最后更新**：2025.10.17

