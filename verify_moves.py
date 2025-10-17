#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证生成的宝可梦是否包含技能表"""

import zipfile
import json
from pathlib import Path

# 检查thunder_wolf_v2.zip
zip_path = Path(__file__).parent / "output" / "thunder_wolf_v2.zip"

with zipfile.ZipFile(zip_path, 'r') as zf:
    species_data = json.loads(zf.read('data/cobblemon/species/custom/thunder_wolf.json'))
    
    print("=" * 60)
    print("Thunder Wolf V2 - Moves Verification")
    print("=" * 60)
    print()
    
    moves = species_data.get('moves', [])
    print(f"Total moves: {len(moves)}")
    print()
    
    if moves:
        print("Skill List:")
        for i, move in enumerate(moves, 1):
            if 'level' in move:
                print(f"  {i}. Level {move['level']:2d}: {', '.join(move['moves'])}")
            elif 'egg' in move:
                print(f"  {i}. Egg Moves: {', '.join(move['egg'])}")
            elif 'tm' in move:
                print(f"  {i}. TM Moves: {', '.join(move['tm'])}")
    else:
        print("ERROR: No moves found!")
    
    print()
    print("=" * 60)

