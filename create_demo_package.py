"""
创建综合演示资源包
展示 CobbleSeer MCP Server 的所有核心功能

功能展示：
1. create_pokemon - 创建宝可梦
2. create_move - 创建自定义技能（规则引擎）
3. build_package - 构建资源包（文件夹格式）
4. 智能依赖检测
5. 智能换行格式化
6. 完整的中英文语言支持
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder
from services.move_generator import MoveGenerator
import yaml


def load_config():
    """加载配置"""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


async def main():
    """创建综合演示资源包"""
    print("\n" + "="*60)
    print("CobbleSeer MCP Server - 综合功能演示")
    print("="*60)
    
    config = load_config()
    builder = Builder(config)
    move_gen = MoveGenerator()
    
    # ============================================================
    # 1. 创建自定义宝可梦
    # ============================================================
    print("\n[1/4] 创建自定义宝可梦：DemoMon...")
    
    pokemon_data = {
        "name": "demomon",
        "dex": 9997,
        "primary_type": "Fire",
        "secondary_type": "Flying",
        "stats": {
            "hp": 90,
            "attack": 110,
            "defence": 80,
            "special_attack": 100,
            "special_defence": 85,
            "speed": 95
        },
        "height": 1.8,
        "weight": 75.5,
        "base_friendship": 70,
        "description_zh": "一只用于展示CobbleSeer所有功能的演示精灵，拥有强大的火焰与飞行能力，掌握多种不同效果的技能。",
        "description_en": "A demonstration Pokemon showcasing all CobbleSeer features. Possesses powerful fire and flying abilities with various move effects."
    }
    
    # 构建基础文件
    base_files = builder.build_all(pokemon_data)
    print(f"  [OK] 基础文件已生成（species, spawn, poser, resolver, lang）")
    
    # ============================================================
    # 2. 创建自定义技能（展示所有效果类型）
    # ============================================================
    print("\n[2/4] 创建自定义技能（10个技能展示不同效果）...")
    
    custom_moves = []
    move_configs = [
        # 状态异常技能
        {
            "name": "demofireblast",
            "type": "Fire",
            "category": "Special",
            "base_power": 110,
            "accuracy": 85,
            "pp": 5,
            "effect": "burn",
            "effect_chance": 30,
            "description": "强力的火焰爆炸攻击，有30%几率灼伤对手。",
            "desc_en": "A powerful fire blast. 30% chance to burn the target."
        },
        {
            "name": "demoparalyze",
            "type": "Electric",
            "category": "Physical",
            "base_power": 80,
            "accuracy": 100,
            "pp": 15,
            "effect": "paralyze",
            "effect_chance": 20,
            "description": "电击对手，有20%几率麻痹。",
            "desc_en": "Electric attack. 20% chance to paralyze."
        },
        
        # 能力提升技能
        {
            "name": "demopowerup",
            "type": "Fighting",
            "category": "Status",
            "base_power": 0,
            "pp": 20,
            "effect": "boost_attack",
            "effect_value": 2,
            "description": "大幅提升自己的攻击力。",
            "desc_en": "Sharply raises the user's Attack."
        },
        {
            "name": "demospeedup",
            "type": "Normal",
            "category": "Status",
            "base_power": 0,
            "pp": 30,
            "effect": "boost_speed",
            "effect_value": 2,
            "description": "大幅提升自己的速度。",
            "desc_en": "Sharply raises the user's Speed."
        },
        
        # 能力削弱技能
        {
            "name": "demoweaken",
            "type": "Dark",
            "category": "Status",
            "base_power": 0,
            "accuracy": 100,
            "pp": 20,
            "effect": "lower_defense",
            "effect_value": 1,
            "description": "降低对手的防御力。",
            "desc_en": "Lowers the target's Defense."
        },
        
        # 特殊效果技能
        {
            "name": "demodrain",
            "type": "Grass",
            "category": "Special",
            "base_power": 75,
            "accuracy": 100,
            "pp": 10,
            "effect": "drain",
            "effect_value": 50,
            "description": "吸取对手的生命力，回复造成伤害的一半HP。",
            "desc_en": "Drains the target. User recovers half the damage dealt."
        },
        {
            "name": "demorecoil",
            "type": "Normal",
            "category": "Physical",
            "base_power": 120,
            "accuracy": 100,
            "pp": 15,
            "effect": "recoil",
            "effect_value": 33,
            "description": "全力冲撞对手，自己也会受到1/3的反伤。",
            "desc_en": "Powerful attack. User takes 1/3 recoil damage."
        },
        
        # 高威力技能
        {
            "name": "demoultimate",
            "type": "Fire",
            "category": "Special",
            "base_power": 150,
            "accuracy": 90,
            "pp": 5,
            "priority": 0,
            "description": "释放极其强大的火焰能量，威力巨大但命中率略低。",
            "desc_en": "Unleashes tremendous fire energy. High power but lower accuracy."
        },
        
        # 先制技能
        {
            "name": "demoquick",
            "type": "Flying",
            "category": "Physical",
            "base_power": 40,
            "accuracy": 100,
            "pp": 30,
            "priority": 1,
            "description": "快速突击对手，必定先制攻击。",
            "desc_en": "Quick strike. Always moves first."
        },
        
        # 必中技能
        {
            "name": "demoaura",
            "type": "Psychic",
            "category": "Special",
            "base_power": 80,
            "accuracy": 0,
            "pp": 20,
            "description": "发射波导之力，攻击必定命中。",
            "desc_en": "Aura attack. Never misses."
        }
    ]
    
    # 使用规则引擎生成技能
    for i, config in enumerate(move_configs, 1):
        print(f"  [{i}/10] 生成技能: {config['name']}...")
        result = move_gen.generate(
            name=config["name"],
            type=config["type"],
            category=config["category"],
            base_power=config.get("base_power", 0),
            accuracy=config.get("accuracy", 100),
            pp=config.get("pp", 10),
            priority=config.get("priority", 0),
            effect=config.get("effect"),
            effect_chance=config.get("effect_chance", 0),
            effect_value=config.get("effect_value", 1),
            description=config.get("description", "")
        )
        
        if result["success"]:
            custom_moves.append({
                "name": config["name"],
                "code": result["code"],
                "description_zh": config.get("description", ""),
                "description_en": config.get("desc_en", "")
            })
    
    print(f"  [OK] 所有技能已生成")
    
    # ============================================================
    # 3. 构建完整的文件结构
    # ============================================================
    print("\n[3/4] 构建完整的数据包结构...")
    
    # 创建 mega_showdown 技能文件结构
    files = {**base_files}
    
    # 添加自定义技能到文件结构
    for move in custom_moves:
        move_path = f"data/mega_showdown/showdown/moves/{move['name']}.js"
        files[move_path] = move["code"]
    
    # 扩展语言文件，添加技能翻译
    for move in custom_moves:
        move_key = move['name']
        files["lang_zh"][f"cobblemon.move.{move_key}"] = move['name'].replace('demo', '演示')
        files["lang_zh"][f"cobblemon.move.{move_key}.desc"] = builder.format_text_for_display(
            move['description_zh'], is_chinese=True
        )
        files["lang_en"][f"cobblemon.move.{move_key}"] = move['name'].replace('demo', 'Demo ')
        files["lang_en"][f"cobblemon.move.{move_key}.desc"] = builder.format_text_for_display(
            move['description_en'], is_chinese=False
        )
    
    # 更新宝可梦的技能表，包含自定义技能
    demomon_moves = [
        "1:tackle",
        "1:growl",
        "5:ember",
        "10:peck",
        "15:demoquick",          # 自定义：快速攻击
        "20:demofireblast",      # 自定义：火焰爆炸
        "25:demoparalyze",       # 自定义：麻痹攻击
        "30:demopowerup",        # 自定义：攻击提升
        "35:demoweaken",         # 自定义：防御削弱
        "40:demodrain",          # 自定义：吸取
        "45:demospeedup",        # 自定义：速度提升
        "50:demorecoil",         # 自定义：反伤攻击
        "55:demoaura",           # 自定义：必中技能
        "60:demoultimate",       # 自定义：终极技能
        "egg:demoparalyze",
        "tm:protect",
        "tm:rest",
        "tm:substitute"
    ]
    
    files["species"]["moves"] = demomon_moves
    
    print(f"  [OK] 文件结构已构建")
    print(f"     - 基础文件: 6个")
    print(f"     - 自定义技能: {len(custom_moves)}个")
    print(f"     - 语言条目: {len(files['lang_zh'])}个（中）+ {len(files['lang_en'])}个（英）")
    
    # ============================================================
    # 4. 生成最终资源包
    # ============================================================
    print("\n[4/4] 生成最终资源包...")
    
    result = builder.build_package("DemoMon_Complete_Package", files)
    
    if result["success"]:
        print(f"  [SUCCESS] 资源包已生成！")
        print(f"\n" + "="*60)
        print("资源包信息")
        print("="*60)
        print(f"输出路径: {result['output_path']}")
        print(f"输出格式: {result['format']}")
        print(f"文件大小: {result['size_mb']} MB")
        print(f"所需模组: {', '.join(result['dependencies'])}")
        print(f"\n包含内容:")
        print(f"  - 自定义宝可梦: DemoMon")
        print(f"  - 自定义技能: {len(custom_moves)}个")
        print(f"  - 语言支持: 中文 + 英文")
        print(f"  - 智能换行: 已启用")
        print(f"  - 依赖检测: 已启用")
        print(f"\n使用方法:")
        print(f"  1. 复制整个文件夹到: .minecraft/saves/你的存档/datapacks/")
        print(f"  2. 进入游戏执行: /reload")
        print(f"  3. 召唤测试: /pokespawn demomon")
        print(f"\n技能列表:")
        for i, move in enumerate(custom_moves, 1):
            print(f"  {i:2d}. {move['name']:20s} - {move['description_zh']}")
        
        print("\n" + "="*60)
        print("[COMPLETE] 综合演示资源包创建完成！")
        print("="*60)
        
        return True
    else:
        print(f"  [FAILED] 生成失败: {result.get('error', 'Unknown error')}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

