import pytest
from pathlib import Path
from unittest.mock import Mock, patch, ANY
from src.main import AutoCoder
from textwrap import dedent  # Important for handling indentation

@pytest.fixture
def config():
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

@pytest.fixture
def auto_coder(config):
    return AutoCoder(config)

@pytest.mark.asyncio
async def test_improve_simple_code(auto_coder, tmp_path):
    """Test improving a simple code file"""
    test_file = tmp_path / "simple.py"
    test_file.write_text("def hello(): return 'world'")
    
    mock_response = {
        'suggestions': 'Add docstring to function',
        'model_used': 'test-model'
    }
    
    with patch.object(auto_coder.api_client, 'analyze_code', return_value=mock_response):
        result = await auto_coder.improve_code(test_file)
        
        assert result['analysis']['metrics']['num_functions'] == 1
        assert len(result['analysis']['issues']) == 0
        assert result['improvements'] == 'Add docstring to function'

@pytest.mark.asyncio
async def test_improve_complex_code(auto_coder, tmp_path):
    """Test improving code with multiple issues"""
    test_file = tmp_path / "complex.py"
    code = dedent("""
    from module import *

    class LargeClass:
        def method1(self): pass
        def method2(self): pass
        def method3(self): pass
        def method4(self): pass
        def method5(self): pass
        def method6(self): pass
        def method7(self): pass
        def method8(self): pass
        def method9(self): pass
        def method10(self): pass
        def method11(self): pass
        
    def risky_function():
        try:
            something()
        except:
            pass
    """).lstrip()  # lstrip() removes leading newline
    
    test_file.write_text(code)
    
    mock_response = {
        'suggestions': 'Multiple improvements needed...',
        'model_used': 'test-model'
    }
    
    with patch.object(auto_coder.api_client, 'analyze_code', return_value=mock_response):
        result = await auto_coder.improve_code(test_file)
        
        # Check if analysis caught all issues
        issues = result['analysis']['issues']
        assert any(i['type'] == 'star_import' for i in issues)
        assert any(i['type'] == 'bare_except' for i in issues)
        assert 'LargeClass' in result['analysis']['metrics']['large_classes']

@pytest.mark.asyncio
async def test_prompt_generation(auto_coder, tmp_path):
    """Test if the improvement prompt is properly generated"""
    test_file = tmp_path / "prompt_test.py"
    # Make the function longer to exceed the max_function_length threshold
    code = dedent("""
    def very_long_function():
        a = 1
        b = 2
        c = 3
        d = 4
        e = 5
        f = 6
        g = 7
        h = 8
        i = 9
        j = 10
        k = 11
        l = 12
        m = 13
        n = 14
        o = 15
        p = 16
        q = 17
        r = 18
        s = 19
        t = 20
        u = 21  # Exceeds the default threshold of 20
        return a + b + c + d + e + f + g + h + i + j + k + l + m + n + o + p + q + r + s + t + u
    
    try:
        something()
    except:
        pass
    """).lstrip()
    
    test_file.write_text(code)
    
    with patch.object(auto_coder.api_client, 'analyze_code') as mock_analyze:
        await auto_coder.improve_code(test_file)
        
        # Check if the prompt contains relevant information
        call_args = mock_analyze.call_args
        prompt = call_args[0][1]  # Get the prompt argument
        
        # Print the prompt for debugging
        print("\nGenerated prompt:")
        print(prompt)
        
        assert 'very_long_function' in prompt
        assert 'bare except' in prompt.lower()

@pytest.mark.asyncio
async def test_api_error_handling(auto_coder, tmp_path):
    """Test handling of API errors"""
    test_file = tmp_path / "error_test.py"
    test_file.write_text("def test(): pass")
    
    with patch.object(auto_coder.api_client, 'analyze_code', side_effect=Exception("API Error")):
        with pytest.raises(Exception) as exc_info:
            await auto_coder.improve_code(test_file)
        assert "API Error" in str(exc_info.value)

@pytest.mark.asyncio
async def test_file_error_handling(auto_coder):
    """Test handling of file-related errors"""
    test_cases = [
        Path("nonexistent.py"),
        Path("invalid/path/test.py"),
        Path("")
    ]
    
    for test_path in test_cases:
        with pytest.raises((FileNotFoundError, OSError)):
            await auto_coder.improve_code(test_path)

@pytest.mark.asyncio
async def test_empty_file_handling(auto_coder, tmp_path):
    """Test handling of empty files"""
    test_file = tmp_path / "empty.py"
    test_file.write_text("")
    
    mock_response = {
        'suggestions': 'File is empty',
        'model_used': 'test-model'
    }
    
    with patch.object(auto_coder.api_client, 'analyze_code', return_value=mock_response):
        result = await auto_coder.improve_code(test_file)
        
        assert result['analysis']['metrics']['num_functions'] == 0
        assert result['analysis']['metrics']['num_classes'] == 0

def test_initialization(config):
    """Test AutoCoder initialization"""
    # Test with valid config
    auto_coder = AutoCoder(config)
    assert auto_coder.analyzer is not None
    assert auto_coder.api_client is not None
    
    # Test with invalid config
    invalid_configs = [
        {},
        {'analysis': {}},
        {'openrouter': {}}
    ]
    
    for invalid_config in invalid_configs:
        with pytest.raises(KeyError):
            AutoCoder(invalid_config) 