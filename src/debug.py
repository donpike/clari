import logging
from pathlib import Path
import json
from typing import Dict, Any
from datetime import datetime


class DebugManager:
    """Debug manager for handling debug operations and logging."""

    def __init__(self) -> None:
        """Initialize the debug manager."""
        self.debug_dir = Path("debug")
        self.debug_dir.mkdir(exist_ok=True)
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            filename='debug/debug.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def log_api_request(self, endpoint: str, payload: Dict[str, Any]) -> None:
        """Log API requests for debugging.
        
        Args:
            endpoint: The API endpoint being called
            payload: The request payload
        """
        log_file = self.debug_dir / "api_requests.json"
        existing = []
        if log_file.exists():
            with open(log_file) as f:
                existing = json.load(f)

        existing.append({
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "payload": payload
        })

        with open(log_file, "w") as f:
            json.dump(existing, f, indent=2)

    def analyze_task_performance(self) -> Dict[str, Any]:
        """Analyze task processing performance.
        
        Returns:
            Dict containing performance metrics including total tasks,
            successful tasks, failed tasks, and average processing time.
        """
        results_dir = Path("results")
        if not results_dir.exists():
            return {"error": "No results found"}

        performance = {
            "total_tasks": 0,
            "successful": 0,
            "failed": 0,
            "average_time": 0
        }

        times = []
        for result_file in results_dir.glob("*.json"):
            with open(result_file) as f:
                data = json.load(f)
                performance["total_tasks"] += 1
                if data["status"] == "completed":
                    performance["successful"] += 1
                else:
                    performance["failed"] += 1

        return performance
