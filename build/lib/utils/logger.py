import logging
import logging.config
import yaml
from pathlib import Path

def setup_logging():
    """Set up logging configuration"""
    config_path = Path(__file__).parent.parent.parent / 'config' / 'logging_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.config.dictConfig(config)
    return logging.getLogger(__name__)

# Create logger instance
logger = setup_logging()
