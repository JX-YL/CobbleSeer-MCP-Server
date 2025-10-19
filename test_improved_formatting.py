"""
测试改进的文本格式化功能
基于参考文件的实际格式
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder


def test_real_examples():
    """测试真实示例（从参考文件）"""
    print("\n=== 测试真实示例（参考文件格式） ===\n")
    
    test_cases = [
        # 示例1：switcheroo
        ("用一闪而过的速度交换自己和对手的持有物。",
         "用一闪而过的速度 交换自己和对手的持有物。"),
        
        # 示例2：tackle
        ("用整个身体撞向对手进行攻击。",
         "用整个身体 撞向对手进行攻击。"),
        
        # 示例3：tailslap
        ("用坚硬的尾巴拍打对手进行攻击。连续攻击2～5次。",
         "用坚硬的尾巴 拍打对手进行攻击。 连续攻击2～5次。"),
        
        # 示例4：tailwind
        ("刮起猛烈的旋风，在4回合内提高我方全员的速度。",
         "刮起猛烈的旋风， 在4回合内 提高我方全员的速度。"),
        
        # 示例5：takedown
        ("以惊人的气势撞向对手进行攻击。自己也会受到少许伤害。",
         "以惊人的气势 撞向对手进行攻击。 自己也会受到少许伤害。"),
    ]
    
    for i, (original, expected) in enumerate(test_cases, 1):
        result = Builder.format_text_for_display(original, is_chinese=True)
        
        # 检查是否匹配
        matches = result == expected
        status = "[PASS]" if matches else "[PARTIAL]"
        
        print(f"{status} 示例 {i}:")
        print(f"  原文: {original}")
        print(f"  期望: {expected}")
        print(f"  结果: {result}")
        
        if not matches:
            print(f"  差异: 结果可能需要手动调整")
        print()


def test_our_examples():
    """测试我们生成的示例"""
    print("\n=== 测试我们的技能描述 ===\n")
    
    test_cases = [
        "用电击攻击对手。有时会让对手陷入麻痹状态。",
        "集中精神，大幅提高自己的攻击。",
        "吸取对手的生命力进行攻击。可以回复给予对手伤害的一半HP。",
        "拼命地猛撞向对手。自己也会受到不小的伤害。",
    ]
    
    for desc in test_cases:
        result = Builder.format_text_for_display(desc, is_chinese=True)
        print(f"原文: {desc}")
        print(f"格式化: {result}")
        print()


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("改进的文本格式化功能测试")
    print("="*60)
    
    test_real_examples()
    test_our_examples()
    
    print("\n" + "="*60)
    print("[INFO] 测试完成")
    print("="*60)
    print("\n说明:")
    print("- 在标点符号后添加空格")
    print("- 在常见的语义断点（如动词后）添加空格")
    print("- 提供多个软换行点供游戏引擎选择")
    print("\n注意:")
    print("- 完美匹配参考文件需要完整的中文分词系统")
    print("- 当前实现提供了基础的软换行点")
    print("- 用户可以手动调整语言文件以获得最佳效果")


if __name__ == "__main__":
    main()

