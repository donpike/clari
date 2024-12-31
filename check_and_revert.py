import os
from pathlib import Path
import ast
import re

def check_file_formatting(file_path: Path) -> bool:
    """Check if a file has formatting issues."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check for common formatting issues
        issues = []
        
        # Check for excessive spaces
        if re.search(r'\s{4,}', content):
            issues.append("Excessive spacing")
            
        # Check for malformed docstrings
        if '"\\"' in content or '\\"' in content:
            issues.append("Malformed docstrings")
            
        # Check for incorrect indentation
        if re.search(r'^\s*(?!    )\s+\w', content, re.MULTILINE):
            issues.append("Incorrect indentation")
            
        # Try parsing with ast to check for syntax
        try:
            ast.parse(content)
        except SyntaxError:
            issues.append("Syntax error")
            
        if issues:
            print(f"Issues in {file_path}:")
            for issue in issues:
                print(f"  - {issue}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error checking {file_path}: {e}")
        return False

def revert_file(file_path: Path):
    """Revert a file from its backup."""
    backup_path = file_path.with_suffix('.py.bak')
    if backup_path.exists():
        print(f"Reverting {file_path} from backup")
        with open(backup_path, 'r') as f:
            content = f.read()
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    src_dir = Path('src')
    files_to_revert = []
    
    # Check all Python files
    for file_path in src_dir.rglob('*.py'):
        print(f"\nChecking {file_path}...")
        if not check_file_formatting(file_path):
            files_to_revert.append(file_path)
    
    if files_to_revert:
        print("\nFiles with issues:")
        for file in files_to_revert:
            print(f"  - {file}")
            
        response = input("\nRevert these files to their backups? (y/n): ")
        if response.lower() == 'y':
            for file in files_to_revert:
                if revert_file(file):
                    print(f"Reverted {file}")
                else:
                    print(f"No backup found for {file}")
    else:
        print("\nAll files look good!")

if __name__ == "__main__":
    main() 