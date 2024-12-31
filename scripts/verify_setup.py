import click
import sys
from pathlib import Path
import importlib
import requests
from src.config_manager import ConfigManager

def check_dependencies():
    """Verify all required packages are installed"""
    required = [
        "requests",
        "click",
        "pytest",
        "python-dotenv",
        "tqdm",
        "tenacity",
        "watchdog",
        "gitpython"
    ]
    
    missing = []
    for package in required:
        try:
            importlib.import_module(package)
        except ImportError:
            missing.append(package)
            
    return missing

def check_api_access():
    """Verify OpenRouter API access"""
    config = ConfigManager()
    try:
        response = requests.get(
            f"{config.api_base_url}/models",
            headers=config.headers
        )
        response.raise_for_status()
        return True
    except Exception as e:
        return str(e)

def check_directory_structure():
    """Verify project structure"""
    required_dirs = ["src", "tests", "logs", "results", "debug"]
    missing = []
    
    for dir in required_dirs:
        if not Path(dir).exists():
            missing.append(dir)
            
    return missing

@click.command()
def verify():
    """Verify the setup is working correctly"""
    click.echo("Checking setup...")
    
    # Check dependencies
    missing_deps = check_dependencies()
    if missing_deps:
        click.echo(f"Missing dependencies: {', '.join(missing_deps)}")
        click.echo("Install them with: pip install " + " ".join(missing_deps))
    else:
        click.echo("✅ All dependencies installed")
    
    # Check API access
    api_status = check_api_access()
    if api_status is True:
        click.echo("✅ OpenRouter API access verified")
    else:
        click.echo(f"❌ API access failed: {api_status}")
    
    # Check directory structure
    missing_dirs = check_directory_structure()
    if missing_dirs:
        click.echo(f"Missing directories: {', '.join(missing_dirs)}")
        create = click.confirm("Create missing directories?")
        if create:
            for dir in missing_dirs:
                Path(dir).mkdir(exist_ok=True)
            click.echo("Directories created")
    else:
        click.echo("✅ Directory structure verified")

if __name__ == "__main__":
    verify() 