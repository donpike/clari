import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.cli import cli, improve, scan
from textwrap import dedent

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def mock_config():
    return {
        'analysis': {
            'max_function_length': 20,
            'max_class_methods': 10,
            'style_checks': {
                'enable_naming_convention': True,
                'enable_docstring_check': True
            }
        },
        'openrouter': {
            'default_model': 'claude-3-5-sonnet',
            'temperature': 0.7,
            'max_tokens': 2000
        }
    }

def test_improve_command(runner, tmp_path, mock_config):
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    # Create test config
    config_file = tmp_path / "config.yaml"
    import yaml
    with open(config_file, 'w') as f:
        yaml.dump(mock_config, f)
    
    with patch('src.main.AutoCoder.improve_code') as mock_improve:
        mock_improve.return_value = {
            'file_path': str(test_file),
            'analysis': {
                'issues': [{'message': 'Missing docstring', 'line': 1}],
                'metrics': {
                    'num_functions': 1,
                    'num_classes': 0,
                    'long_functions': [],
                    'large_classes': []
                }
            },
            'improvements': 'Add docstring to function'
        }
        
        result = runner.invoke(cli, ['improve', str(test_file), '-c', str(config_file)])
        assert result.exit_code == 0
        assert 'Missing docstring' in result.output

def test_scan_command(runner, tmp_path):
    # Create test directory with Python files
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    
    (test_dir / "file1.py").write_text("def test1(): pass")
    (test_dir / "file2.py").write_text("def test2(): pass")
    
    with patch('src.cli.improve.callback') as mock_improve:
        result = runner.invoke(cli, ['scan', str(test_dir)])
        assert result.exit_code == 0
        assert mock_improve.call_count == 2

def test_recursive_scan(runner, tmp_path):
    # Create nested directory structure
    root_dir = tmp_path / "root"
    sub_dir = root_dir / "sub"
    root_dir.mkdir()
    sub_dir.mkdir()
    
    (root_dir / "file1.py").write_text("def test1(): pass")
    (sub_dir / "file2.py").write_text("def test2(): pass")
    
    with patch('src.cli.improve.callback') as mock_improve:
        result = runner.invoke(cli, ['scan', str(root_dir), '--recursive'])
        assert result.exit_code == 0
        assert mock_improve.call_count == 2

def test_output_file(runner, tmp_path, mock_config):
    # Test saving output to file
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")
    
    output_file = tmp_path / "output.txt"
    
    with patch('src.main.AutoCoder.improve_code') as mock_improve:
        mock_improve.return_value = {
            'file_path': str(test_file),
            'analysis': {
                'issues': [],
                'metrics': {
                    'num_functions': 1,
                    'num_classes': 0,
                    'long_functions': [],
                    'large_classes': []
                }
            },
            'improvements': 'No improvements needed'
        }
        
        result = runner.invoke(cli, [
            'improve', 
            str(test_file), 
            '--output', 
            str(output_file)
        ])
        
        assert result.exit_code == 0
        assert output_file.exists()
        assert 'No improvements needed' in output_file.read_text() 