import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Dict, Any

def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """Setup the logger with configuration"""
    logger = logging.getLogger('autocoder')
    logger.setLevel(config['logging']['level'])
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = RotatingFileHandler(
        config['logging']['file'],
        maxBytes=config['logging']['max_file_size'],
        backupCount=config['logging']['backup_count']
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create global logger instance
logger = setup_logger({
    'logging': {
        'level': 'INFO',
        'file': 'autocoder.log',
        'max_file_size': 10485760,
        'backup_count': 5
    }
})
