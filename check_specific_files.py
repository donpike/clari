from pathlib import Path
from check_and_revert import check_file_formatting, revert_file

files_to_check = [
    Path('src/auto_coder.py'),
    Path('src/codebase_manager.py')
]

def main():
    files_to_revert = []
    
    for file_path in files_to_check:
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
        print("\nBoth files look good!")

if __name__ == "__main__":
    main() 