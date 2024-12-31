import aiohttp
import json
from typing import Optional, Dict, Any
from ..utils.logger import logger

class OpenRouterClient:
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config['api']['openrouter_key']
        self.model = config['api']['model']
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
    async def get_completion(self, prompt: str) -> Optional[str]:
        """Get completion from OpenRouter API"""
        if not self.api_key:
            raise ValueError("OpenRouter API key not found in config")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Replace with your repo
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a Python code improvement assistant. Provide specific, actionable improvements."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=data, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"API Error: {error_text}")
                        return None
                    
                    result = await response.json()
                    logger.debug(f"API Response: {result}")  # Debug log
                    
                    if 'choices' in result and result['choices']:
                        return result['choices'][0]['message']['content']
                    return None

        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return None 