import asyncio
from src.auto_coder import AutoCoder
from pathlib import Path

async def main():
    auto_coder = AutoCoder()
    file_path = Path('test_improvement.py')
    
    print(f"Analyzing file: {file_path}")
    print("Current content:")
    print("-" * 40)
    print(file_path.read_text())
    print("-" * 40)
    
    # Get issues first
    issues = auto_coder.analyzer.analyze_file(file_path)
    print("\nDetected issues:", issues)
    
    # Try improvements
    result = await auto_coder.improve_code(file_path)
    print("\nImprovement Result:", result)
    
    if result['status'] == 'success':
        print("\nFile after improvements:")
        print("-" * 40)
        print(file_path.read_text())
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main()) 