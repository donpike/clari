from pathlib import Path
from typing import Dict, Any, List
from ..database.db_init import init_db, Improvement
from ..utils.logger import logger

class ImprovementTracker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = config['database']['path']
        self.session = init_db(self.db_path)
        
    def record_improvements(self, file_path: Path, improvements: List[Dict[str, Any]]):
        """Record improvements to the database"""
        try:
            for imp in improvements:
                improvement = Improvement(
                    file_path=str(file_path),
                    improvement_type=imp.get('type', 'unknown'),
                    original_code=imp.get('original', ''),
                    improved_code=imp.get('improved', ''),
                    description=imp.get('description', ''),
                    extra_data=imp.get('metadata', {}),
                    status='pending'
                )
                self.session.add(improvement)
            
            self.session.commit()
            logger.info(f"Recorded {len(improvements)} improvements for {file_path}")
            
        except Exception as e:
            logger.error(f"Error recording improvements: {str(e)}")
            self.session.rollback()
            
    def get_improvements(self, file_path: Path = None) -> List[Dict[str, Any]]:
        """Get recorded improvements"""
        query = self.session.query(Improvement)
        if file_path:
            query = query.filter(Improvement.file_path == str(file_path))
        return [
            {
                'id': imp.id,
                'file_path': imp.file_path,
                'type': imp.improvement_type,
                'original': imp.original_code,
                'improved': imp.improved_code,
                'description': imp.description,
                'timestamp': imp.timestamp,
                'status': imp.status
            }
            for imp in query.all()
        ] 