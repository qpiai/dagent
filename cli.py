#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from framework import AgenticDAG


async def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py 'your query here'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    framework = AgenticDAG()
    result = await framework.execute(query)

    if result["success"]:
        print("Execution completed successfully!")
    else:
        print(f"Execution failed: {result.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())