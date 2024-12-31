import pytest
from pathlib import Path
import yaml

@pytest.fixture
def test_config():
    with open('config/settings.yaml') as f:
        return yaml.safe_load(f)

@pytest.fixture
def mock_openrouter_response():
    return {
        "choices": [{
            "message": {
                "content": "Mocked response content"
            }
        }]
    }

@pytest.fixture
def sample_python_file(tmp_path):
    content = """
def test_function():
    # This is a test function
    return "test"
    """
    file_path = tmp_path / "test.py"
    file_path.write_text(content)
    return file_path 