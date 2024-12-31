import winreg
import os
import sys

def add_context_menu():
    python_path = sys.executable
    script_path = os.path.abspath("scripts/run_tasks.py")
    
    # Add for Python files
    key_path = r"Python.File\shell\improveCode"
    
    try:
        key = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, "Improve with AI")
        
        command_key = winreg.CreateKey(key, "command")
        command = f'"{python_path}" "{script_path}" add "%1" -t code_improvement'
        winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        
        print("Context menu added successfully!")
        
    except Exception as e:
        print(f"Error adding context menu: {e}")

if __name__ == "__main__":
    add_context_menu() 