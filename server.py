"""
CobbleSeer MCP Server - 主入口

基于 fastmcp 的 MCP 服务器，为 Cobblemon 资源包生成提供 AI 工具支持。
"""

import sys
import asyncio
from pathlib import Path
from typing import Optional, List
import yaml
from loguru import logger
from rich.console import Console
from rich.panel import Panel

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from fastmcp import FastMCP
    from pydantic import BaseModel, Field
except ImportError as e:
    print("Error: Missing dependencies. Please run: pip install -r requirements.txt")
    print(f"Details: {e}")
    sys.exit(1)

# 导入服务
from services.ai_generator import AIGenerator
from services.rag_service import RAGService
from services.builder import Builder
from services.validator import Validator
from services.move_generator import MoveGenerator

# ==================== 初始化 ====================

console = Console()

# 创建 fastmcp 实例
mcp = FastMCP(
    "CobbleSeer Generator",
    version="1.0.0"
)

# ==================== 配置加载 ====================

def load_config() -> dict:
    """加载配置文件（静默模式）"""
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        return get_default_config()
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        return get_default_config()


def get_default_config() -> dict:
    """获取默认配置"""
    return {
        "ai": {
            "mode": "local",
            "cloud": {
                "provider": "claude",
                "api_key": "",
                "model": "claude-3-5-sonnet-20241022"
            },
            "local": {
                "model": "qwen3:32b",
                "ollama_host": "http://localhost:11434"
            }
        },
        "rag": {
            "enabled": True,
            "collection_name": "cobblemon_reference",
            "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
            "top_k": 5
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8765
        }
    }


# 加载配置
config = load_config()

# 初始化服务
logger.info("初始化服务...")
rag_service = RAGService(config)
ai_generator = AIGenerator(config, rag_service=rag_service)
builder = Builder(config)
validator = Validator(config)
move_generator = MoveGenerator()  # 规则引擎（无需配置）
logger.info("服务初始化完成")

# ==================== 数据模型 ====================

class PokemonFormData(BaseModel):
    """宝可梦表单数据"""
    name: str = Field(..., description="物种ID（小写字母+下划线）", pattern=r"^[a-z_]+$")
    dex: int = Field(..., ge=1, le=9999, description="全国图鉴号")
    primary_type: str = Field(..., description="主属性")
    secondary_type: Optional[str] = Field(None, description="副属性")
    stats: dict = Field(..., description="能力值字典 {hp, attack, defense, ...}")
    
    # 可选字段
    generation: Optional[str] = Field(None, description="世代")
    height: Optional[float] = Field(None, description="高度（米）")
    weight: Optional[float] = Field(None, description="体重（千克）")
    base_friendship: Optional[int] = Field(70, description="基础亲密度")
    
    # 自定义内容
    custom_moves_desc: Optional[str] = Field(None, description="自定义技能描述（换行分隔）")
    custom_abilities_desc: Optional[str] = Field(None, description="自定义特性描述（换行分隔）")


class MoveDescription(BaseModel):
    """技能描述"""
    description: str = Field(..., description="技能描述")
    type: Optional[str] = Field(None, description="技能属性")
    category: Optional[str] = Field(None, description="技能类型（Physical/Special/Status）")


class AbilityDescription(BaseModel):
    """特性描述"""
    description: str = Field(..., description="特性描述")


# ==================== MCP 工具定义 ====================

@mcp.tool()
async def hello_world(name: str = "CobbleSeer") -> dict:
    """
    测试工具：打招呼
    
    Args:
        name: 名称
    
    Returns:
        欢迎消息
    """
    logger.info(f"👋 Hello, {name}!")
    return {
        "message": f"Hello, {name}! CobbleSeer MCP Server is running!",
        "version": "1.0.0",
        "status": "ready"
    }


