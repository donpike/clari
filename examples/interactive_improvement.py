import asyncio
import sys
from pathlib import Path
import difflib
from enum import Enum
from typing import List, Dict, Any, Optional

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Now we can import from src
from src.auto_coder import AutoCoder
from src.config import default_config
from src.core.safety import SafetyChecker

class ImprovementTier(Enum):
    """Defines different tiers of code improvements."""
    BASIC = 1  # Only automatic fixes (no AI)
    INTERMEDIATE = 2  # Automatic fixes + simple AI improvements
    ADVANCED = 3  # All possible improvements including complex AI suggestions

async def interactive_improve(directory: str = "src", tier: ImprovementTier = ImprovementTier.INTERMEDIATE):
    """Interactively improve Python files in a directory.
    
    Args:
        directory: Directory containing Python files to improve
        tier: Level of improvements to apply (basic, intermediate, or advanced)
    """
    print("🔍 Clari Interactive Improvement")
    print("This will help improve the Clari project itself")
    print(f"Using improvement tier: {tier.name}\n")
    
    auto_coder = AutoCoder(config=default_config)
    
    # First just analyze without modifying
    files = list(Path(directory).rglob("*.py"))
    files_needing_improvement = []
    
    print("Analyzing files...")
    for file in files:
        result = await auto_coder.analyze_code(file)  # Only analyze
        if result['status'] == 'success':
            automatic_fixes = result.get('automatic_fixes', 0)
            if automatic_fixes > 0:
                files_needing_improvement.append((file, result))
                print(f"\n  {file}: {automatic_fixes} potential improvements")
                if 'issues' in result:
                    for issue in result['issues']:
                        print(f"    - Line {issue['line']}: {issue['message']}")
            else:
                print(f"  {file}: No improvements needed")
    
    if not files_needing_improvement:
        print("\nNo files need improvements!")
        return
    
    # Show files that need improvement
    print("\nFiles needing improvement:")
    for i, (file, result) in enumerate(files_needing_improvement, 1):
        print(f"{i}. {file} ({result.get('automatic_fixes', 0)} potential improvements)")
    
    # Offer bulk processing options
    print("\nImprovement options:")
    print("1. Process all files")
    print("2. Select specific files")
    print("3. Process files by directory")
    
    while True:
        choice = input("\nSelect option (1-3): ")
        
        selected_files = []
        if choice == '1':
            selected_files = [f[0] for f in files_needing_improvement]
            break
        elif choice == '2':
            print("\nEnter file numbers (comma-separated), or:")
            print("- 'done' to finish selection")
            print("- 'show N' to see details for file N")
            print("- 'exit' to quit")
            
            while True:
                choice = input("\nEnter choice: ").strip().lower()
                
                if choice == 'exit':
                    return
                    
                if choice == 'done':
                    if selected_files:
                        break
                    else:
                        print("No files selected yet")
                        continue
                
                if choice.startswith('show '):
                    try:
                        file_num = int(choice.split()[1])
                        if 1 <= file_num <= len(files_needing_improvement):
                            file_info = files_needing_improvement[file_num - 1]
                            print(f"\nImprovements for {file_info[0]}:")
                            result = file_info[1]
                            if 'issues' in result:
                                for issue in result['issues']:
                                    print(f"- Line {issue['line']}: {issue['message']}")
                            else:
                                print("No detailed issues available")
                        else:
                            print(f"Invalid file number: {file_num}")
                    except (ValueError, IndexError):
                        print("Invalid show command")
                    continue
                
                try:
                    for num in choice.split(','):
                        file_num = int(num.strip())
                        if 1 <= file_num <= len(files_needing_improvement):
                            file_path = files_needing_improvement[file_num - 1][0]
                            if file_path not in selected_files:
                                selected_files.append(file_path)
                                print(f"Added: {file_path}")
                        else:
                            print(f"Invalid number: {file_num}")
                except ValueError:
                    print("Please enter valid numbers, 'show N', 'done', or 'exit'")
            
            if selected_files:
                print("\nSelected files:")
                for file in selected_files:
                    print(f"- {file}")
                confirm = input("\nProceed with these files? (y/n): ")
                if confirm.lower() == 'y':
                    break
                else:
                    selected_files = []
                    print("Selection cleared. Please try again.")
        elif choice == '3':
            dirs = {str(f[0].parent) for f in files_needing_improvement}
            print("\nAvailable directories:")
            for i, d in enumerate(dirs, 1):
                print(f"{i}. {d}")
            try:
                dir_num = int(input("\nSelect directory number: "))
                if 1 <= dir_num <= len(dirs):
                    selected_dir = list(dirs)[dir_num - 1]
                    selected_files = [f[0] for f in files_needing_improvement 
                                   if str(f[0].parent) == selected_dir]
                    break
            except ValueError:
                print("Please enter a valid number")
        
        if not selected_files:
            print("No files selected. Please try again.")
    
    # Process selected files
    for file_path in selected_files:
        print(f"\nProcessing {file_path}...")
        
        try:
            # First get proposed changes without modifying
            result = await auto_coder.improve_code(
                file_path,
                apply_changes=False,  # Important: don't modify yet
                improvement_level=tier.value
            )
            
            if result['status'] == 'success':
                # Show proposed changes
                print("\nProposed changes:")
                # ... show diff ...
                
                response = input("\nApply these changes? (y/n): ")
                if response.lower() == 'y':
                    # Create backup first
                    backup_path = file_path.with_suffix('.py.bak')
                    with open(file_path, 'r') as f:
                        original_content = f.read()
                    with open(backup_path, 'w') as f:
                        f.write(original_content)
                        
                    # Now apply changes
                    result = await auto_coder.improve_code(
                        file_path,
                        apply_changes=True,
                        improvement_level=tier.value
                    )
            else:
                print(f"Error: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            continue

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Interactively improve Python code')
    parser.add_argument('--dir', default='src', help='Directory to analyze')
    parser.add_argument('--tier', choices=['basic', 'intermediate', 'advanced'],
                      default='intermediate', help='Improvement tier to use')
    
    args = parser.parse_args()
    tier_map = {
        'basic': ImprovementTier.BASIC,
        'intermediate': ImprovementTier.INTERMEDIATE,
        'advanced': ImprovementTier.ADVANCED
    }
    
    asyncio.run(interactive_improve(args.dir, tier_map[args.tier]))
