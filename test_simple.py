from services.template_library import TemplateLibrary
import json

lib = TemplateLibrary('E:/AI Super Personal Studio/Reference document/Cobblemon/对决参考')
moves = lib.load_moves()

print(f"\nLoaded {len(moves)} moves\n")

# 显示第一个技能
sample = list(moves.items())[0]
print(f"Sample Move ID: {sample[0]}")
print(json.dumps(sample[1], indent=2, ensure_ascii=False))

# 搜索电系技能
print("\n" + "="*60)
print("Searching Electric moves...")
electric = lib.search_moves(type="Electric", limit=5)
print(f"Found {len(electric)} Electric moves:")
for m in electric:
    print(f"  - {m.get('name')}: Power={m.get('basePower', 0)}, Acc={m.get('accuracy', 100)}")

# 搜索优先度技能
print("\n" + "="*60)
print("Searching Priority moves...")
priority = lib.search_moves(has_priority=True, limit=5)
print(f"Found {len(priority)} Priority moves:")
for m in priority:
    print(f"  - {m.get('name')} (Priority {m.get('priority', 0)}): {m.get('type')}")