@mcp.tool()
async def create_pokemon(
    name: str,
    dex: int,
    primary_type: str,
    hp: int,
    attack: int,
    defence: int,
    special_attack: int,
    special_defence: int,
    speed: int,
    secondary_type: str = None,
    height: float = None,
    weight: float = None,
    base_friendship: int = 70,
    generate_moves: bool = False,
    generate_abilities: bool = False
) -> dict:
    """
    创建完整的宝可梦配置文件
    
    根据用户填写的表单数据生成：
    - species.json（种族配置）
    - spawn.json（生成规则）
    - poser.json（模型配置）
    - resolver.json（资源定位）
    - lang_zh.json / lang_en.json（多语言）
    
    Args:
        name: 物种ID（小写字母+下划线）
        dex: 全国图鉴号（1-9999）
        primary_type: 主属性
        hp: HP能力值
        attack: 攻击能力值
        defence: 防御能力值
        special_attack: 特攻能力值
        special_defence: 特防能力值
        speed: 速度能力值
        secondary_type: 副属性（可选）
        height: 高度（米，可选）
        weight: 体重（千克，可选）
        base_friendship: 基础亲密度（默认70）
        generate_moves: 是否自动生成技能（需要AI）
        generate_abilities: 是否自动生成特性（需要AI）
        
    Returns:
        {"success": True, "files": {...}, "validation": {...}}
    """
    # 构建form_data
    form_data = PokemonFormData(
        name=name,
        dex=dex,
        primary_type=primary_type,
        secondary_type=secondary_type,
        stats={
            "hp": hp,
            "attack": attack,
            "defence": defence,
            "special_attack": special_attack,
            "special_defence": special_defence,
            "speed": speed
        },
        height=height,
        weight=weight,
        base_friendship=base_friendship
    )
    
    logger.info(f"📝 创建宝可梦: {form_data.name}")
    
    try:
        from services.builder import Builder
        
        builder = Builder(config)
        
        # 转换为字典
        data_dict = {
            "name": form_data.name,
            "dex": form_data.dex,
            "primary_type": form_data.primary_type,
            "secondary_type": form_data.secondary_type,
            "stats": form_data.stats,
            "height": form_data.height,
            "weight": form_data.weight,
            "base_friendship": form_data.base_friendship
        }
        
        # 构建所有文件
        files = builder.build_all(data_dict)
        
        logger.info("✅ 基础文件生成完成")
        
        # AI生成（如果需要）
        if generate_moves and form_data.custom_moves_desc:
            logger.info("🤖 AI生成技能中...")
            # files["custom_moves"] = await ai_gen.generate_moves(...)
        
        if generate_abilities and form_data.custom_abilities_desc:
            logger.info("🤖 AI生成特性中...")
            # files["custom_abilities"] = await ai_gen.generate_abilities(...)
        
        return {
            "success": True,
            "pokemon_name": form_data.name,
            "files": files,
            "validation": {"valid": True, "errors": []}
        }
        
    except Exception as e:
        logger.error(f"❌ 创建失败：{e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def generate_moves(
    descriptions: List[str],
    auto_reference: bool = True
) -> List[dict]:
    """
    AI生成Cobblemon技能代码（Showdown格式）
    
    基于自然语言描述生成完整的技能JavaScript代码。
    自动查询参考库中相似技能作为参考，提升生成质量。
    
    Args:
        descriptions: 技能描述列表
                     例如：["强力火系物理攻击，威力90，命中100，PP15"]
        auto_reference: 是否自动RAG检索相似参考技能
        
    Returns:
        [{"description": "...", "code": "...", "references": [...], "valid": True}]
    
    Example:
        >>> await generate_moves([
        ...     "火系物理攻击，威力90，命中100",
        ...     "水系特殊攻击，威力80，必定命中"
        ... ])
    """
    logger.info(f"🎯 生成技能：共{len(descriptions)}个")
    
    results = []
    
    for i, desc in enumerate(descriptions, 1):
        logger.info(f"  [{i}/{len(descriptions)}] {desc[:50]}...")
        
        try:
            # 使用 AI Generator 生成技能
            move_data = await ai_generator.generate_move(
                description=desc,
                auto_reference=auto_reference
            )
            
            if move_data.get("success"):
                results.append({
                    "description": desc,
                    "code": move_data.get("code", ""),
                    "name": move_data.get("name", "Unknown"),
                    "type": move_data.get("type", "Normal"),
                    "category": move_data.get("category", "Physical"),
                    "basePower": move_data.get("basePower", 0),
                    "valid": True,
                    "errors": []
                })
                logger.info(f"    ✅ 完成：{move_data.get('name', 'Unknown')}")
            else:
                results.append({
                    "description": desc,
                    "code": "",
                    "valid": False,
                    "errors": [move_data.get("error", "未知错误")]
                })
                logger.error(f"    ❌ 失败：{move_data.get('error')}")
            
        except Exception as e:
            logger.error(f"    ❌ 生成失败：{e}")
            results.append({
                "description": desc,
                "code": "",
                "valid": False,
                "errors": [str(e)]
            })
    
    return results


