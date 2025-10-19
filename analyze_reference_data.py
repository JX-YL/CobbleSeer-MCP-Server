"""
分析参考数据结构
提取技能和特性的模式
"""
import json
import re
from pathlib import Path
from collections import Counter, defaultdict

def parse_js_object(file_path):
    """解析JS文件中的对象数据"""
    content = Path(file_path).read_text(encoding='utf-8')
    
    # 查找主对象定义
    match = re.search(r'const (Moves|Abilities|Pokemon) = ({[\s\S]*?});', content)
    if not match:
        print(f"[ERROR] Cannot find object definition in {file_path}")
        return None
    
    obj_str = match.group(2)
    
    # 简单统计（不尝试完整解析，因为包含函数）
    items = re.findall(r'^\s+(\w+): {', obj_str, re.MULTILINE)
    
    return items

def analyze_moves(moves_file):
    """分析技能数据"""
    print("\n" + "="*70)
    print("  技能数据分析 (moves.js)")
    print("="*70)
    
    content = Path(moves_file).read_text(encoding='utf-8')
    
    # 统计数量
    items = re.findall(r'^\s+(\w+): {', content, re.MULTILINE)
    print(f"\n总技能数量: {len(items)}")
    
    # 统计分类
    categories = re.findall(r'category: "(\w+)"', content)
    category_count = Counter(categories)
    print(f"\n分类统计:")
    for cat, count in category_count.most_common():
        print(f"  - {cat}: {count}")
    
    # 统计属性
    types = re.findall(r'type: "(\w+)"', content)
    type_count = Counter(types)
    print(f"\n属性统计 (Top 10):")
    for typ, count in type_count.most_common(10):
        print(f"  - {typ}: {count}")
    
    # 统计优先度
    priorities = re.findall(r'priority: (-?\d+)', content)
    priority_count = Counter(priorities)
    print(f"\n优先度统计:")
    for pri, count in sorted(priority_count.items(), key=lambda x: int(x[0])):
        print(f"  - {pri}: {count}")
    
    # 统计追加效果
    secondary_exists = len(re.findall(r'secondary: {', content))
    secondary_null = len(re.findall(r'secondary: null', content))
    print(f"\n追加效果:")
    print(f"  - 有追加效果: {secondary_exists}")
    print(f"  - 无追加效果: {secondary_null}")
    
    # 统计常见标志
    flags_pattern = r'flags: {([^}]+)}'
    all_flags = []
    for flags_match in re.finditer(flags_pattern, content):
        flags_str = flags_match.group(1)
        flag_names = re.findall(r'(\w+): 1', flags_str)
        all_flags.extend(flag_names)
    
    flag_count = Counter(all_flags)
    print(f"\n常见标志 (Top 10):")
    for flag, count in flag_count.most_common(10):
        print(f"  - {flag}: {count}")
    
    # 威力分布
    powers = re.findall(r'basePower: (\d+)', content)
    power_ints = [int(p) for p in powers if int(p) > 0]
    if power_ints:
        print(f"\n威力统计:")
        print(f"  - 最小: {min(power_ints)}")
        print(f"  - 最大: {max(power_ints)}")
        print(f"  - 平均: {sum(power_ints) // len(power_ints)}")
        
        # 威力档位
        power_ranges = defaultdict(int)
        for p in power_ints:
            if p < 50:
                power_ranges["<50"] += 1
            elif p < 80:
                power_ranges["50-79"] += 1
            elif p < 100:
                power_ranges["80-99"] += 1
            elif p < 120:
                power_ranges["100-119"] += 1
            else:
                power_ranges[">=120"] += 1
        
        print(f"\n威力档位:")
        for range_name, count in sorted(power_ranges.items()):
            print(f"  - {range_name}: {count}")

