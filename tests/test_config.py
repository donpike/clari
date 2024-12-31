import pytest
import sys
from pathlib import Path
import yaml

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import ConfigManager
from src.utils.logger import logger

def test_config_loading():
    """Test if configuration loads correctly"""
    config = ConfigManager()
    
    # Test if settings are loaded
    assert config.settings is not None
    
    # Test if specific settings exist
    assert 'openrouter' in config.settings
    assert 'analysis' in config.settings
    
    # Test specific values
    assert config.settings['openrouter']['default_model'] == "claude-3-5-sonnet"
    assert config.settings['analysis']['max_function_length'] == 20

def test_logging():
    """Test if logging works"""
    logger.info("Test log message")
    # If no exception is raised, logging is working 

def test_file_structure():
    """Test if all necessary files and directories exist"""
    config_file = Path("config/settings.yaml")
    log_dir = Path("logs")
    assert config_file.exists(), "Settings file not found"
    assert log_dir.exists(), "Logs directory not found"

def test_logging_file_creation():
    """Test if logging actually creates a file"""
    logger.info("Test message")
    log_file = Path("logs/app.log")
    assert log_file.exists(), "Log file not created"
    assert log_file.stat().st_size > 0, "Log file is empty"

def test_openrouter_settings():
    """Test OpenRouter specific settings"""
    config = ConfigManager()
    openrouter = config.settings['openrouter']
    assert 'default_model' in openrouter
    assert 'temperature' in openrouter
    assert 'max_tokens' in openrouter 

def test_config_file_format():
    """Test if the YAML files are properly formatted"""
    config_files = [
        Path("config/settings.yaml"),
        Path("config/logging_config.yaml")
    ]
    
    for config_file in config_files:
        try:
            with open(config_file, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML format in {config_file}: {e}")

def test_config_required_sections():
    """Test if all required configuration sections exist"""
    config = ConfigManager()
    required_sections = {
        'analysis': ['max_function_length', 'max_class_methods', 'style_checks'],
        'openrouter': ['default_model', 'temperature', 'max_tokens'],
        'logging': ['level', 'file', 'format']
    }
    
    for section, fields in required_sections.items():
        assert section in config.settings, f"Missing section: {section}"
        for field in fields:
            assert field in config.settings[section], f"Missing field: {field} in section {section}"

def test_config_value_types():
    """Test if configuration values have correct types"""
    config = ConfigManager()
    
    # Test numeric values
    assert isinstance(config.settings['analysis']['max_function_length'], int)
    assert isinstance(config.settings['openrouter']['temperature'], float)
    assert isinstance(config.settings['openrouter']['max_tokens'], int)
    
    # Test boolean values
    assert isinstance(config.settings['analysis']['style_checks']['enable_naming_convention'], bool)
    
    # Test string values
    assert isinstance(config.settings['openrouter']['default_model'], str)

def test_logger_configuration():
    """Test logger configuration and behavior"""
    # Test different log levels
    test_messages = {
        'debug': 'Debug test message',
        'info': 'Info test message',
        'warning': 'Warning test message',
        'error': 'Error test message'
    }
    
    for level, message in test_messages.items():
        getattr(logger, level)(message)
    
    # Check if log file contains the messages
    log_file = Path("logs/app.log")
    with open(log_file, 'r') as f:
        log_content = f.read()
        for message in test_messages.values():
            assert message in log_content, f"Log message not found: {message}"

def test_path_resolution():
    """Test if paths are properly resolved"""
    config = ConfigManager()
    
    # Test if paths are absolute
    assert config.settings_path.is_absolute()
    
    # Test if paths are resolved correctly
    assert config.settings_path.exists()
    assert (project_root / 'logs').exists()
    assert (project_root / 'config').exists()

@pytest.mark.parametrize("invalid_path", [
    "nonexistent/settings.yaml",
    "config/nonexistent.yaml"
])
def test_config_error_handling(invalid_path):
    """Test error handling for invalid configurations"""
    class TestConfigManager(ConfigManager):
        def __init__(self, test_path):
            self.settings_path = Path(test_path)
            with pytest.raises(Exception):
                self.load_settings()
    
    TestConfigManager(invalid_path) 