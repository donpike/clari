import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import warnings
from src.auto_coder import AutoCoder
from src.core.code_modifier import CodeModifier
from src.config.improvement_settings import ImprovementConfig

# Suppress ResourceWarning for unclosed files
warnings.filterwarnings("ignore", category=ResourceWarning)

@pytest.fixture
def sample_files(tmp_path):
    """Create sample files for testing different scenarios"""
    # File missing docstrings
    missing_docstring = tmp_path / "missing_docstring.py"
    missing_docstring.write_text("""
def add(a: int, b: int) -> int:
    return a + b

class Calculator:
    def multiply(self, x: int, y: int) -> int:
        return x * y
""")

    # File with type hint issues
    type_hints = tmp_path / "type_hints.py"
    type_hints.write_text("""
def process_data(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
""")

    return {
        'missing_docstring': missing_docstring,
        'type_hints': type_hints
    }

@pytest.mark.asyncio
async def test_docstring_improvement(sample_files):
    """Test automatic docstring addition"""
    auto_coder = AutoCoder()
    file_path = sample_files['missing_docstring']
    
    result = await auto_coder.improve_code(file_path)
    
    assert result['status'] == 'success'
    assert result['automatic_fixes'] > 0
    
    # Check if docstrings were added
    with open(file_path, 'r') as f:
        improved_code = f.read()
        assert '"""Add two integers."""' in improved_code
        assert '"""Calculator class for basic operations."""' in improved_code

@pytest.mark.asyncio
async def test_type_hint_improvement(sample_files):
    """Test automatic type hint addition"""
    auto_coder = AutoCoder()
    file_path = sample_files['type_hints']
    
    result = await auto_coder.improve_code(file_path)
    
    assert result['status'] == 'success'
    assert result['automatic_fixes'] > 0
    
    # Check if type hints were added
    with open(file_path, 'r') as f:
        improved_code = f.read()
        assert 'def process_data(data: list) -> list:' in improved_code

def test_backup_creation(sample_files):
    """Test backup file creation"""
    modifier = CodeModifier()
    file_path = sample_files['missing_docstring']
    
    original_content = file_path.read_text()
    result = modifier.modify_file(file_path, [{'type': 'missing_docstring'}])
    
    backup_file = file_path.with_suffix('.py.bak')
    assert backup_file.exists()
    assert backup_file.read_text() == original_content

@pytest.mark.asyncio
async def test_cost_threshold_respect(sample_files):
    """Test that cost thresholds are respected"""
    config = ImprovementConfig(
        automatic_fixes=['missing_docstring'],
        ai_improvements=['logic_improvement'],
        cost_threshold=0.001,  # Very low threshold
        max_tokens=1000,
        backup_files=True
    )
    
    auto_coder = AutoCoder()
    auto_coder.config = config
    
    file_path = sample_files['missing_docstring']
    result = await auto_coder.improve_code(file_path)
    
    # Should only have automatic fixes, no AI improvements
    assert result['status'] == 'success'
    assert result.get('complex_issues', 0) == 0

@pytest.mark.asyncio
async def test_combined_improvements(sample_files):
    """Test both automatic and AI improvements"""
    with patch('src.auto_coder.OpenRouterClient') as mock_client:
        mock_client.return_value.generate_code.return_value = {
            "improvements": ["Improved variable names", "Added error handling"]
        }
        mock_client.return_value.estimate_cost.return_value = 0.001
        
        auto_coder = AutoCoder()
        file_path = sample_files['missing_docstring']
        
        result = await auto_coder.improve_code(file_path)
        
        assert result['status'] == 'success'
        assert result['automatic_fixes'] > 0
        assert result.get('complex_issues', 0) > 0

def test_invalid_file_handling():
    """Test handling of invalid files"""
    modifier = CodeModifier()
    result = modifier.modify_file(Path('nonexistent.py'), [{'type': 'missing_docstring'}])
    assert result['status'] == 'error'
    assert 'error' in result

if __name__ == '__main__':
    pytest.main(['-v', __file__]) 