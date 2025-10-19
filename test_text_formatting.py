"""
测试文本格式化功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder


def test_chinese_formatting():
    """测试中文文本格式化"""
    print("\n=== 测试中文文本格式化 ===\n")
    
    test_cases = [
        ("用电击攻击对手。有时会让对手陷入麻痹状态。", 
         "用电击攻击对手。 有时会让对手陷入麻痹状态。"),
        
        ("一只用于测试18种技能效果的神秘精灵，拥有电龙双属性。",
         "一只用于测试18种技能效果的神秘精灵， 拥有电龙双属性。"),
        
        ("吸取对手的养分进行攻击。可以回复给予对手伤害的一半HP。",
         "吸取对手的养分进行攻击。 可以回复给予对手伤害的一半HP。"),
        
        ("通过细胞的变化进行液化，从而大幅提高自己的防御。",
         "通过细胞的变化进行液化， 从而大幅提高自己的防御。"),
    ]
    
    for original, expected in test_cases:
        result = Builder.format_text_for_display(original, is_chinese=True)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status} 原文: {original}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        print()


def test_english_formatting():
    """测试英文文本格式化"""
    print("\n=== 测试英文文本格式化 ===\n")
    
    test_cases = [
        ("Attacks the target with an electric shock. May also paralyze the target.",
         "Attacks the target with an electric shock.  May also paralyze the target."),
        
        ("Drains the target's life force. The user recovers half the HP it dealt as damage.",
         "Drains the target's life force.  The user recovers half the HP it dealt as damage."),
        
        ("The user focuses its will and sharply raises its Sp. Def stat.",
         "The user focuses its will and sharply raises its Sp.  Def stat."),
    ]
    
    for original, expected in test_cases:
        result = Builder.format_text_for_display(original, is_chinese=False)
        status = "[PASS]" if result == expected else "[FAIL]"
        print(f"{status} 原文: {original}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        print()


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("文本格式化功能测试")
    print("="*60)
    
    test_chinese_formatting()
    test_english_formatting()
    
    print("\n" + "="*60)
    print("[SUCCESS] 所有测试完成！")
    print("="*60)
    print("\n功能说明:")
    print("- 在中文标点符号后添加空格（。，！？；：）")
    print("- 在英文标点符号后添加空格（. , ! ? ; :）")
    print("- 实现游戏内自动换行，避免文本显示不完全")


if __name__ == "__main__":
    main()

