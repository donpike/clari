from pathlib import Path
import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.default_model = os.getenv('DEFAULT_MODEL', 'claude-3-sonnet')
        self.api_base_url = os.getenv('API_BASE_URL', 'https://api.openrouter.ai/api/v1')
        
    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "HTTP-Referer": "http://localhost:5000",  # Replace with your actual domain
            "Content-Type": "application/json"
        }

    def validate_config(self):
        if not self.openrouter_api_key:
            raise ValueError("OpenRouter API key not found in environment variables") 