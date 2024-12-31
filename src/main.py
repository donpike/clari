import asyncio
from pathlib import Path
from typing import Dict, Any, List
from .api.openrouter_client import OpenRouterClient
from .analysis.code_parser import CodeAnalyzer
from .core.safety import SafetyChecker
from .utils.logger import logger
from .tools.code_improver import CodeImproverTool
from .core.code_modifier import CodeModifier
import json

class AutoCoder:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.code_analyzer = CodeAnalyzer()
        self.code_modifier = CodeModifier()
        
    async def improve_code(self, file_path: Path) -> Dict[str, Any]:
        try:
            # First analyze
            issues = self.code_analyzer.analyze_file(file_path)
            
            if not issues:
                return {
                    'status': 'success',
                    'message': 'No improvements needed'
                }
            
            # Generate improvements
            improvements = self._generate_improvements(issues)
            
            # Apply improvements
            result = self.code_modifier.modify_file(file_path, improvements)
            
            return {
                'status': result['status'],
                'file_path': str(file_path),
                'improvements': result.get('changes', []),
                'backup': result.get('backup'),
                'analysis': {
                    'issues': issues,
                    'metrics': self.code_analyzer.get_metrics(file_path)
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    async def _get_ai_improvements(self, prompt: str) -> List[Dict[str, Any]]:
        """Get improvements from AI and parse the response"""
        try:
            logger.debug(f"Sending prompt to AI: {prompt}")
            response = await self.ai_client.get_completion(prompt)
            logger.debug(f"Received AI response: {response}")
            
            if not response:
                logger.warning("No response from AI client")
                return []

            # Parse improvements from the response
            improvements = []
            current_improvement = None
            current_section = None
            code_block = []
            
            for line in response.split('\n'):
                line = line.rstrip()
                
                # Handle section headers
                if line.startswith('Type:'):
                    if current_improvement:
                        # Clean up and add the previous improvement
                        if code_block and current_section:
                            current_improvement[current_section] = '\n'.join(code_block)
                        improvements.append(current_improvement)
                    
                    current_improvement = {'type': line[5:].strip()}
                    current_section = None
                    code_block = []
                    
                elif line.startswith('Description:') and current_improvement:
                    if code_block and current_section:
                        current_improvement[current_section] = '\n'.join(code_block)
                    current_improvement['description'] = line[12:].strip()
                    current_section = None
                    code_block = []
                    
                elif line.startswith('Original:') and current_improvement:
                    if code_block and current_section:
                        current_improvement[current_section] = '\n'.join(code_block)
                    current_section = 'original'
                    code_block = []
                    
                elif line.startswith('Improved:') and current_improvement:
                    if code_block and current_section:
                        current_improvement[current_section] = '\n'.join(code_block)
                    current_section = 'improved'
                    code_block = []
                    
                # Handle code blocks
                elif current_section and current_improvement:
                    if line.strip():  # Only add non-empty lines
                        code_block.append(line)
            
            # Add the last improvement
            if current_improvement:
                if code_block and current_section:
                    current_improvement[current_section] = '\n'.join(code_block)
                improvements.append(current_improvement)

            # Validate improvements
            valid_improvements = []
            for imp in improvements:
                if all(k in imp for k in ['type', 'description', 'original', 'improved']):
                    # Ensure code blocks have proper indentation
                    imp['original'] = self._normalize_indentation(imp['original'])
                    imp['improved'] = self._normalize_indentation(imp['improved'])
                    valid_improvements.append(imp)
            
            logger.info(f"Parsed {len(valid_improvements)} valid improvements from AI response")
            return valid_improvements
            
        except Exception as e:
            logger.error(f"Error parsing AI improvements: {str(e)}")
            return []

    def _normalize_indentation(self, code: str) -> str:
        """Normalize indentation of a code block"""
        if not code:
            return code
            
        lines = code.splitlines()
        if not lines:
            return code
            
        # Find the minimum indentation
        min_indent = float('inf')
        for line in lines:
            if line.strip():  # Only check non-empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
                
        if min_indent == float('inf'):
            return code
            
        # Remove the common indentation
        normalized_lines = []
        for line in lines:
            if line.strip():
                normalized_lines.append(line[min_indent:])
            else:
                normalized_lines.append('')
                
        return '\n'.join(normalized_lines)

    async def analyze_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Analyze project structure"""
        return {
            'suggestions': []
        }

    async def batch_process_directory(self, 
                                    directory: Path,
                                    safety_level: str = 'high',
                                    max_changes_per_file: int = 5) -> Dict[str, Any]:
        """Process multiple files in a directory"""
        results = {}
        for file_path in directory.rglob('*.py'):
            results[str(file_path)] = await self.improve_code(file_path)
        return results

    def _create_improvement_prompt(self, code: str, issues: List[Dict]) -> str:
        return f"""
        Analyze and improve this Python code. Found issues:
        {json.dumps(issues, indent=2)}

        Code to improve:
        ```python
        {code}
        ```

        For each issue, provide improvements in this exact format:

        Type: [code_style|performance|security|maintainability]
        Description: [Clear explanation of what needs to be improved]
        Original: [The specific code that needs improvement]
        Improved: [The improved version of that code]

        Focus on practical, specific improvements. Each improvement should be complete and self-contained.
        """

async def improve_code(file_path: Path) -> Dict[str, Any]:
    """Improve code in the given file"""
    auto_coder = AutoCoder()
    return await auto_coder.improve_code(file_path)

def main():
    """Main entry point"""
    import yaml
    
    # Load configuration
    config_path = Path(__file__).parent.parent / 'config' / 'settings.yaml'
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Create AutoCoder instance
    auto_coder = AutoCoder(config)
    
    # Example usage
    async def improve_file(file_path: str):
        result = await auto_coder.improve_code(Path(file_path))
        print(f"\nAnalysis Results for {result['file_path']}:")
        print("\nIssues found:")
        for issue in result['analysis']['issues']:
            print(f"- {issue['message']}")
        print("\nSuggested Improvements:")
        print(result['improvements'])

    # Run with example file
    asyncio.run(improve_file("example.py"))

if __name__ == "__main__":
    main()
