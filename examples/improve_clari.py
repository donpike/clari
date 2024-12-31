import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.main import AutoCoder
from src.config import default_config

async def improve_clari_project():
    config = default_config()
    coder = AutoCoder(config)
    
    # 1. First, let's analyze our core files
    core_files = [
        'src/core/safety.py',
        'src/core/improvement_tracker.py',
        'src/core/batch_processor.py'
    ]
    
    print("🔍 Analyzing core components...")
    for file in core_files:
        result = await coder.improve_code(Path(file))
        if result['status'] == 'success':
            print(f"✅ {file}: {len(result['improvements'])} improvements suggested")
            print("   Patterns found:", result['pattern_type'])
        else:
            print(f"❌ {file}: {result['issues']}")
            
    # 2. Let's improve the project structure
    print("\n📁 Analyzing project structure...")
    structure_result = await coder.analyze_project_structure(Path('src'))
    print("Suggested reorganization:", structure_result['suggestions'])
    
    # 3. Check for common patterns across files
    print("\n🔄 Looking for common patterns...")
    patterns = coder.tracker.get_common_patterns()
    print("Most common patterns found:", patterns)
    
    # 4. Generate automated improvements
    print("\n🤖 Generating automated improvements...")
    improvements = await coder.batch_process_directory(
        Path('src'),
        safety_level='high',
        max_changes_per_file=5
    )
    
    # 5. Show statistics
    print("\n📊 Project Statistics:")
    stats = coder.tracker.get_improvement_stats()
    print(f"Success rate: {stats['success_rate']}%")
    print("Common improvements:", stats['successful_patterns'])

if __name__ == "__main__":
    asyncio.run(improve_clari_project()) 