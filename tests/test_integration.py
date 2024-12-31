import pytest
from pathlib import Path
import tempfile
import shutil
from src.task_queue import TaskQueue
from src.codebase_manager import CodebaseManager
from src.config_manager import ConfigManager
import os
import asyncio

@pytest.fixture
def temp_project():
    """Create a temporary project structure for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        
        # Create sample files
        (project_dir / "src").mkdir()
        (project_dir / "tests").mkdir()
        
        # Create a sample Python file
        sample_code = """
def test_function():
    # This needs improvement
    x = 1
    y = 2
    return x + y
"""
        with open(project_dir / "src" / "sample.py", "w") as f:
            f.write(sample_code)
            
        yield project_dir

@pytest.fixture
def config():
    """Ensure config is properly set up"""
    config = ConfigManager()
    assert config.openrouter_api_key, "API key not found in environment"
    return config

@pytest.mark.asyncio
async def test_full_workflow(temp_project, config):
    """Test the entire workflow from adding tasks to processing them"""
    # Initialize components
    queue = TaskQueue()
    manager = CodebaseManager(temp_project)
    
    # Add a task
    sample_file = temp_project / "src" / "sample.py"
    task_id = queue.add_task("code_improvement", sample_file, priority=5)
    
    # Verify task was added
    assert task_id in [task.id for task in queue.tasks]
    
    # Run the queue
    results = await queue.run()
    
    # Verify results
    assert results["total"] > 0
    assert results["successful"] > 0
    
    # Check if results were saved
    results_dir = Path("results")
    assert results_dir.exists()
    result_files = list(results_dir.glob(f"{task_id}*.json"))
    assert len(result_files) > 0

@pytest.mark.asyncio
async def test_daily_session(temp_project):
    """Test daily session functionality"""
    manager = CodebaseManager(temp_project)
    
    # Schedule daily session
    await manager.schedule_daily_session(max_files=2)
    
    # Verify tasks were created
    assert len(manager.task_queue.tasks) > 0
    
    # Run the session
    results = await manager.task_queue.run()
    
    # Verify report generation
    report = manager.generate_session_report()
    assert report["timestamp"]
    assert report["files_processed"] > 0

def test_storage_persistence(temp_project):
    """Test that tasks persist in storage"""
    from src.storage import Storage
    
    storage = Storage()
    queue = TaskQueue()
    
    # Add a task
    sample_file = temp_project / "src" / "sample.py"
    task_id = queue.add_task("code_improvement", sample_file)
    
    # Get pending tasks
    pending = storage.get_pending_tasks()
    assert len(pending) > 0
    assert any(task["id"] == task_id for task in pending) 