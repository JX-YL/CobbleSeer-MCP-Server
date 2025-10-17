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

# 导入服务（延迟导入，避免循环依赖）
# from services.ai_generator import AIGenerator
# from services.rag_service import RAGService
# from services.builder import Builder
# from services.validator import Validator

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
            "mode": "cloud",
            "cloud": {
                "provider": "claude",
                "api_key": "",
                "model": "claude-3-5-sonnet-20241022"
            },
            "local": {
                "model": "qwen3:7b",
                "ollama_host": "http://localhost:11434"
            }
        },
        "rag": {
            "enabled": True,
            "collection_name": "cobblemon_reference"
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8765
        }
    }


# 加载配置
config = load_config()

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
            # TODO: 实现AI生成逻辑
            # 1. RAG检索参考
            references = []
            if auto_reference:
                logger.info("    🔍 查询参考库...")
                # references = await rag.search_moves(desc, top_k=3)
            
            # 2. AI生成
            logger.info("    🤖 AI生成中...")
            # code = await ai_gen.generate_move(desc, references)
            
            # 临时返回（演示）
            code = """
{
  num: -10001,
  accuracy: 100,
  basePower: 90,
  category: "Physical",
  name: "Example Move",
  pp: 15,
  priority: 0,
  flags: {contact: 1, protect: 1, mirror: 1},
  secondary: {chance: 10, status: "brn"},
  target: "normal",
  type: "Fire"
}
            """.strip()
            
            results.append({
                "description": desc,
                "code": code,
                "references": [r.get("name", "") for r in references],
                "valid": True,
                "errors": []
            })
            
            logger.info("    ✅ 完成")
            
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
    descriptions: List[str]
) -> List[dict]:
    """
    AI生成Cobblemon特性代码
    
    Args:
        descriptions: 特性描述列表
        
    Returns:
        生成的特性代码列表
    """
    logger.info(f"🎯 生成特性：共{len(descriptions)}个")
    
    # TODO: 实现（类似generate_moves）
    
    return [
        {
            "description": desc,
            "code": "// TODO: 实现特性生成",
            "valid": False,
            "errors": ["功能开发中"]
        }
        for desc in descriptions
    ]


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

