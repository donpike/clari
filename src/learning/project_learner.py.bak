from pathlib import Path
from typing import Dict, Any, List, Set
import json
from datetime import datetime

class ProjectLearner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_path = Path(config['learning']['db_path'])
        self.knowledge_base = self._load_knowledge_base()
        
    def get_project_patterns(self, file_path: Path) -> Dict[str, Any]:
        """Get learned patterns specific to this project"""
        context = self._get_file_context(file_path)
        return {
            'common_patterns': self._get_common_patterns(context),
            'style_guide': self._get_project_style_guide(),
            'naming_conventions': self._get_naming_conventions(),
            'success_patterns': self._get_successful_patterns(context)
        }
    
    def update_project_knowledge(self, file_path: Path, result: Dict[str, Any]):
        """Learn from code analysis results"""
        context = self._get_file_context(file_path)
        
        # Update pattern statistics
        self._update_pattern_stats(context, result)
        
        # Learn naming conventions
        if result['status'] == 'success':
            self._learn_naming_conventions(result)
            
        # Learn successful improvements
        if result.get('feedback') == 'helpful':
            self._record_successful_pattern(
                result['pattern_type'],
                context
            )
    
    def _get_file_context(self, file_path: Path) -> Dict[str, Any]:
        """Understand the context of a file"""
        return {
            'framework': self._detect_framework(file_path),
            'module_type': self._detect_module_type(file_path),
            'dependencies': self._get_dependencies(file_path),
            'project_type': self._detect_project_type(file_path)
        }
    
    def _detect_framework(self, file_path: Path) -> str:
        """Detect which framework the file is using"""
        content = file_path.read_text()
        frameworks = {
            'django': ['django', 'models.Model', 'views.View'],
            'flask': ['flask', 'Flask', 'Blueprint'],
            'fastapi': ['fastapi', 'FastAPI', 'APIRouter'],
            'pytest': ['pytest', '@pytest.fixture'],
            'sqlalchemy': ['sqlalchemy', 'Base.metadata'],
        }
        
        for framework, patterns in frameworks.items():
            if any(pattern in content for pattern in patterns):
                return framework
        return 'standard'
    
    def _detect_module_type(self, file_path: Path) -> str:
        """Detect the type of module"""
        filename = file_path.name
        if filename.startswith('test_'):
            return 'test'
        if 'models' in str(file_path):
            return 'model'
        if 'views' in str(file_path):
            return 'view'
        if 'utils' in str(file_path):
            return 'utility'
        return 'general'
    
    def _get_common_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get patterns common to this context"""
        framework = context['framework']
        module_type = context['module_type']
        
        return self.knowledge_base.get('patterns', {}).get(framework, {}).get(module_type, [])
    
    def _update_pattern_stats(self, context: Dict[str, Any], result: Dict[str, Any]):
        """Update statistics about pattern effectiveness"""
        if 'pattern_type' in result:
            stats = self.knowledge_base.setdefault('stats', {})
            pattern = result['pattern_type']
            
            if pattern not in stats:
                stats[pattern] = {'uses': 0, 'successes': 0}
            
            stats[pattern]['uses'] += 1
            if result.get('feedback') == 'helpful':
                stats[pattern]['successes'] += 1
    
    def _learn_naming_conventions(self, result: Dict[str, Any]):
        """Learn naming conventions from successful improvements"""
        conventions = self.knowledge_base.setdefault('naming_conventions', {})
        
        if 'improved_code' in result:
            # Analyze naming patterns in improved code
            patterns = self._extract_naming_patterns(result['improved_code'])
            
            for pattern_type, names in patterns.items():
                if pattern_type not in conventions:
                    conventions[pattern_type] = {'count': 0, 'examples': set()}
                
                conventions[pattern_type]['count'] += 1
                conventions[pattern_type]['examples'].update(names)
    
    def _save_knowledge_base(self):
        """Save learned knowledge to disk"""
        with open(self.db_path, 'w') as f:
            json.dump(self.knowledge_base, f) 