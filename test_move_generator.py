"""测试规则引擎技能生成器"""
from services.move_generator import MoveGenerator

def test_move_generator():
    print("\n" + "="*70)
    print("  测试规则引擎技能生成器")
    print("="*70)
    
    gen = MoveGenerator()
    
    # 测试1：电系物理攻击 + 麻痹
    print("\n[测试1] 电系物理攻击 + 麻痹")
    result1 = gen.generate(
        name="Thunder Strike",
        type="Electric",
        category="Physical",
        base_power=90,
        accuracy=100,
        pp=15,
        priority=1,
        effect="paralyze",
        effect_chance=10
    )
    print(f"Success: {result1['success']}")
    print(f"Name: {result1['name']}")
    print(f"\nGenerated Code:")
    print(result1['code'])
    
    # 测试2：吸血技能
    print("\n" + "="*70)
    print("\n[测试2] 草系吸血技能")
    result2 = gen.generate(
        name="Drain Leaf",
        type="Grass",
        category="Special",
        base_power=75,
        accuracy=100,
        pp=10,
        effect="drain",
        effect_value=50
    )
    print(f"Success: {result2['success']}")
    print(f"Name: {result2['name']}")
    print(f"\nGenerated Code:")
    print(result2['code'])
    
    # 测试3：能力提升（变化技能）
    print("\n" + "="*70)
    print("\n[测试3] 攻击提升（变化技能）")
    result3 = gen.generate(
        name="Power Up",
        type="Normal",
        category="Status",
        base_power=0,
        accuracy=100,
        pp=20,
        effect="boost_attack",
        effect_value=2
    )
    print(f"Success: {result3['success']}")
    print(f"Name: {result3['name']}")
    print(f"\nGenerated Code:")
    print(result3['code'])
    
    # 测试4：反伤技能
    print("\n" + "="*70)
    print("\n[测试4] 火系反伤技能")
    result4 = gen.generate(
        name="Flame Crash",
        type="Fire",
        category="Physical",
        base_power=120,
        accuracy=100,
        pp=15,
        effect="recoil",
        effect_value=33
    )
    print(f"Success: {result4['success']}")
    print(f"Name: {result4['name']}")
    print(f"\nGenerated Code:")
    print(result4['code'])
    
    # 测试5：无效果技能
    print("\n" + "="*70)
    print("\n[测试5] 简单攻击（无效果）")
    result5 = gen.generate(
        name="Quick Attack",
        type="Normal",
        category="Physical",
        base_power=40,
        accuracy=100,
        pp=30,
        priority=1,
        effect=None
    )
    print(f"Success: {result5['success']}")
    print(f"Name: {result5['name']}")
    print(f"\nGenerated Code:")
    print(result5['code'])
    
    print("\n" + "="*70)
    print("  测试完成")
    print("="*70)
    print()

if __name__ == "__main__":
    test_move_generator()

