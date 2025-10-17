"""
Test MCP Server tool registration
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from server import mcp

async def test():
    # Test tool listing
    print("=" * 60)
    print("Testing MCP Server Tool Registration")
    print("=" * 60)

    tools = await mcp.get_tools()
    print(f"\nTotal tools registered: {len(tools)}")

    for i, tool in enumerate(tools, 1):
        if isinstance(tool, str):
            print(f"\n{i}. {tool}")
        elif isinstance(tool, dict):
            print(f"\n{i}. {tool.get('name', 'Unknown')}")
            desc = tool.get('description', 'No description')
            if len(desc) > 80:
                print(f"   Description: {desc[:80]}...")
            else:
                print(f"   Description: {desc}")
        else:
            print(f"\n{i}. {getattr(tool, 'name', str(tool))}")
            desc = getattr(tool, 'description', 'No description')
            if len(desc) > 80:
                print(f"   Description: {desc[:80]}...")
            else:
                print(f"   Description: {desc}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test())

