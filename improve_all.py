import asyncio
from pathlib import Path
from src.auto_coder import AutoCoder

async def improve_directory(directory: str = "src"):
    auto_coder = AutoCoder()
    path = Path(directory)
    
    for file_path in path.rglob("*.py"):
        print(f"\nImproving {file_path}...")
        result = await auto_coder.improve_code(file_path)
        
        if result['status'] == 'success':
            print(f"✓ Successfully improved with {result.get('automatic_fixes', 0)} fixes")
        else:
            print(f"✗ Error: {result.get('message', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(improve_directory()) 