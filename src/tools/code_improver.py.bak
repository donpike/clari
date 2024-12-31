from mcp import Tool
import ast
import astor
import json
from pathlib import Path
from typing import Dict, Any, Union

class CodeImproverTool(Tool):
    name: str = "code_improver"
    description: str = "AST-based code improvement tool"
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming tool requests"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id', 1)
        
        try:
            if method == 'analyze_code':
                result = await self._analyze_code(params.get('file_path', ''))
            elif method == 'improve_code':
                result = await self._improve_code(
                    params.get('file_path', ''),
                    params.get('improvement', {})
                )
            else:
                return {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': -32601,
                        'message': f'Method {method} not found'
                    },
                    'id': request_id
                }
            
            return {
                'jsonrpc': '2.0',
                'result': result,
                'id': request_id
            }
            
        except Exception as e:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32000,
                    'message': str(e)
                },
                'id': request_id
            }
    
    async def _analyze_code(self, file_path: str) -> Dict[str, Any]:
        """Internal method to analyze code for potential improvements"""
        path = Path(file_path)
        
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        # Parse to AST
        tree = ast.parse(source)
        
        # Find potential improvements
        analyzer = CodeAnalyzer()
        issues = analyzer.analyze(tree, source)
        
        return {
            "status": "success",
            "issues": issues
        }
    
    async def _improve_code(self, file_path: str, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to handle code modifications using AST"""
        path = Path(file_path)
        
        # Read the file
        with open(path, 'r', encoding='utf-8') as f:
            source = f.read()
            
        # Parse to AST
        tree = ast.parse(source)
        
        # Apply improvements
        transformer = CodeTransformer(improvement)
        modified_tree = transformer.visit(tree)
        
        # Generate new source
        new_source = astor.to_source(modified_tree)
        
        return {
            'status': 'success',
            'diff': {
                'file': str(path),
                'original': source,
                'modified': new_source
            }
        }

class CodeAnalyzer:
    def analyze(self, tree: ast.AST, source: str) -> list:
        """Analyze AST for potential improvements"""
        issues = []
        
        # Walk through the AST nodes
        for node in ast.walk(tree):
            # Check for function definitions
            if isinstance(node, ast.FunctionDef):
                # Example: Check for functions without docstrings
                if not ast.get_docstring(node):
                    issues.append({
                        'message': f'Function {node.name} is missing a docstring',
                        'original': ast.unparse(node),
                        'type': 'missing_docstring'
                    })
                
                # Example: Check for long functions (more than 15 lines)
                if len(node.body) > 15:
                    issues.append({
                        'message': f'Function {node.name} is too long ({len(node.body)} lines)',
                        'original': ast.unparse(node),
                        'type': 'long_function'
                    })
            
            # Check for complex if statements
            elif isinstance(node, ast.If):
                test_source = ast.unparse(node.test)
                if test_source.count('and') + test_source.count('or') > 2:
                    issues.append({
                        'message': 'Complex conditional statement could be simplified',
                        'original': ast.unparse(node),
                        'type': 'complex_condition'
                    })
        
        return issues

class CodeTransformer(ast.NodeTransformer):
    def __init__(self, improvement: Dict[str, Any]):
        self.improvement = improvement
        self.improvement_type = improvement.get('type', '')
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Visit and potentially modify function definitions"""
        if ast.unparse(node) == self.improvement['original']:
            if self.improvement_type == 'missing_docstring':
                # Add a docstring to the function
                docstring = ast.Expr(value=ast.Str(s=f"Description of {node.name} function"))
                node.body.insert(0, docstring)
                return node
            elif self.improvement_type == 'long_function':
                # If improved code is provided, use it
                if self.improvement.get('improved'):
                    try:
                        return ast.parse(self.improvement['improved']).body[0]
                    except:
                        return node
            else:
                # For other improvements, use provided improved code
                try:
                    return ast.parse(self.improvement['improved']).body[0]
                except:
                    return node
        return node
    
    def visit_If(self, node: ast.If) -> ast.AST:
        """Visit and potentially modify if statements"""
        if ast.unparse(node) == self.improvement['original']:
            if self.improvement_type == 'complex_condition':
                # If improved code is provided, use it
                if self.improvement.get('improved'):
                    try:
                        return ast.parse(self.improvement['improved']).body[0]
                    except:
                        return node
                
                # Otherwise, attempt to simplify the condition
                try:
                    # Extract the complex condition parts
                    test_source = ast.unparse(node.test)
                    if 'and' in test_source or 'or' in test_source:
                        # Create a new variable for the condition
                        condition_var = ast.Name(id='condition_result', ctx=ast.Store())
                        condition_assign = ast.Assign(
                            targets=[condition_var],
                            value=node.test
                        )
                        
                        # Create new if statement using the condition variable
                        new_if = ast.If(
                            test=ast.Name(id='condition_result', ctx=ast.Load()),
                            body=node.body,
                            orelse=node.orelse
                        )
                        
                        # Return both the assignment and the if statement
                        return [condition_assign, new_if]
                except:
                    return node
        return node