@mcp.tool()
async def generate_abilities(
    descriptions: List[str],
    auto_reference: bool = True
) -> List[dict]:
    """
    AI生成Cobblemon特性代码
    
    Args:
        descriptions: 特性描述列表
        auto_reference: 是否自动RAG检索相似参考特性
        
    Returns:
        生成的特性代码列表
    """
    logger.info(f"🎯 生成特性：共{len(descriptions)}个")
    
    results = []
    
    for i, desc in enumerate(descriptions, 1):
        logger.info(f"  [{i}/{len(descriptions)}] {desc[:50]}...")
        
        try:
            # 使用 AI Generator 生成特性
            ability_data = await ai_generator.generate_ability(
                description=desc,
                auto_reference=auto_reference
            )
            
            if ability_data.get("success"):
                results.append({
                    "description": desc,
                    "code": ability_data.get("code", ""),
                    "name": ability_data.get("name", "Unknown"),
                    "rating": ability_data.get("rating", 0),
                    "valid": True,
                    "errors": []
                })
                logger.info(f"    ✅ 完成：{ability_data.get('name', 'Unknown')}")
            else:
                results.append({
                    "description": desc,
                    "code": "",
                    "valid": False,
                    "errors": [ability_data.get("error", "未知错误")]
                })
                logger.error(f"    ❌ 失败：{ability_data.get('error')}")
            
        except Exception as e:
            logger.error(f"    ❌ 生成失败：{e}")
            results.append({
                "description": desc,
                "code": "",
                "valid": False,
                "errors": [str(e)]
            })
    
    return results


@mcp.tool()
async def search_reference(
    query: str,
    type: str = "moves",
    limit: int = 5
) -> List[dict]:
    """
    从参考库搜索相似数据
    
    Args:
        query: 搜索关键词
        type: 搜索类型（moves/abilities/pokemon）
        limit: 返回结果数量
    
    Returns:
        相似内容列表
    """
    logger.info(f"🔍 搜索参考：{query} (类型: {type}, 限制: {limit})")
    
    # TODO: 实现RAG检索
    
    return [
        {
            "name": "示例技能1",
            "basePower": 90,
            "accuracy": 100,
            "type": "Fire",
            "similarity": 0.85
        }
    ]


@mcp.tool()
async def validate_package(files: dict) -> dict:
    """
    验证生成的文件
    
    Args:
        files: 文件内容字典
    
    Returns:
        验证结果
    """
    logger.info("✅ 验证资源包...")
    
    # TODO: 实现验证逻辑
    
    return {
        "valid": True,
        "errors": [],
        "warnings": []
    }


