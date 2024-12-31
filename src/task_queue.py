import asyncio
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from .openrouter_client import OpenRouterClient
from .progress_tracker import ProgressTracker

@dataclass
class Task:
    id: str
    type: str  # 'code_improvement', 'test_generation', 'dependency_check'
    input_path: Path
    status: str = 'pending'
    created_at: datetime = datetime.now()
    result: Dict = None
    priority: int = 0

class TaskQueue:
    def __init__(self):
        self.tasks: List[Task] = []
        self.client = OpenRouterClient()
        self.running = False
        self._setup_logging()
    
    def _setup_logging(self):
        logging.basicConfig(
            filename='logs/task_queue.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def add_task(self, task_type: str, input_path: Path, priority: int = 0) -> str:
        """Add a new task to the queue with priority (0-10)"""
        task_id = f"{task_type}_{len(self.tasks)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        task = Task(
            id=task_id, 
            type=task_type, 
            input_path=input_path,
            priority=priority
        )
        self.storage.save_task(task)
        self.tasks.append(task)
        logging.info(f"Added task {task_id} to queue with priority {priority}")
        return task_id
    
    async def process_task(self, task: Task):
        """Process a single task"""
        try:
            task.status = 'running'
            if task.type == 'code_improvement':
                with open(task.input_path, 'r') as f:
                    code = f.read()
                task.result = await self.client.generate_code(
                    f"Improve this code:\n```python\n{code}\n```"
                )
            elif task.type == 'test_generation':
                with open(task.input_path, 'r') as f:
                    code = f.read()
                task.result = await self.client.suggest_tests(code)
            elif task.type == 'dependency_check':
                task.result = await self.client.analyze_dependencies(task.input_path)
            
            task.status = 'completed'
            self._save_result(task)
            
        except Exception as e:
            task.status = 'failed'
            task.result = {'error': str(e)}
            logging.error(f"Task {task.id} failed: {str(e)}")
    
    def _save_result(self, task: Task):
        """Save task result to file"""
        output_dir = Path('results')
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{task.id}_result.json"
        with open(output_file, 'w') as f:
            json.dump({
                'task_id': task.id,
                'type': task.type,
                'input_path': str(task.input_path),
                'status': task.status,
                'created_at': task.created_at.isoformat(),
                'result': task.result
            }, f, indent=2)
    
    async def run(self):
        """Run the task queue"""
        self.running = True
        progress = ProgressTracker(len(self.tasks))
        
        while self.running and self.tasks:
            pending_tasks = [t for t in self.tasks if t.status == 'pending']
            if not pending_tasks:
                break
                
            # Process up to 3 tasks concurrently
            batch = pending_tasks[:3]
            await asyncio.gather(*[self.process_task(task) for task in batch])
            
            for task in batch:
                progress.update(task.input_path, task.status, 
                              "Completed" if task.status == 'completed' else "Failed")
        
        return progress.get_summary() 
    
    async def watch_directory(self, directory: Path):
        """Watch directory for changes and automatically queue tasks"""
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class CodeChangeHandler(FileSystemEventHandler):
            def __init__(self, queue):
                self.queue = queue
                
            def on_modified(self, event):
                if event.src_path.endswith('.py'):
                    self.queue.add_task('code_improvement', Path(event.src_path), priority=5)
        
        observer = Observer()
        observer.schedule(CodeChangeHandler(self), directory, recursive=True)
        observer.start() 