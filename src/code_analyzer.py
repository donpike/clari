import ast
from typing import List, Dict, Any
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes Python code for potential improvements"""
    
    def analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a Python file for potential improvements.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of issues found in the code
        """
        logger.debug(f"Starting analysis of file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            issues = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    logger.debug(f"Analyzing {node.__class__.__name__}: {node.name}")
                    
                    # Check for malformed docstrings
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        logger.debug(f"Missing docstring in {node.name}")
                        issues.append({
                            'type': 'missing_docstring',
                            'line': node.lineno,
                            'message': f"Missing docstring for {node.name}",
                            'node_type': node.__class__.__name__,
                            'name': node.name
                        })
                    elif '"\\"' in docstring or '\\""' in docstring:
                        logger.debug(f"Malformed docstring in {node.name}")
                        issues.append({
                            'type': 'malformed_docstring',
                            'line': node.lineno,
                            'message': f"Malformed docstring for {node.name}",
                            'node_type': node.__class__.__name__,
                            'name': node.name
                        })
                    
                    # Check function arguments and return types
                    if isinstance(node, ast.FunctionDef):
                        logger.debug(f"Checking function arguments for {node.name}")
                        # Check for numeric operations needing int type
                        is_numeric = any(op in node.name.lower() for op in ['add', 'subtract', 'multiply', 'divide'])
                        
                        for arg in node.args.args:
                            if arg.arg != 'self':
                                if arg.annotation is None:
                                    logger.debug(f"Missing type hint for argument '{arg.arg}' in {node.name}")
                                    issues.append({
                                        'type': 'missing_type_hint',
                                        'line': node.lineno,
                                        'message': f"Missing type hint for argument '{arg.arg}' in function '{node.name}'",
                                        'node_type': 'argument',
                                        'function': node.name,
                                        'argument': arg.arg,
                                        'name': node.name,
                                        'suggested_type': 'int' if is_numeric else 'Any'
                                    })
                                elif is_numeric and getattr(arg.annotation, 'id', None) == 'Any':
                                    logger.debug(f"Imprecise type hint for argument '{arg.arg}' in {node.name}")
                                    issues.append({
                                        'type': 'imprecise_type_hint',
                                        'line': node.lineno,
                                        'message': f"Could use more specific type hint (int) for argument '{arg.arg}' in function '{node.name}'",
                                        'node_type': 'argument',
                                        'function': node.name,
                                        'argument': arg.arg,
                                        'name': node.name,
                                        'suggested_type': 'int'
                                    })
                        
                        if node.returns is None:
                            logger.debug(f"Missing return type for {node.name}")
                            issues.append({
                                'type': 'missing_return_type',
                                'line': node.lineno,
                                'message': f"Missing return type hint for function '{node.name}'",
                                'node_type': 'return',
                                'function': node.name,
                                'name': node.name,
                                'suggested_type': 'int' if is_numeric else 'Any'
                            })
                        elif is_numeric and getattr(node.returns, 'id', None) == 'Any':
                            logger.debug(f"Imprecise return type for {node.name}")
                            issues.append({
                                'type': 'imprecise_return_type',
                                'line': node.lineno,
                                'message': f"Could use more specific return type (int) for function '{node.name}'",
                                'node_type': 'return',
                                'function': node.name,
                                'name': node.name,
                                'suggested_type': 'int'
                            })
            
            logger.debug(f"Analysis complete. Found {len(issues)} issues")
            logger.debug(f"Issues: {issues}")
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}", exc_info=True)
            return []