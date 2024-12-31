import asyncio
import json
from pathlib import Path
from src.openrouter_client import OpenRouterClient
import subprocess
import sys

async def check_dependencies():
    client = OpenRouterClient()
    
    # Get current dependencies
    requirements_path = Path("requirements.txt")
    
    # Analyze dependencies
    analysis = await client.analyze_dependencies(requirements_path)
    
    # Fix: Capture the output properly
    outdated = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
        capture_output=True, 
        text=True
    )
    
    # Generate report
    report = {
        "ai_analysis": analysis,
        "outdated_packages": json.loads(outdated.stdout) if outdated.stdout else []
    }
    
    # Save report
    with open("dependency_report.json", "w") as f:
        json.dump(report, f, indent=2)
        
    return report

if __name__ == "__main__":
    asyncio.run(check_dependencies()) 