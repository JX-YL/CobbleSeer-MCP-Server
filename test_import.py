"""
Test basic imports and initialization
"""

import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("Testing imports...")
print("="*60)

# Test 1: Import server
try:
    import server
    print("[PASS] server module imported")
except Exception as e:
    print(f"[FAIL] server module import: {e}")
    sys.exit(1)

# Test 2: Check MCP object
try:
    mcp = server.mcp
    print(f"[PASS] MCP object created: {type(mcp)}")
except Exception as e:
    print(f"[FAIL] MCP object: {e}")
    sys.exit(1)

# Test 3: Check tools
try:
    # FastMCP 2.12.4 uses different API
    if hasattr(mcp, 'list_tools'):
        tools = mcp.list_tools()
        print(f"[PASS] list_tools() available: {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool.get('name', 'unknown')}")
    else:
        print(f"[INFO] MCP attributes: {dir(mcp)}")
except Exception as e:
    print(f"[FAIL] Tools: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Import services
try:
    from services.builder import Builder
    print("[PASS] Builder imported")
    
    from services.validator import Validator
    print("[PASS] Validator imported")
    
    print("\n[INFO] Services can be initialized with config")
except Exception as e:
    print(f"[FAIL] Services import: {e}")

# Test 5: Create test data
try:
    from server import PokemonFormData
    pokemon = PokemonFormData(
        name="test_pokemon",
        dex=1001,  # Valid range
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
    print(f"[PASS] PokemonFormData created: {pokemon.name}")
except Exception as e:
    print(f"[FAIL] PokemonFormData: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Import tests completed")
print("="*60)

