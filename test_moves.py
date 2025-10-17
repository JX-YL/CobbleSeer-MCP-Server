#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试技能生成功能"""

import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder
import yaml

# 加载配置
config_path = Path(__file__).parent / "config.yaml"
with open(config_path, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 创建Builder
builder = Builder(config)

# 测试数据
test_data = {
    "name": "test_electric",
    "dex": 9999,
    "primary_type": "Electric",
    "stats": {
        "hp": 85,
        "attack": 105,
        "defence": 75,
        "special_attack": 115,
        "special_defence": 80,
        "speed": 120
    }
}

# 构建species
species = builder.build_species(test_data)

# 检查moves
print("=== Species Keys ===")
print(list(species.keys()))
print()

print("=== Has Moves ===")
print("moves" in species)
print()

if "moves" in species:
    print("=== Moves Count ===")
    print(len(species["moves"]))
    print()
    
    print("=== First 3 Moves ===")
    for i, move in enumerate(species["moves"][:3]):
        print(f"{i+1}. {json.dumps(move, indent=2, ensure_ascii=False)}")
    print()
else:
    print("ERROR: No moves in species!")

