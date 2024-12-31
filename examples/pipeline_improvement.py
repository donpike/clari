import asyncio
from pathlib import Path
import sys
from rich.console import Console
from datetime import datetime
import json
import argparse
from typing import Dict, Any, List, Optional
import ast

sys.path.append(str(Path(__file__).parent.parent))

from src.main import AutoCoder
from src.config import default_config
from src.utils.logger import logger

class ImprovementPipeline:
    def __init__(self):
        self.console = Console()
        self.config = default_config()
        self.coder = AutoCoder(self.config)
        self.session_file = Path('improvement_sessions.json')
        
    def load_sessions(self) -> List[Dict[str, Any]]:
        """Load previous improvement sessions"""
        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding session file: {e}")
            return []
        
    def save_session(self, session: Dict[str, Any]):
        """Save improvement session"""
        sessions = self.load_sessions()
        sessions.append(session)
        with open(self.session_file, 'w') as f:
            json.dump(sessions, f, indent=2)
            
    async def process_task(self, task_path, task_type='improve', priority='medium', context=None):
        session = {
            'timestamp': datetime.now().isoformat(),
            'task_path': str(task_path),
            'task_type': task_type,
            'priority': priority,
            'context': context or {},
            'improvements': [],
            'status': 'pending'
        }

        try:
            # 1. Analyze the code
            result = await self.coder.improve_code(task_path)

            if result['status'] != 'success':
                session['status'] = 'error'
                session['error'] = result['issues']
                return session

            # 2. Filter improvements based on priority and type
            improvements = self._filter_improvements(
                result['improvements'],
                priority=priority,
                task_type=task_type
            )
            
            session['improvements'] = improvements
            session['status'] = 'success'
            return session
            
        except Exception as e:
            session['status'] = 'error'
            session['error'] = str(e)
            return session
            
    def _filter_improvements(self, 
                           improvements: List[Dict],
                           priority: str,
                           task_type: str) -> List[Dict]:
        """Filter improvements based on priority and type"""
        priority_levels = {
            'critical': ['god_class', 'security_issue'],
            'high': ['large_class', 'complex_function', 'error_handling'],
            'medium': ['long_function', 'nested_blocks'],
            'low': ['documentation', 'style']
        }
        
        allowed_types = priority_levels.get(priority, [])
        
        return [
            imp for imp in improvements
            if (imp['type'] in allowed_types and
                (task_type == 'improvement' or imp['type'] == task_type))
        ]
        
    def _should_apply_improvement(self, 
                                improvement: Dict,
                                priority: str) -> bool:
        """Determine if an improvement should be auto-applied"""
        auto_apply_types = {
            'critical': ['security_issue'],
            'high': ['error_handling'],
            'medium': [],
            'low': ['documentation', 'style']
        }
        
        return improvement['type'] in auto_apply_types.get(priority, [])
        
    async def _apply_improvement(self,
                               file_path: Path,
                               improvement: Dict) -> bool:
        """Apply an improvement to the code"""
        try:
            # Read the current file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create backup
            backup_path = file_path.with_suffix('.bak')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Apply the improvement
            if improvement['type'] == 'god_class':
                # Handle class splitting specially
                new_content = self._split_class(content, improvement)
            else:
                # Simple replacement for other improvements
                new_content = content.replace(
                    improvement['original'].strip(),
                    improvement['improved'].strip()
                )
            
            # Write the improved content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Applied improvement to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying improvement: {e}")
            return False
            
    def _split_class(self, content: str, improvement: Dict) -> str:
        """Handle splitting a class into multiple classes"""
        # Parse the original content
        tree = ast.parse(content)
        
        # Find the class to split
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.name == 'SafetyChecker':  # or other class name from improvement
                    # Create new content with split classes
                    return improvement['improved']
        
        return content

    def save_sessions(self, sessions: List[Dict[str, Any]]) -> None:
        try:
            with open(self.session_file, "w") as f:
                json.dump(sessions, f, indent=4)
        except IOError as e:
            self.logger.error(f"Error saving session file: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error while saving sessions: {e}")

async def main():
    # Remove argument parsing and use default values
    pipeline = ImprovementPipeline()
    
    # Use a default path - you can modify this to your target file/directory
    default_path = Path('examples/pipeline_improvement.py')  # or whatever file you want to analyze
    
    result = await pipeline.process_task(
        task_path=default_path,
        task_type='improvement',
        priority='high',
        context={}
    )
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(main()) 