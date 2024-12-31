from typing import Dict, Any
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def default_config() -> Dict[str, Any]:
    """Default configuration for AutoCoder"""
    return {
        'api': {
            'openrouter_key': os.getenv('OPENROUTER_API_KEY'),  # Get from .env
            'model': 'anthropic/claude-3-sonnet',
            'temperature': 0.7,
            'max_tokens': 2000,
            'mock_mode': False  # Set to False for development without API credits
        },
        'safety': {
            'backup_dir': 'backups',
            'max_changes_per_file': 5,
            'safety_level': 'high',
        },
        'analysis': {
            'max_file_size': 1000000,  # 1MB
            'max_complexity': 15,
            'max_line_length': 88,
            'max_function_length': 50,
            'max_class_length': 200,
            'max_class_methods': 20,
            'max_method_complexity': 8,
            'max_cognitive_complexity': 10,
            'min_test_coverage': 80,
            'max_nested_blocks': 4,
            'max_arguments': 5,
            'max_attributes': 15
        },
        'improvements': {
            'auto_apply': False,
            'require_confirmation': True,
            'track_changes': True,
            'max_suggestions_per_file': 10,
            'improvement_types': [
                'code_style',
                'performance',
                'security',
                'maintainability'
            ]
        },
        'learning': {
            'db_path': 'improvements.db',
            'min_confidence': 0.8,
            'learn_from_changes': True,
            'pattern_threshold': 0.7
        },
        'database': {
            'path': 'improvements.db',
            'backup_frequency': 'daily',
            'max_history_size': 1000
        },
        'logging': {
            'level': 'INFO',
            'file': 'autocoder.log',
            'max_file_size': 10485760,
            'backup_count': 5
        }
    } 