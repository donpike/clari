import asyncio
from pathlib import Path
from src.auto_coder import AutoCoder
from src.openrouter_client import OpenRouterClient
import logging
from typing import List, Dict, Any
import json

class WorkflowManager:
    def __init__(self):
        self.auto_coder = AutoCoder()
        self.client = OpenRouterClient()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='logs/workflow.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    async def process_directory(self, directory: Path) -> Dict[str, Any]:
        """Process all Python files in a directory"""
        results = {}
        
        # Find all Python files
        python_files = list(directory.glob('**/*.py'))
        
        # Analyze and improve each file
        for file_path in python_files:
            try:
                # Analyze code
                result = await self.auto_coder.improve_code(file_path)
                
                # Generate tests if needed
                if result["status"] == "success" and result.get("improvements"):
                    tests = await self.client.suggest_tests(file_path.read_text())
                    result["suggested_tests"] = tests
                    
                results[str(file_path)] = result
                
            except Exception as e:
                logging.error(f"Error processing {file_path}: {str(e)}")
                results[str(file_path)] = {"status": "error", "message": str(e)}
                
        return results

async def main():
    manager = WorkflowManager()
    results = await manager.process_directory(Path("src"))
    
    # Save results
    with open("improvement_report.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main()) 