from pathlib import Path
from check_and_revert import check_file_formatting, revert_file

def check_all_python_files():
    src_dir = Path('src')
    all_files = list(src_dir.rglob('*.py'))
    
    print(f"Found {len(all_files)} Python files")
    
    # First, just check and report
    files_with_issues = []
    for file_path in all_files:
        print(f"\nChecking {file_path}...")
        if not check_file_formatting(file_path):
            files_with_issues.append(file_path)
    
    # Report findings
    if files_with_issues:
        print("\n=== Files with formatting issues ===")
        for file in files_with_issues:
            print(f"  - {file}")
            
        # Show backup status
        print("\n=== Backup status ===")
        for file in files_with_issues:
            backup = file.with_suffix('.py.bak')
            if backup.exists():
                print(f"  ✓ {file} has backup")
            else:
                print(f"  ✗ {file} no backup found")
        
        response = input("\nRevert files with issues to their backups? (y/n): ")
        if response.lower() == 'y':
            for file in files_with_issues:
                if revert_file(file):
                    print(f"Reverted {file}")
                else:
                    print(f"Could not revert {file} - no backup")
    else:
        print("\nAll files look good!")

if __name__ == "__main__":
    check_all_python_files() 