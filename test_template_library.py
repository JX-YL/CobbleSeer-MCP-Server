"""测试模板库功能"""
from services.template_library import TemplateLibrary
from pathlib import Path

def test_template_library():
    print("\n" + "="*70)
    print("  测试模板库")
    print("="*70)
    
    # 初始化
    ref_dir = "E:/AI Super Personal Studio/Reference document/Cobblemon/对决参考"
    lib = TemplateLibrary(ref_dir)
    
    # 测试1：加载技能
    print("\n[测试1] 加载技能数据")
    moves = lib.load_moves()
    print(f"✅ 成功加载 {len(moves)} 个技能")
    
    # 显示几个示例
    print("\n示例技能：")
    for i, (move_id, move_data) in enumerate(list(moves.items())[:3]):
        print(f"\n{i+1}. {move_id}")
        print(f"   名称: {move_data.get('name', 'N/A')}")
        print(f"   属性: {move_data.get('type', 'N/A')}")
        print(f"   分类: {move_data.get('category', 'N/A')}")
        print(f"   威力: {move_data.get('basePower', 0)}")
        print(f"   命中: {move_data.get('accuracy', 'N/A')}")
        print(f"   优先度: {move_data.get('priority', 0)}")
        if 'secondary' in move_data and move_data['secondary']:
            print(f"   追加效果: {move_data['secondary']}")
    
    # 测试2：搜索电系技能
    print("\n" + "="*70)
    print("\n[测试2] 搜索电系物理攻击技能")
    electric_moves = lib.search_moves(
        type="Electric",
        category="Physical",
        limit=5
    )
    print(f"✅ 找到 {len(electric_moves)} 个结果：")
    for move in electric_moves:
        print(f"  - {move.get('name')}: 威力{move.get('basePower', 0)}, 命中{move.get('accuracy', 100)}")
    
    # 测试3：搜索高优先度技能
    print("\n" + "="*70)
    print("\n[测试3] 搜索高优先度技能")
    priority_moves = lib.search_moves(
        has_priority=True,
        limit=10
    )
    print(f"✅ 找到 {len(priority_moves)} 个结果：")
    for move in priority_moves:
        print(f"  - {move.get('name')} (优先度{move.get('priority', 0)}): "
              f"{move.get('type')}, 威力{move.get('basePower', 0)}")
    
    # 测试4：根据效果查找参考技能
    print("\n" + "="*70)
    print("\n[测试4] 查找麻痹效果的参考技能")
    paralyze_move = lib.get_move_by_effect('paralyze')
    if paralyze_move:
        print(f"✅ 找到参考技能：")
        print(f"   名称: {paralyze_move.get('name')}")
        print(f"   属性: {paralyze_move.get('type')}")
        print(f"   威力: {paralyze_move.get('basePower', 0)}")
        print(f"   追加效果: {paralyze_move.get('secondary')}")
    
    # 测试5：查找吸血效果
    print("\n" + "="*70)
    print("\n[测试5] 查找吸血效果的参考技能")
    drain_move = lib.get_move_by_effect('drain')
    if drain_move:
        print(f"✅ 找到参考技能：")
        print(f"   名称: {drain_move.get('name')}")
        print(f"   威力: {drain_move.get('basePower', 0)}")
        print(f"   吸血: {drain_move.get('drain')}")
    
    # 测试6：加载特性
    print("\n" + "="*70)
    print("\n[测试6] 加载特性数据")
    abilities = lib.load_abilities()
    print(f"✅ 成功加载 {len(abilities)} 个特性")
    
    # 显示几个示例
    print("\n示例特性：")
    for i, (ability_id, ability_data) in enumerate(list(abilities.items())[:3]):
        print(f"\n{i+1}. {ability_id}")
        print(f"   名称: {ability_data.get('name', 'N/A')}")
        print(f"   评级: {ability_data.get('rating', 'N/A')}星")
        if 'flags' in ability_data:
            print(f"   标志: {ability_data['flags']}")
    
    print("\n" + "="*70)
    print("  测试完成")
    print("="*70)
    print()

if __name__ == "__main__":
    test_template_library()

