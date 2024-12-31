from pathlib import Path

def restore_all_backups(directory: str = "src"):
    """Restore all .py files from their .py.bak backups."""
    src_dir = Path(directory)
    backup_files = list(src_dir.rglob("*.py.bak"))
    
    print(f"Found {len(backup_files)} backup files")
    
    for backup in backup_files:
        original = backup.with_suffix('')  # Remove .bak to get original .py path
        try:
            print(f"Restoring {original.name}...")
            with open(backup, 'r') as f:
                content = f.read()
            with open(original, 'w') as f:
                f.write(content)
            print(f"✓ Restored {original.name}")
        except Exception as e:
            print(f"✗ Error restoring {original.name}: {e}")
    
    response = input("\nDelete backup files? (y/n): ")
    if response.lower() == 'y':
        for backup in backup_files:
            try:
                backup.unlink()
                print(f"Deleted {backup.name}")
            except Exception as e:
                print(f"Error deleting {backup.name}: {e}")

if __name__ == "__main__":
    restore_all_backups() 