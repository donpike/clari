import sys
from pathlib import Path
import json
from datetime import datetime
import difflib
import ast

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.code_modifier import CodeModifier
from src.tools.code_improver import CodeAnalyzer, CodeTransformer

class SemiAutomatedImprovement:
    def __init__(self):
        self.improvements_dir = Path('improvements')
        self.improvements_dir.mkdir(exist_ok=True)
        self.code_modifier = CodeModifier()
        self.analyzer = CodeAnalyzer()
        
    def run(self, target_path: Path = Path('src')):
        """Run semi-automated improvements"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.improvements_dir / f'improvement_report_{timestamp}.json'
        
        print(f"🔍 Starting semi-automated improvement run at {timestamp}")
        
        # Debug: Print target path
        print(f"\nTarget path: {target_path}")
        print(f"Target path exists: {target_path.exists()}")
        
        # 1. Find files to analyze
        files_to_analyze = []
        if target_path.is_file() and target_path.suffix == '.py':
            files_to_analyze = [target_path]
        else:
            files_to_analyze = list(target_path.rglob('*.py'))
            
        # Debug: Print found files
        print(f"\nFound {len(files_to_analyze)} Python files:")
        for file in files_to_analyze:
            print(f"- {file}")
        
        # 2. Analyze files
        print("\nAnalyzing project files...")
        files_needing_improvement = []
        
        for file_path in files_to_analyze:
            if any(excluded in str(file_path) for excluded in ['venv', '__pycache__', '.git']):
                continue
                
            try:
                print(f"\nAnalyzing {file_path}...")
                
                # Read and parse the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    source = f.read()
                tree = ast.parse(source)
                
                # Find potential improvements
                issues = self.analyzer.analyze(tree, source)
                
                if issues:
                    files_needing_improvement.append((file_path, issues))
                    print(f"Found {len(issues)} issues:")
                    for issue in issues:
                        print(f"  - {issue['message']}")
                else:
                    print("No issues found.")
                    
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
                continue
        
        if not files_needing_improvement:
            print("No files need improvement!")
            return
        
        # 3. Show summary before proceeding
        print(f"\nFound {len(files_needing_improvement)} files that might need improvement:")
        for i, (file_path, issues) in enumerate(files_needing_improvement, 1):
            print(f"\n{i}. {file_path}:")
            for issue in issues:
                print(f"   - {issue['message']}")
        
        # 4. Ask which files to improve
        while True:
            choice = input("\nSelect files to improve (comma-separated numbers, 'all', or 'q' to quit): ").strip().lower()
            
            if choice == 'q':
                return
                
            if choice == 'all':
                selected_indices = range(len(files_needing_improvement))
                break
                
            try:
                selected_indices = [int(x.strip()) - 1 for x in choice.split(',')]
                if all(0 <= i < len(files_needing_improvement) for i in selected_indices):
                    break
                print(f"Please enter numbers between 1 and {len(files_needing_improvement)}")
            except ValueError:
                print("Invalid input. Please enter numbers separated by commas, 'all', or 'q'")
        
        # 5. Process selected files
        improvements_found = []
        
        for file_path, issues in [files_needing_improvement[i] for i in selected_indices]:
            print(f"\nProcessing {file_path}...")
            
            for issue in issues:
                print(f"\nAddressing issue: {issue['message']}")
                
                if 'original' in issue:
                    try:
                        # Read the file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()
                        
                        # Create transformer with the issue
                        transformer = CodeTransformer(issue)
                        
                        # Parse and transform
                        tree = ast.parse(source)
                        modified_tree = transformer.visit(tree)
                        
                        # Generate new source
                        new_source = ast.unparse(modified_tree)
                        
                        # Show diff
                        print("\nProposed changes:")
                        diff_lines = list(difflib.unified_diff(
                            source.splitlines(keepends=True),
                            new_source.splitlines(keepends=True),
                            fromfile='Original',
                            tofile='Improved'
                        ))
                        
                        for line in diff_lines:
                            if line.startswith('+'):
                                print(f"\033[92m{line}\033[0m", end='')
                            elif line.startswith('-'):
                                print(f"\033[91m{line}\033[0m", end='')
                            else:
                                print(line, end='')
                        
                        while True:
                            choice = input("\nApply this improvement? (y/n/s/q): ").lower()
                            if choice in ('y', 'n', 's', 'q'):
                                break
                        
                        if choice == 'q':
                            print("\n🛑 Stopping improvement process")
                            return
                        elif choice == 's':
                            print("\n⏭️ Skipping remaining improvements for this file")
                            break
                        elif choice == 'y':
                            # Backup file
                            backup_path = self.improvements_dir / f"{file_path.name}.{timestamp}.bak"
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            with open(backup_path, 'w', encoding='utf-8') as f:
                                f.write(content)
                            
                            # Apply improvement using CodeModifier
                            improvement_data = {
                                'original': source,
                                'improved': new_source
                            }
                            
                            if self.code_modifier.apply_improvement(file_path, improvement_data):
                                improvements_found.append({
                                    'file': str(file_path),
                                    'issue': issue,
                                    'improvement': {
                                        'original': source,
                                        'modified': new_source
                                    }
                                })
                                print(f"✅ Applied improvement (backup at {backup_path})")
                            else:
                                print("❌ Failed to apply improvement")
                            
                    except Exception as e:
                        print(f"Error improving {file_path}: {e}")
                        continue
        
        # 6. Save report
        report = {
            'timestamp': timestamp,
            'files_analyzed': len(files_to_analyze),
            'files_improved': len(improvements_found),
            'improvements': improvements_found
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✨ Improvement run complete! Report saved to {report_file}")

def main():
    improver = SemiAutomatedImprovement()
    
    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
    else:
        target_path = Path('src')
    
    improver.run(target_path)

if __name__ == "__main__":
    main()
