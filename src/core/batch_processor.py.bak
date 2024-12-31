from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from ..utils.logger import logger
from ..core.safety import SafetyChecker

class BatchProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.safety_checker = SafetyChecker(config)
        
    async def process_directory(self, 
                              directory: Path,
                              processor_func,
                              max_workers: int = 4) -> Dict[Path, Any]:
        """Process multiple files in parallel"""
        results = {}
        files = list(directory.rglob('*.py'))
        
        # First, run safety checks
        unsafe_files = []
        for file in files:
            safety_result = await self.safety_checker.pre_check(file)
            if not safety_result['is_safe']:
                unsafe_files.append(file)
                logger.warning(f"Skipping unsafe file: {file}")
        
        # Remove unsafe files
        safe_files = [f for f in files if f not in unsafe_files]
        
        # Process safe files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(processor_func, file): file 
                for file in safe_files
            }
            
            for future in futures:
                file = futures[future]
                try:
                    results[file] = await future
                except Exception as e:
                    logger.error(f"Error processing {file}: {e}")
                    results[file] = {
                        'status': 'error',
                        'error': str(e)
                    }
        
        return results 