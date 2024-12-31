import sys
import asyncio
from pathlib import Path

# Add the project root directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Change relative imports to absolute imports
from src.main import AutoCoder
from src.config import default_config
from src.core.improvement_tracker import ImprovementTracker

async def run_full_review():
    config = default_config()
    auto_coder = AutoCoder(config)
    tracker = ImprovementTracker(config)
    
    # Get all Python files in the project
    project_root = Path(__file__).parent.parent
    python_files = list(project_root.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files to analyze")
    
    for file_path in python_files:
        print(f"\nAnalyzing {file_path.relative_to(project_root)}...")
        result = await auto_coder.improve_code(file_path)
        
        if result['status'] == 'success':
            if 'improvements' in result:
                print(f"Found {len(result['improvements'])} potential improvements")
                # Record improvements in database
                tracker.record_improvements(file_path, result['improvements'])
            else:
                print("No improvements needed")
        else:
            print(f"Error: {result.get('issues', 'Unknown error')}")
    
    # Show summary from database
    all_improvements = tracker.get_improvements()
    print("\n=== Review Summary ===")
    print(f"Total files analyzed: {len(python_files)}")
    print(f"Total improvements found: {len(all_improvements)}")
    
    # Group by type
    by_type = {}
    for imp in all_improvements:
        imp_type = imp['type']
        by_type[imp_type] = by_type.get(imp_type, 0) + 1
    
    print("\nImprovements by type:")
    for imp_type, count in by_type.items():
        print(f"- {imp_type}: {count}")

if __name__ == "__main__":
    asyncio.run(run_full_review()) 