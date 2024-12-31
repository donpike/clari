import asyncio
import click
from pathlib import Path
from src.task_queue import TaskQueue
import json
import sys
from src.codebase_manager import CodebaseManager
from datetime import datetime

@click.group()
def cli():
    """Task Queue CLI for code improvements"""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--task-type', '-t', 
              type=click.Choice(['code_improvement', 'test_generation', 'dependency_check']),
              required=True)
def add(file_path, task_type):
    """Add a new task to the queue"""
    queue = TaskQueue()
    task_id = queue.add_task(task_type, Path(file_path))
    click.echo(f"Added task {task_id} to queue")

@cli.command()
def run():
    """Run all queued tasks"""
    async def run_queue():
        queue = TaskQueue()
        results = await queue.run()
        click.echo(json.dumps(results, indent=2))
    
    asyncio.run(run_queue())

@cli.command()
def status():
    """Show status of all tasks"""
    results_dir = Path('results')
    if not results_dir.exists():
        click.echo("No tasks have been processed yet")
        return
        
    results = []
    for result_file in results_dir.glob('*_result.json'):
        with open(result_file) as f:
            results.append(json.load(f))
    
    click.echo(json.dumps(results, indent=2))

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def watch(directory):
    """Watch a directory for changes and automatically improve code"""
    async def watch_dir():
        queue = TaskQueue()
        await queue.watch_directory(Path(directory))
        # Keep running
        while True:
            await asyncio.sleep(1)
    
    click.echo(f"Watching directory: {directory}")
    asyncio.run(watch_dir())

@cli.command()
@click.argument('file_paths', type=click.Path(exists=True), nargs=-1)
@click.option('--priority', '-p', type=int, default=0, help='Task priority (0-10)')
def batch(file_paths, priority):
    """Add multiple files to the queue"""
    queue = TaskQueue()
    for path in file_paths:
        task_id = queue.add_task('code_improvement', Path(path), priority)
        click.echo(f"Added {path} with task ID: {task_id}")

@cli.command()
def process():
    """Process pending tasks in background"""
    import subprocess
    
    pythonw = sys.executable.replace('python.exe', 'pythonw.exe')
    subprocess.Popen([pythonw, __file__, 'run'])
    click.echo("Processing tasks in background")

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--max-files', '-m', default=5, help='Maximum files to process per session')
def daily_session(project_path, max_files):
    """Run a daily improvement session on the codebase"""
    async def run_session():
        manager = CodebaseManager(Path(project_path))
        await manager.schedule_daily_session(max_files)
        
        # Process tasks
        queue = TaskQueue()
        results = await queue.run()
        
        # Generate report
        report = manager.generate_session_report()
        
        # Save report
        report_path = Path('reports') / f"session_{datetime.now().strftime('%Y%m%d')}.json"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        click.echo(f"Session complete! Report saved to {report_path}")
    
    asyncio.run(run_session())

if __name__ == '__main__':
    cli() 