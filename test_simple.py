"""
CobbleSeer MCP Server - Simple Test
Test basic functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from server import mcp, PokemonFormData


async def test_hello():
    """Test hello_world tool"""
    print("\n" + "="*60)
    print("Test 1/3: hello_world")
    print("="*60)
    
    try:
        result = await mcp.tools["hello_world"](name="Test")
        print(f"Success: {result['message']}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


async def test_create():
    """Test create_pokemon tool"""
    print("\n" + "="*60)
    print("Test 2/3: create_pokemon")
    print("="*60)
    
    try:
        pokemon = PokemonFormData(
            name="test_pokemon",
            dex=99999,
            primary_type="Fire",
            stats={
                "hp": 100,
                "attack": 110,
                "defence": 90,
                "special_attack": 120,
                "special_defence": 95,
                "speed": 105
            }
        )
        
        result = await mcp.tools["create_pokemon"](
            form_data=pokemon,
            generate_moves=False,
            generate_abilities=False
        )
        
        if result["success"]:
            print(f"Success: Created {result['pokemon_name']}")
            print(f"Files: {list(result['files'].keys())}")
            return True
        else:
            print(f"Failed: {result.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_validate():
    """Test validate_package tool"""
    print("\n" + "="*60)
    print("Test 3/3: validate_package")
    print("="*60)
    
    try:
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
        
        print(f"Validation completed")
        print(f"Valid: {result['valid']}")
        print(f"Errors: {len(result['errors'])}")
        print(f"Warnings: {len(result['warnings'])}")
        return True
            
    except Exception as e:
        print(f"Failed: {e}")
        return False


async def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("CobbleSeer MCP Server - Basic Tests")
    print("="*60)
    
    tests = [
        ("hello_world", test_hello),
        ("create_pokemon", test_create),
        ("validate_package", test_validate),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            print(f"\nTest {name} exception: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"[{status}] {name}")
    
    print("-"*60)
    print(f"Total: {passed}/{total} passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\nAll tests passed!")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(run_tests())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nTest run failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

