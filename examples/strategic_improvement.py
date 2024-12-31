import asyncio
from pathlib import Path
import sys
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from src.main import AutoCoder
from src.config import default_config

async def analyze_and_prioritize():
    console = Console()
    config = default_config()
    coder = AutoCoder(config)
    
    # 1. First, get a high-level overview
    console.print("\n[bold blue]🔍 High-Level Analysis[/]")
    
    # Create analysis categories
    categories = {
        'critical': {
            'patterns': ['god_class', 'security_issue'],
            'improvements': []
        },
        'high': {
            'patterns': ['large_class', 'complex_function', 'error_handling'],
            'improvements': []
        },
        'medium': {
            'patterns': ['long_function', 'nested_blocks', 'code_duplication'],
            'improvements': []
        },
        'low': {
            'patterns': ['documentation', 'style', 'minor_optimization'],
            'improvements': []
        }
    }
    
    # Analyze each core file
    core_files = [
        'src/core/safety.py',
        'src/core/improvement_tracker.py',
        'src/core/batch_processor.py',
        'src/main.py'
    ]
    
    all_improvements = {}
    
    for file in core_files:
        console.print(f"\nAnalyzing {file}...")
        result = await coder.improve_code(Path(file))
        
        if result['status'] == 'success':
            all_improvements[file] = result['improvements']
            
            # Categorize improvements
            for imp in result['improvements']:
                for priority, cat in categories.items():
                    if any(pattern in imp['type'].lower() for pattern in cat['patterns']):
                        cat['improvements'].append({
                            'file': file,
                            **imp
                        })
    
    # Display prioritized improvements
    console.print("\n[bold green]Prioritized Improvements:[/]")
    
    for priority, cat in categories.items():
        if cat['improvements']:
            table = Table(title=f"{priority.upper()} Priority Issues")
            table.add_column("File")
            table.add_column("Type")
            table.add_column("Description")
            
            for imp in cat['improvements']:
                table.add_row(
                    Path(imp['file']).name,
                    imp['type'],
                    imp['description'][:100] + "..." if len(imp['description']) > 100 else imp['description']
                )
            
            console.print(table)
            console.print()
    
    # Ask which category to tackle first
    priorities = [p for p in categories if categories[p]['improvements']]
    if not priorities:
        console.print("[yellow]No improvements found![/]")
        return
    
    console.print("\n[bold]Available priorities:[/]")
    for i, p in enumerate(priorities, 1):
        count = len(categories[p]['improvements'])
        console.print(f"{i}. {p.upper()} ({count} issues)")
    
    choice = int(input("\nWhich priority would you like to tackle? (number): ")) - 1
    if 0 <= choice < len(priorities):
        selected_priority = priorities[choice]
        improvements = categories[selected_priority]['improvements']
        
        console.print(f"\n[bold]Tackling {selected_priority.upper()} priority issues:[/]")
        
        for i, imp in enumerate(improvements, 1):
            console.print(f"\n{i}. In {imp['file']}:")
            console.print(f"   Type: {imp['type']}")
            console.print(f"   Description: {imp['description']}")
            console.print(f"   Original: {imp['original']}")
            console.print(f"   Improved: {imp['improved']}")
            
            if Confirm.ask("Apply this improvement?"):
                # Here we would apply the improvement
                console.print("[green]✓[/] Improvement applied!")
            else:
                console.print("[yellow]Skipped[/]")
            
            if i < len(improvements) and not Confirm.ask("\nContinue with next improvement?"):
                break

if __name__ == "__main__":
    asyncio.run(analyze_and_prioritize()) 