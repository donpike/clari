from pathlib import Path
from typing import List, Dict, Any
import git
from datetime import datetime
import json
import logging
from .task_queue import TaskQueue

class CodebaseManager:
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.task_queue = TaskQueue()
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            filename='logs/codebase.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def analyze_codebase(self) -> Dict:
        """Analyze entire codebase and create improvement tasks"""
        python_files = list(self.root_path.glob('**/*.py'))
        
        # Group files by directory for better organization
        file_groups = {}
        for file in python_files:
            relative_path = file.relative_to(self.root_path)
            group = str(relative_path.parent)
            if group not in file_groups:
                file_groups[group] = []
            file_groups[group].append(file)
            
        return file_groups
    
    async def schedule_daily_session(self, max_files: int = 5):
        """Schedule a daily improvement session with limited files"""
        file_groups = self.analyze_codebase()
        
        # Get modified files first
        if self._is_git_repo():
            repo = git.Repo(self.root_path)
            modified_files = [
                Path(item.a_path) 
                for item in repo.index.diff(None) 
                if item.a_path.endswith('.py')
            ]
            
            # Add modified files with high priority
            for file in modified_files[:max_files]:
                self.task_queue.add_task('code_improvement', file, priority=10)
                max_files -= 1
                
        # Add some files from each directory for balanced coverage
        if max_files > 0:
            for group, files in file_groups.items():
                if not files:
                    continue
                # Take one file from each group
                self.task_queue.add_task('code_improvement', files[0], priority=5)
                max_files -= 1
                if max_files <= 0:
                    break
    
    def _is_git_repo(self) -> bool:
        try:
            git.Repo(self.root_path)
            return True
        except git.exc.InvalidGitRepositoryError:
            return False
    
    def generate_session_report(self) -> Dict:
        """Generate a report of the improvement session"""
        return {
            'timestamp': datetime.now().isoformat(),
            'files_processed': len(self.task_queue.tasks),
            'improvements': self.task_queue.get_summary()
        } 