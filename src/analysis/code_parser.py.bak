import ast
from typing import List, Dict
from ..utils.logger import logger

class CodeAnalyzer:
    def analyze_file(self, file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return [{'type': 'syntax_error', 'message': str(e), 'line': e.lineno}]
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Function length check (stricter)
                func_lines = len(ast.unparse(node).splitlines())
                if func_lines > 10:  # Lowered from 15
                    issues.append({
                        'type': 'length',
                        'message': f'Function {node.name} is too long ({func_lines} lines)',
                        'line': node.lineno,
                        'function': node.name,
                        'original': ast.unparse(node)
                    })
                
                # Complexity check
                complexity = self._calculate_complexity(node)
                if complexity > 4:  # Lowered from 5
                    issues.append({
                        'type': 'complexity',
                        'message': f'Function {node.name} has high complexity ({complexity})',
                        'line': node.lineno,
                        'function': node.name,
                        'original': ast.unparse(node)
                    })
                
                # Nesting depth check
                depth = self._check_nesting_depth(node)
                if depth > 2:  # Lowered from 3
                    issues.append({
                        'type': 'nesting',
                        'message': f'Function {node.name} has deep nesting (depth: {depth})',
                        'line': node.lineno,
                        'function': node.name,
                        'original': ast.unparse(node)
                    })
                
                # Arguments check
                args = len(node.args.args)
                if args > 3:
                    issues.append({
                        'type': 'args',
                        'message': f'Function {node.name} has too many arguments ({args})',
                        'line': node.lineno,
                        'function': node.name,
                        'original': ast.unparse(node)
                    })

                # Error handling check
                try_count = sum(1 for child in ast.walk(node) if isinstance(child, ast.Try))
                if try_count > 1:
                    issues.append({
                        'type': 'error_handling',
                        'message': f'Function {node.name} has multiple try blocks',
                        'line': node.lineno,
                        'function': node.name,
                        'original': ast.unparse(node)
                    })

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity

    def _check_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth"""
        def get_depth(node, current=0):
            max_depth = current
            
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.With,
                                   ast.AsyncFor, ast.AsyncWith, ast.Try)):
                    child_depth = get_depth(child, current + 1)
                    max_depth = max(max_depth, child_depth)
                else:
                    child_depth = get_depth(child, current)
                    max_depth = max(max_depth, child_depth)
            
            return max_depth
        
        return get_depth(node) 