def analyze_abilities(abilities_file):
    """分析特性数据"""
    print("\n" + "="*70)
    print("  特性数据分析 (abilities.js)")
    print("="*70)
    
    content = Path(abilities_file).read_text(encoding='utf-8')
    
    # 统计数量
    items = re.findall(r'^\s+(\w+): {', content, re.MULTILINE)
    print(f"\n总特性数量: {len(items)}")
    
    # 统计评级
    ratings = re.findall(r'rating: ([\d.]+)', content)
    rating_floats = [float(r) for r in ratings]
    if rating_floats:
        rating_count = Counter([int(r) for r in rating_floats])
        print(f"\n评级统计:")
        for rating, count in sorted(rating_count.items()):
            print(f"  - {rating}星: {count}")
    
    # 统计事件处理器类型
    event_handlers = re.findall(r'(on[A-Z]\w+)\(', content)
    handler_count = Counter(event_handlers)
    print(f"\n常见事件处理器 (Top 15):")
    for handler, count in handler_count.most_common(15):
        print(f"  - {handler}: {count}")
    
    # 统计简单特性（只有基础字段，无函数）
    simple_abilities = 0
    complex_abilities = 0
    
    # 简单统计：如果有on开头的方法，就是复杂特性
    for item in items:
        ability_match = re.search(rf'{item}: {{([^}}]+?)}}', content, re.DOTALL)
        if ability_match:
            ability_content = ability_match.group(1)
            if 'on' in ability_content.lower() and '(' in ability_content:
                complex_abilities += 1
            else:
                simple_abilities += 1
    
    print(f"\n复杂度分析:")
    print(f"  - 简单特性（纯数据）: {simple_abilities}")
    print(f"  - 复杂特性（包含代码）: {complex_abilities}")

def extract_common_patterns(moves_file):
    """提取常见技能模式"""
    print("\n" + "="*70)
    print("  提取常见技能模式")
    print("="*70)
    
    content = Path(moves_file).read_text(encoding='utf-8')
    
    # 提取追加效果模式
    print("\n常见追加效果:")
    
    # 状态异常
    status_effects = re.findall(r'status: "(\w+)"', content)
    status_count = Counter(status_effects)
    print("\n  状态异常:")
    for status, count in status_count.most_common():
        print(f"    - {status}: {count}次")
    
    # 能力变化
    boost_patterns = re.findall(r'boosts: {([^}]+)}', content)
    boost_stats = []
    for boost in boost_patterns:
        stats = re.findall(r'(\w+): (-?\d+)', boost)
        boost_stats.extend([f"{stat}:{val}" for stat, val in stats])
    
    boost_count = Counter(boost_stats)
    print("\n  能力变化 (Top 10):")
    for boost, count in boost_count.most_common(10):
        print(f"    - {boost}: {count}次")
    
    # 特殊效果
    print("\n  特殊效果:")
    drain_count = len(re.findall(r'drain:', content))
    recoil_count = len(re.findall(r'recoil:', content))
    heal_count = len(re.findall(r'heal:', content))
    multihit_count = len(re.findall(r'multihit:', content))
    
    print(f"    - drain (吸血): {drain_count}")
    print(f"    - recoil (反伤): {recoil_count}")
    print(f"    - heal (回复): {heal_count}")
    print(f"    - multihit (多次攻击): {multihit_count}")

if __name__ == "__main__":
    # 参考数据路径
    ref_dir = Path("E:/AI Super Personal Studio/Reference document/Cobblemon/对决参考")
    
    moves_file = ref_dir / "moves.js"
    abilities_file = ref_dir / "abilities.js"
    
    print("\n" + "="*70)
    print("  Cobblemon 参考数据分析工具")
    print("="*70)
    print(f"\n数据源: {ref_dir}")
    
    if moves_file.exists():
        analyze_moves(moves_file)
        extract_common_patterns(moves_file)
    else:
        print(f"\n[ERROR] 文件不存在: {moves_file}")
    
    if abilities_file.exists():
        analyze_abilities(abilities_file)
    else:
        print(f"\n[ERROR] 文件不存在: {abilities_file}")
    
    print("\n" + "="*70)
    print("  分析完成")
    print("="*70)
    print()

