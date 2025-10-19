"""
测试优化后的Builder功能
测试项：
1. 依赖检测功能
2. 文件夹格式输出
3. README中的依赖信息
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder
import yaml


def load_config():
    """加载配置"""
    config_path = Path(__file__).parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def test_dependency_detection():
    """测试依赖检测功能"""
    print("\n" + "="*60)
    print("测试 1: 依赖检测功能")
    print("="*60)
    
    config = load_config()
    builder = Builder(config)
    
    # 测试用例1：只有基础文件（只需Cobblemon）
    files_basic = {
        "species": {"name": "testmon"},
        "spawn": {},
        "poser": {},
        "resolver": {}
    }
    
    deps_basic = builder.detect_dependencies(files_basic)
    print(f"\n基础宝可梦的依赖: {deps_basic}")
    assert deps_basic == ["Cobblemon"], f"预期 ['Cobblemon']，实际 {deps_basic}"
    print("[PASS] 基础宝可梦依赖检测通过")
    
    # 测试用例2：包含自定义技能（需要Mega Showdown）
    files_with_moves = {
        "species": {"name": "testmon"},
        "data/mega_showdown/showdown/moves/custom_move.js": "// move code"
    }
    
    deps_with_moves = builder.detect_dependencies(files_with_moves)
    print(f"\n带自定义技能的依赖: {deps_with_moves}")
    assert "Cobblemon" in deps_with_moves, "应包含 Cobblemon"
    assert "Mega Showdown" in deps_with_moves, "应包含 Mega Showdown"
    print("[PASS] 自定义技能依赖检测通过")


def test_folder_output():
    """测试文件夹格式输出"""
    print("\n" + "="*60)
    print("测试 2: 文件夹格式输出")
    print("="*60)
    
    config = load_config()
    builder = Builder(config)
    
    # 创建测试数据
    test_data = {
        "name": "test_optimization",
        "dex": 9998,
        "primary_type": "Electric",
        "stats": {
            "hp": 80,
            "attack": 80,
            "defence": 80,
            "special_attack": 80,
            "special_defence": 80,
            "speed": 80
        }
    }
    
    # 构建文件
    files = builder.build_all(test_data)
    
    # 构建资源包（文件夹格式）
    result = builder.build_package("test_optimization", files)
    
    print(f"\n构建结果:")
    print(f"  - 成功: {result['success']}")
    print(f"  - 输出路径: {result['output_path']}")
    print(f"  - 格式: {result['format']}")
    print(f"  - 大小: {result['size_mb']} MB")
    print(f"  - 依赖: {result['dependencies']}")
    
    # 验证
    assert result['success'], "构建应该成功"
    assert result['format'] == "folder", f"格式应为 folder，实际为 {result['format']}"
    assert Path(result['output_path']).exists(), "输出路径应存在"
    assert Path(result['output_path']).is_dir(), "输出应为文件夹"
    assert result['dependencies'] == ["Cobblemon"], f"基础宝可梦只需要 Cobblemon"
    
    print("[PASS] 文件夹格式输出测试通过")
    
    return result['output_path']


def test_readme_content(output_path):
    """测试README内容"""
    print("\n" + "="*60)
    print("测试 3: README依赖信息")
    print("="*60)
    
    readme_path = Path(output_path) / "README.md"
    assert readme_path.exists(), "README.md 应存在"
    
    readme_content = readme_path.read_text(encoding="utf-8")
    
    # 检查关键内容
    checks = [
        ("## 📦 所需模组", "应包含'所需模组'章节"),
        ("- **Cobblemon**", "应列出 Cobblemon"),
        ("## 📁 文件结构", "应包含文件结构"),
        ("## 🎮 使用方法", "应包含使用方法"),
    ]
    
    for pattern, description in checks:
        assert pattern in readme_content, f"{description}（未找到：{pattern}）"
        print(f"[PASS] {description}")
    
    # 检查是否没有Mega Showdown警告（因为是基础宝可梦）
    if "Mega Showdown" not in readme_content or "⚠️ 重要提示" not in readme_content:
        print("[PASS] 基础宝可梦不包含Mega Showdown警告")
    
    print("\n[PASS] README内容测试通过")


def main():
    """运行所有测试"""
    print("\n[START] 开始测试优化后的Builder功能...")
    
    try:
        # 测试1: 依赖检测
        test_dependency_detection()
        
        # 测试2: 文件夹输出
        output_path = test_folder_output()
        
        # 测试3: README内容
        test_readme_content(output_path)
        
        print("\n" + "="*60)
        print("[SUCCESS] 所有测试通过!")
        print("="*60)
        print(f"\n生成的测试数据包位于: {output_path}")
        print("\n优化总结:")
        print("  1. [OK] 依赖检测功能正常")
        print("  2. [OK] 文件夹格式输出正常")
        print("  3. [OK] README依赖信息完整")
        print("  4. [OK] 无需压缩包，直接可用")
        
    except AssertionError as e:
        print(f"\n[FAIL] 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