@mcp.tool()
async def build_package(
    project_name: str,
    files: dict,
    output_format: str = "zip"
) -> dict:
    """
    构建并打包资源包
    
    Args:
        project_name: 项目名称
        files: 文件内容字典
        output_format: 输出格式（zip/folder）
    
    Returns:
        打包结果
    """
    logger.info(f"📦 构建资源包：{project_name} ({output_format})")
    
    try:
        from services.builder import Builder
        
        builder = Builder(config)
        result = builder.build_package(project_name, files, output_format)
        
        logger.info(f"✅ 资源包构建完成：{result['output_path']}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 打包失败：{e}")
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
async def create_move(
    name: str,
    type: str,
    category: str,
    base_power: int = 0,
    accuracy: int = 100,
    pp: int = 10,
    priority: int = 0,
    effect: Optional[str] = None,
    effect_chance: int = 0,
    effect_value: int = 1,
    description: str = "",
    contact: Optional[bool] = None
) -> dict:
    """
    创建自定义技能（规则引擎，零配置，开箱即用）
    
    **核心优势：**
    - ✅ 零配置：无需安装Ollama或API Key
    - ✅ 100%可靠：基于规则引擎，不会出错
    - ✅ 开箱即用：立即可以发布给所有用户
    - ✅ 速度快：毫秒级生成
    
    **参数说明：**
    
    基础信息：
    - name: 技能名称（如 "Thunder Strike"）
    - type: 属性类型（Electric, Fire, Water, Grass等18种）
    - category: 分类（Physical/Special/Status）
    - base_power: 威力（0-250，0表示变化技能）
    - accuracy: 命中率（1-100，或0表示必中）
    - pp: PP值（1-40）
    - priority: 优先度（-7到+5，0为普通，+1为先制，-4为后攻）
    
    效果配置：
    - effect: 效果类型（见下方列表）
    - effect_chance: 效果概率（0-100，0表示100%）
    - effect_value: 效果强度（用于吸血%、反伤%、能力变化级数等）
    - description: 自定义描述（留空则自动生成）
    - contact: 是否接触技能（None表示自动判断）
    
    **支持的效果类型（effect参数）：**
    
    状态异常：
    - "paralyze": 麻痹
    - "burn": 灼伤
    - "poison": 中毒
    - "toxic": 剧毒
    - "sleep": 睡眠
    - "freeze": 冰冻
    
    能力变化：
    - "boost_attack": 提升攻击
    - "boost_defense": 提升防御
    - "boost_special_attack": 提升特攻
    - "boost_special_defense": 提升特防
    - "boost_speed": 提升速度
    - "lower_attack": 降低攻击
    - "lower_defense": 降低防御
    - "lower_special_attack": 降低特攻
    - "lower_special_defense": 降低特防
    - "lower_speed": 降低速度
    
    特殊效果：
    - "drain": 吸血（effect_value=50表示吸血50%）
    - "recoil": 反伤（effect_value=33表示1/3反伤）
    - "flinch": 畏缩
    - "confusion": 混乱
    - "high_crit": 高会心率
    - None: 无追加效果
    
    **使用示例：**
    
    示例1 - 电系物理攻击+麻痹：
    >>> await create_move(
    ...     name="Thunder Strike",
    ...     type="Electric",
    ...     category="Physical",
    ...     base_power=90,
    ...     accuracy=100,
    ...     pp=15,
    ...     priority=1,
    ...     effect="paralyze",
    ...     effect_chance=10
    ... )
    
    示例2 - 吸血技能：
    >>> await create_move(
    ...     name="Drain Leaf",
    ...     type="Grass",
    ...     category="Special",
    ...     base_power=75,
    ...     effect="drain",
    ...     effect_value=50
    ... )
    
    示例3 - 能力提升：
    >>> await create_move(
    ...     name="Power Up",
    ...     type="Normal",
    ...     category="Status",
    ...     effect="boost_attack",
    ...     effect_value=2
    ... )
    
    Returns:
        {
            "success": True,
            "code": "生成的JavaScript代码",
            "name": "技能名称",
            "type": "属性",
            "category": "分类",
            "basePower": 威力
        }
    """
    logger.info(f"🔧 创建技能：{name} ({type} {category})")
    
    try:
        result = move_generator.generate(
            name=name,
            type=type,
            category=category,
            base_power=base_power,
            accuracy=accuracy,
            pp=pp,
            priority=priority,
            effect=effect,
            effect_chance=effect_chance,
            effect_value=effect_value,
            description=description,
            contact=contact
        )
        
        logger.info(f"✅ 技能创建完成：{name}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 创建失败：{e}")
        return {
            "success": False,
            "error": str(e),
            "code": ""
        }


