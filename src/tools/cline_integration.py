from mcp import Tool
from typing import Dict, Any
import json

class ClineIntegration(Tool):
    name: str = "cline_improver"
    description: str = "Cline integration for code improvements"
    
    async def handle_improvement_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle improvement requests from Cline"""
        try:
            # Extract file path and improvements
            file_path = request['file_path']
            improvements = request['improvements']
            
            # Use the code improver tool
            code_improver = self.mcp.get_tool('code_improver')
            
            results = []
            for improvement in improvements:
                response = await code_improver.handle_file_modification(
                    file_path,
                    improvement
                )
                
                if response['success']:
                    results.append({
                        'status': 'success',
                        'diff': response['diff']
                    })
                else:
                    results.append({
                        'status': 'error',
                        'error': response['error']
                    })
            
            return {
                'success': True,
                'data': {
                    'results': results,
                    'message': f"Applied {len(results)} improvements"
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            } 