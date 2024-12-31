import pytest
from pathlib import Path
from src.analysis.code_parser import CodeAnalyzer
from textwrap import dedent

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
        }
    }

@pytest.fixture
def analyzer(config):
    return CodeAnalyzer(config)

def test_analyze_simple_code(analyzer, tmp_path):
    code = dedent("""
    def short_function():
        return True

    def long_function():
        a = 1
        b = 2
        c = 3
        d = 4
        e = 5
        return a + b + c + d + e
    """)
    
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    
    result = analyzer.analyze_file(file_path)
    
    assert result['metrics']['num_functions'] == 2
    assert len(result['metrics']['long_functions']) == 0
    assert len(result['issues']) == 0

def test_detect_code_issues(analyzer, tmp_path):
    code = dedent("""
    from module import *
    
    def risky_function():
        try:
            something()
        except:
            pass
    """)
    
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    
    result = analyzer.analyze_file(file_path)
    issues = result['issues']
    
    assert len(issues) == 2
    assert any(i['type'] == 'star_import' for i in issues)
    assert any(i['type'] == 'bare_except' for i in issues)

def test_complex_class_analysis(analyzer, tmp_path):
    code = dedent("""
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
    """)
    
    file_path = tmp_path / "test.py"
    file_path.write_text(code)
    
    result = analyzer.analyze_file(file_path)
    
    assert 'LargeClass' in result['metrics']['large_classes']
    assert len(result['suggestions']) > 0

def test_error_handling(analyzer, tmp_path):
    non_existent_file = tmp_path / "nonexistent.py"
    
    with pytest.raises(FileNotFoundError):
        analyzer.analyze_file(non_existent_file) 