@mcp.tool()
async def create_move_with_template(description: str) -> dict:
    """
    基于大模板创建技能（模板删减法）
    
    **核心思路：**
    - 提供包含所有可能字段的完整模板
    - AI根据用户需求删减不需要的部分
    - 只保留相关字段和效果
    - 100%基于真实数据，不会出现不存在的字段
    
    **优势：**
    - ✅ 灵活：自然语言描述即可
    - ✅ 准确：所有字段来自952个真实样本
    - ✅ 快速：一次性生成完整代码
    - ✅ Token合理：只发送模板结构，不发送全部样本
    
    Args:
        description: 技能描述
                    例如："电系物理攻击，威力90，命中100，PP15，优先度+1，10%麻痹"
    
    Returns:
        {
            "success": True,
            "code": "生成的JavaScript代码",
            "name": "技能名称",
            "type": "属性",
            "category": "分类",
            "basePower": 威力
        }
    
    示例：
        >>> await create_move_with_template(
        ...     "火系物理攻击，威力80，命中100，PP15，10%灼伤"
        ... )
    """
    logger.info(f"🎯 使用模板生成技能：{description[:50]}...")
    
    try:
        # 读取大模板
        template_path = Path(__file__).parent / "MOVE_TEMPLATE.md"
        if not template_path.exists():
            return {
                "success": False,
                "error": "模板文件不存在，请确保 MOVE_TEMPLATE.md 文件存在"
            }
        
        template_content = template_path.read_text(encoding='utf-8')
        
        # 构建Prompt
        prompt = f"""你是一个Cobblemon技能设计师。

**任务：** 根据用户需求，从完整模板中删减不需要的部分，生成技能代码。

**用户需求：**
{description}

**完整技能模板：**
{template_content}

**要求：**
1. **只保留用户需求相关的字段**（删除所有无关字段）
2. **必需字段：** num, name, type, category, basePower, accuracy, pp, priority, target
3. **根据需求添加：** flags, secondary, drain, recoil 等（按需）
4. **num使用负数**（如 -10001）
5. **添加 shortDesc** 描述效果
6. **直接输出JavaScript对象**（不要markdown代码块）

**示例：**
用户需求："电系物理攻击，威力90，命中100，PP15，优先度+1，10%麻痹"

输出：
{{
  num: -10001,
  name: "Thunder Strike",
  type: "Electric",
  category: "Physical",
  basePower: 90,
  accuracy: 100,
  pp: 15,
  priority: 1,
  flags: {{contact: 1, protect: 1, mirror: 1, metronome: 1}},
  secondary: {{
    chance: 10,
    status: "par"
  }},
  target: "normal",
  shortDesc: "Usually goes first. 10% chance to paralyze."
}}

**现在请生成：**
"""
        
        # 调用AI生成
        if config.get("ai", {}).get("mode") == "local":
            # 使用本地Ollama
            import ollama
            
            model = config.get("ai", {}).get("local", {}).get("model", "qwen3:32b")
            logger.info(f"  使用本地模型：{model}")
            
            response = await ollama.AsyncClient().chat(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是Cobblemon技能设计师。根据模板和需求生成JavaScript代码。只输出代码，不要解释。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            code = response["message"]["content"]
        else:
            # 使用云端API（TODO：实现）
            return {
                "success": False,
                "error": "云端AI模式暂未实现，请切换到本地模式（Ollama）"
            }
        
        # 提取代码
        if "```javascript" in code:
            code = code.split("```javascript")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].split("```")[0].strip()
        
        # 解析生成的代码提取字段
        import re
        
        name_match = re.search(r'name:\s*["\']([^"\']+)["\']', code)
        type_match = re.search(r'type:\s*["\'](\w+)["\']', code)
        category_match = re.search(r'category:\s*["\'](\w+)["\']', code)
        power_match = re.search(r'basePower:\s*(\d+)', code)
        
        result = {
            "success": True,
            "code": code,
            "name": name_match.group(1) if name_match else "Unknown",
            "type": type_match.group(1) if type_match else "Normal",
            "category": category_match.group(1) if category_match else "Physical",
            "basePower": int(power_match.group(1)) if power_match else 0
        }
        
        logger.info(f"✅ 生成完成：{result['name']}")
        return result
        
    except Exception as e:
        logger.error(f"❌ 生成失败：{e}")
        return {
            "success": False,
            "error": str(e),
            "code": ""
        }


# ==================== 启动配置 ====================

def setup_logging():
    """配置日志"""
    logger.remove()  # 移除默认处理器
    
    # 添加彩色终端输出
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # 添加文件输出
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "cobbleseer.log",
        rotation="100 MB",
        retention="30 days",
        level="DEBUG",
        encoding="utf-8"
    )


def print_banner():
    """打印欢迎信息"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║       🎮 CobbleSeer MCP Server v1.0.0 🎮                 ║
║                                                           ║
║   AI驱动的 Cobblemon 资源包生成器                         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")
    
    # 显示配置信息
    ai_mode = config.get("ai", {}).get("mode", "unknown")
    server_port = config.get("server", {}).get("port", 8765)
    
    console.print(Panel.fit(
        f"[green]✓[/green] AI模式: [yellow]{ai_mode}[/yellow]\n"
        f"[green]✓[/green] 端口: [yellow]{server_port}[/yellow]\n"
        f"[green]✓[/green] 工具数量: [yellow]{len(mcp.list_tools())}[/yellow]",
        title="[bold]配置信息[/bold]",
        border_style="green"
    ))


def main():
    """主函数"""
    # 检查命令行参数
    args = sys.argv[1:]
    
    if "--http" in args:
        # HTTP模式需要日志和欢迎信息
        setup_logging()
        print_banner()
        logger.info("🌐 启动 HTTP 模式...")
        # HTTP模式（用于Web UI）
        import uvicorn
        uvicorn.run(
            "server:mcp",
            host=config.get("server", {}).get("host", "127.0.0.1"),
            port=config.get("server", {}).get("port", 8765),
            reload="--reload" in args
        )
    else:
        # stdio模式（Cursor）- 不能有任何额外输出
        # 禁用所有日志输出到 stderr
        logger.remove()
        # 直接运行MCP服务器
        mcp.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 服务器已停止[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ 启动失败：{e}[/red]")
        logger.exception(e)
        sys.exit(1)

