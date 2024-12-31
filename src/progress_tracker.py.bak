from tqdm import tqdm
import logging
from pathlib import Path

class ProgressTracker:
    def __init__(self, total_files: int):
        self.progress_bar = tqdm(total=total_files)
        self.results = {}
        
    def update(self, file_path: Path, status: str, message: str):
        self.results[str(file_path)] = {"status": status, "message": message}
        self.progress_bar.update(1)
        logging.info(f"Processed {file_path}: {status}")
        
    def get_summary(self) -> dict:
        return {
            "total": len(self.results),
            "successful": sum(1 for r in self.results.values() if r["status"] == "success"),
            "failed": sum(1 for r in self.results.values() if r["status"] == "error"),
            "results": self.results
        } 