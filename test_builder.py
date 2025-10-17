"""
测试 Builder 文件生成功能
"""

import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.builder import Builder
import yaml

def test_builder():
    """测试 Builder 生成功能"""
    print("=" * 60)
    print("测试 Builder 文件生成")
    print("=" * 60)
    
    # 加载配置
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    # 创建 Builder
    builder = Builder(config)
    print(f"\n输出目录: {builder.output_dir}")
    print(f"绝对路径: {builder.output_dir.absolute()}")
    
    # 准备测试数据
    pokemon_data = {
        "name": "thunder_wolf",
        "dex": 1002,
        "primary_type": "Electric",
        "secondary_type": None,
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
    }
    
    # 构建所有文件
    print("\n正在构建文件...")
    files = builder.build_all(pokemon_data)
    
    print(f"\n生成的文件类型: {list(files.keys())}")
    
    # 打包
    print("\n正在打包...")
    result = builder.build_package("thunder_wolf", files, "zip")
    
    print(f"\n打包结果:")
    print(f"  成功: {result['success']}")
    print(f"  路径: {result['output_path']}")
    print(f"  大小: {result['size_mb']} MB")
    
    # 验证文件
    output_path = Path(result['output_path'])
    if output_path.exists():
        print(f"\n文件已创建: {output_path}")
        print(f"实际大小: {output_path.stat().st_size / 1024:.2f} KB")
        
        # 列出 ZIP 内容
        import zipfile
        with zipfile.ZipFile(output_path, 'r') as zipf:
            print(f"\nZIP 内容 ({len(zipf.namelist())} 个文件):")
            for name in sorted(zipf.namelist()):
                info = zipf.getinfo(name)
                print(f"  {name} ({info.file_size} bytes)")
    else:
        print(f"\n错误: 文件不存在: {output_path}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        test_builder()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

