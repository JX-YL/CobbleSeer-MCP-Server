#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""批量生成带技能表的宝可梦资源包"""

import sys
import yaml
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder

# 加载配置
config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 创建Builder
builder = Builder(config)

# 4只宝可梦的数据
pokemons = [
    {
        "name": "thunder_wolf",
        "dex": 1002,
        "primary_type": "Electric",
        "stats": {
            "hp": 85,
            "attack": 105,
            "defence": 75,
            "special_attack": 115,
            "special_defence": 80,
            "speed": 120
        },
        "height": 1.2,
        "weight": 45.0,
        "base_friendship": 70
    },
    {
        "name": "fire_dragon",
        "dex": 2001,
        "primary_type": "Fire",
        "secondary_type": "Flying",
        "stats": {
            "hp": 78,
            "attack": 130,
            "defence": 90,
            "special_attack": 105,
            "special_defence": 85,
            "speed": 102
        },
        "height": 2.5,
        "weight": 150.5,
        "base_friendship": 50
    },
    {
        "name": "ice_phoenix",
        "dex": 2002,
        "primary_type": "Ice",
        "secondary_type": "Flying",
        "stats": {
            "hp": 90,
            "attack": 85,
            "defence": 75,
            "special_attack": 125,
            "special_defence": 100,
            "speed": 115
        },
        "height": 1.8,
        "weight": 45.0,
        "base_friendship": 70
    },
    {
        "name": "water_serpent",
        "dex": 2003,
        "primary_type": "Water",
        "stats": {
            "hp": 95,
            "attack": 110,
            "defence": 95,
            "special_attack": 80,
            "special_defence": 70,
            "speed": 75
        },
        "height": 4.2,
        "weight": 220.0,
        "base_friendship": 60
    }
]

print("=" * 60)
print("批量生成带技能表的宝可梦资源包")
print("=" * 60)
print()

for i, pokemon_data in enumerate(pokemons, 1):
    name = pokemon_data["name"]
    print(f"{i}/{len(pokemons)}: 正在生成 {name}...")
    
    # 构建所有文件
    files = builder.build_all(pokemon_data)
    
    # 检查是否包含moves
    has_moves = "moves" in files.get("species", {})
    moves_count = len(files["species"].get("moves", [])) if has_moves else 0
    
    print(f"  - Species: OK")
    print(f"  - Moves: {moves_count} skills" if has_moves else "  - Moves: FAILED")
    
    # 打包为ZIP
    result = builder.build_package(
        project_name=f"{name}_v2",
        files=files,
        output_format="zip"
    )
    
    if result["success"]:
        print(f"  - Package: {result['output_path']}")
        print(f"  - SUCCESS!")
    else:
        print(f"  - FAILED: {result.get('error')}")
    
    print()

print("=" * 60)
print("ALL DONE! Generated packages:")
print()
print("  - output/thunder_wolf_v2.zip")
print("  - output/fire_dragon_v2.zip")
print("  - output/ice_phoenix_v2.zip")
print("  - output/water_serpent_v2.zip")
print()
print("Replace old datapacks in .minecraft/datapacks/, then run /reload")
print("=" * 60)

