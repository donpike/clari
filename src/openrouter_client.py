import aiohttp
from typing import Dict, Any
import logging

class OpenRouterClient:
    """OpenRouter API client for code improvements."""

    def __init__(self) -> None:
        """Initialize the OpenRouter client."""
        self.api_key = self._get_api_key()
        self.base_url = "https://openrouter.ai/api/v1"

    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        return None

    async def generate_code(self, prompt: str) -> Dict[str, Any]:
        """Generate code improvements using AI.
        
        If API is not configured, return empty improvements.
        """
        if not self.api_key:
            logging.warning("OpenRouter API key not configured, skipping AI improvements")
            return {"improvements": []}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json={"prompt": prompt},
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logging.error(f"API error: {response.status}")
                        return {"improvements": []}
        except Exception as e:
            logging.error(f"Connection error: {str(e)}")
            return {"improvements": []}

    def estimate_cost(self, issue: Dict[str, Any]) -> float:
        """Estimate the cost of processing an issue with AI."""
        base_costs = {
            'logic_improvement': 0.002,
            'performance_optimization': 0.003,
            'complex_refactoring': 0.004
        }
        return base_costs.get(issue['type'], 0.005)
