from pathlib import Path
from typing import Dict, Any, List
from .code_analyzer import CodeAnalyzer
from .core.code_modifier import CodeModifier, SimpleImprovement
from .openrouter_client import OpenRouterClient
from .config import default_config
import json
import logging

class AutoCoder:
    def __init__(self, config=None):
        """Initialize AutoCoder with optional config."""
        self.config = config or default_config
        self.analyzer = CodeAnalyzer()
        self.modifier = CodeModifier()
        self.client = OpenRouterClient()

    async def analyze_code(self, file_path: Path) -> Dict[str, Any]:
        """Only analyze the code without modifying it."""
        try:
            issues = self.analyzer.analyze_file(file_path)
            return {
                'status': 'success',
                'automatic_fixes': len(issues),
                'issues': issues,
                'message': 'Analysis complete'
            }
        except Exception as e:
            logging.error(f"Error analyzing code: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    async def improve_code(self, file_path: Path, apply_changes: bool = False, improvement_level: int = 2) -> Dict[str, Any]:
        """Analyze and improve the code.
        
        Args:
            file_path: Path to the file to improve
            apply_changes: If True, apply the changes; if False, just return proposed changes
            improvement_level: Level of improvements to apply (1=basic, 2=intermediate, 3=advanced)
        """
        try:
            # First analyze
            issues = self.analyzer.analyze_file(file_path)
            if not issues:
                return {'status': 'success', 'message': 'No improvements needed'}

            # Split issues into automatic and AI-needed
            automatic_fixes = []
            complex_issues = []
            for issue in issues:
                if self.modifier.can_handle_automatically(issue):
                    automatic_fixes.append(issue)
                else:
                    complex_issues.append(issue)
            
            # Filter issues based on improvement level
            if improvement_level == 1:  # Basic - only automatic fixes
                complex_issues = []
            elif improvement_level == 2:  # Intermediate - automatic + simple AI
                complex_issues = [i for i in complex_issues 
                                if i['type'] in self.config.intermediate_improvements]

            if not apply_changes:
                # Just return what would be changed
                return {
                    'status': 'success',
                    'automatic_fixes': len(automatic_fixes),
                    'complex_issues': len(complex_issues),
                    'proposed_changes': {
                        'automatic': automatic_fixes,
                        'complex': complex_issues
                    }
                }

            improvements = []
            
            # Apply automatic fixes if any
            if automatic_fixes:
                # Let CodeModifier create the SimpleImprovement objects
                auto_fixes = []
                for issue in automatic_fixes:
                    fix = self.modifier._create_simple_fix(issue)
                    if fix:
                        auto_fixes.append(fix)
                
                if auto_fixes:
                    auto_result = self.modifier.modify_file(file_path, auto_fixes)
                    if auto_result['status'] == 'success':
                        improvements.extend(auto_result['changes'])
                        logging.info(f'Applied {len(auto_result["changes"])} automatic improvements to {file_path}')

            # Handle complex issues with AI if needed and allowed by improvement level
            if complex_issues and improvement_level > 1:
                with open(file_path, 'r') as file:
                    code_content = file.read()
                
                # For intermediate level, use a simpler prompt focused on basic improvements
                if improvement_level == 2:
                    prompt = self._create_simple_improvement_prompt(code_content, complex_issues)
                else:  # Advanced level - use full AI capabilities
                    prompt = self._create_improvement_prompt(code_content, complex_issues)
                    
                ai_response = await self.client.generate_code(prompt)
                improvements.append({
                    'type': 'ai_suggestion',
                    'changes': ai_response,
                    'level': 'intermediate' if improvement_level == 2 else 'advanced'
                })
                logging.info(f'Generated {improvements[-1]["level"]} AI improvements for {file_path}')

            return {
                'status': 'success',
                'automatic_fixes': len(automatic_fixes),
                'complex_issues': len(complex_issues),
                'improvements': improvements
            }

        except Exception as e:
            logging.error(f'Error improving code: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    def _create_simple_improvement_prompt(self, code: str, issues: List[Dict]) -> str:
        """Create a prompt for simple AI code improvements."""
        return f"""
        Please make basic improvements to the following code, focusing only on:
        1. Code style and formatting
        2. Simple optimizations
        3. Basic error handling
        
        Issues to address:
        {json.dumps(issues, indent=2)}
        
        Code to improve:
        ```python
        {code}
        ```
        
        Please provide only the improved code without explanations.
        """

    def _create_improvement_prompt(self, code: str, issues: List[Dict]) -> str:
        """Create a prompt for AI code improvements."""
        return f"""
        Please improve the following code, addressing these issues:
        {json.dumps(issues, indent=2)}
        
        Here's the code:
        ```python
        {code}
        ```
        
        Please provide:
        1. Improved version of the code
        2. Explanation of changes
        3. Any additional recommendations
        """

    def should_use_ai(self, issue: Dict[str, Any]) -> bool:
        """Determine if an issue should be handled by AI based on config."""
        if issue['type'] not in self.config.ai_improvements:
            return False
        
        estimated_cost = self.client.estimate_cost(issue)
        if estimated_cost > self.config.cost_threshold:
            logging.warning(f"Skipping AI improvement due to cost: ${estimated_cost:.4f}")
            return False
        
        return True
