"""
CobbleSeer MCP Server - 基础功能测试

测试所有核心工具是否正常工作
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from server import mcp, PokemonFormData
from loguru import logger


async def test_hello_world():
    """测试hello_world工具"""
    print("\n" + "="*60)
    print("测试 1/6: hello_world")
    print("="*60)
    
    try:
        result = await mcp.tools["hello_world"](name="CobbleSeer Test")
        print(f"✅ 成功：{result['message']}")
        return True
    except Exception as e:
        print(f"❌ 失败：{e}")
        return False


async def test_create_pokemon():
    """测试create_pokemon工具"""
    print("\n" + "="*60)
    print("测试 2/6: create_pokemon")
    print("="*60)
    
    try:
        # 创建测试数据
        pokemon = PokemonFormData(
            name="test_fire_dragon",
            dex=99999,
            primary_type="Fire",
            secondary_type="Dragon",
            stats={
                "hp": 100,
                "attack": 110,
                "defence": 90,
                "special_attack": 120,
                "special_defence": 95,
                "speed": 105
            },
            height=1.8,
            weight=90.5,
            base_friendship=70
        )
        
        result = await mcp.tools["create_pokemon"](
            form_data=pokemon,
            generate_moves=False,
            generate_abilities=False
        )
        
        if result["success"]:
            print(f"✅ 成功创建宝可梦：{result['pokemon_name']}")
            print(f"   生成文件：{list(result['files'].keys())}")
            return True
        else:
            print(f"❌ 创建失败：{result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ 失败：{e}")
        logger.exception(e)
        return False


async def test_generate_moves():
    """测试generate_moves工具"""
    print("\n" + "="*60)
    print("测试 3/6: generate_moves")
    print("="*60)
    
    try:
        descriptions = [
            "火系物理攻击，威力90，命中100，PP15",
        ]
        
        result = await mcp.tools["generate_moves"](
            descriptions=descriptions,
            auto_reference=False  # 暂时关闭RAG
        )
        
        if result and len(result) > 0:
            move = result[0]
            print(f"✅ 成功生成技能")
            print(f"   描述：{move['description'][:50]}...")
            print(f"   有效：{move['valid']}")
            if move['code']:
                print(f"   代码长度：{len(move['code'])} 字符")
            return True
        else:
            print(f"❌ 生成失败：无结果")
            return False
            
    except Exception as e:
        print(f"❌ 失败：{e}")
        logger.exception(e)
        return False


async def test_search_reference():
    """测试search_reference工具"""
    print("\n" + "="*60)
    print("测试 4/6: search_reference")
    print("="*60)
    
    try:
        result = await mcp.tools["search_reference"](
            query="火焰攻击",
            type="moves",
            limit=3
        )
        
        print(f"✅ 成功搜索，找到 {len(result)} 个结果")
        if result:
            print(f"   示例：{result[0].get('name', 'Unknown')}")
        return True
            
    except Exception as e:
        print(f"❌ 失败：{e}")
        logger.exception(e)
        return False


async def test_validate_package():
    """测试validate_package工具"""
    print("\n" + "="*60)
    print("测试 5/6: validate_package")
    print("="*60)
    
    try:
        # 创建测试文件
        files = {
            "species": {
                "name": "test_mon",
                "nationalPokedexNumber": 10001,
                "primaryType": "Fire",
                "baseStats": {
                    "hp": 100,
                    "attack": 110,
                    "defence": 90,
                    "special_attack": 120,
                    "special_defence": 95,
                    "speed": 105
                }
            }
        }
        
        result = await mcp.tools["validate_package"](files=files)
        
        print(f"✅ 验证完成")
        print(f"   有效：{result['valid']}")
        print(f"   错误：{len(result['errors'])} 个")
        print(f"   警告：{len(result['warnings'])} 个")
        return True
            
    except Exception as e:
        print(f"❌ 失败：{e}")
        logger.exception(e)
        return False


async def test_build_package():
    """测试build_package工具"""
    print("\n" + "="*60)
    print("测试 6/6: build_package")
    print("="*60)
    
    try:
        files = {
            "species": {"test": "data"},
            "spawn": {"test": "data"}
        }
        
        result = await mcp.tools["build_package"](
            project_name="test_project",
            files=files,
            output_format="zip"
        )
        
        if result["success"]:
            print(f"✅ 构建成功")
            print(f"   输出路径：{result['output_path']}")
            return True
        else:
            print(f"❌ 构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 失败：{e}")
        logger.exception(e)
        return False


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("CobbleSeer MCP Server - Basic Functionality Tests")
    print("="*60)
    
    tests = [
        ("hello_world", test_hello_world),
        ("create_pokemon", test_create_pokemon),
        ("generate_moves", test_generate_moves),
        ("search_reference", test_search_reference),
        ("validate_package", test_validate_package),
        ("build_package", test_build_package),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            print(f"\n❌ 测试 {name} 异常：{e}")
            results[name] = False
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print("-"*60)
    print(f"总计：{passed}/{total} 通过 ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 所有测试通过！MCP Server工作正常！")
        return 0
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_all_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试运行失败：{e}")
        logger.exception(e)
        sys.exit(1)

