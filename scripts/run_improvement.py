import asyncio
from pathlib import Path
from src.auto_coder import AutoCoder
import json

async def main():
    auto_coder = AutoCoder()
    
    # Specify the file you want to improve
    file_path = Path("path/to/your/file.py")
    
    result = await auto_coder.improve_code(file_path)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 