import ast
from typing import Dict, Any, List, Set

class PatternDetector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.patterns = {
            'god_class': self._check_god_class,
            'large_class': self._check_large_class,
            'complex_function': self._check_complex_function,
            'long_function': self._check_long_function,
            'nested_blocks': self._check_nested_blocks,
            'too_many_arguments': self._check_too_many_arguments
        }

    def _check_large_class(self, node: ast.ClassDef) -> bool:
        """Check if a class is too large based on lines of code"""
        # Get the last line number of the class
        last_line = max(
            (getattr(n, 'lineno', 0) for n in ast.walk(node)),
            default=node.lineno
        )
        
        # Calculate class length
        class_length = last_line - node.lineno
        
        # Check against configuration
        return class_length > self.config['analysis']['max_class_length']

    def _check_god_class(self, node: ast.ClassDef) -> bool:
        """Check if a class has too many methods or attributes"""
        method_count = len([n for n in node.body if isinstance(n, ast.FunctionDef)])
        attr_count = len([n for n in node.body if isinstance(n, ast.Assign)])
        
        return (method_count > self.config['analysis']['max_class_methods'] or
                attr_count > self.config['analysis']['max_attributes'])

    def _check_complex_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is too complex"""
        complexity = self._calculate_complexity(node)
        return complexity > self.config['analysis']['max_method_complexity']

    def _check_long_function(self, node: ast.FunctionDef) -> bool:
        """Check if a function is too long"""
        # Get the last line number of the function
        last_line = max(
            (getattr(n, 'lineno', 0) for n in ast.walk(node)),
            default=node.lineno
        )
        
        # Calculate function length
        func_length = last_line - node.lineno
        return func_length > self.config['analysis']['max_function_length']

    def _check_nested_blocks(self, node: ast.AST) -> bool:
        """Check for deeply nested blocks"""
        def get_nesting_level(node: ast.AST, level: int = 0) -> int:
            if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                level += 1
            
            child_levels = [
                get_nesting_level(child, level)
                for child in ast.iter_child_nodes(node)
            ]
            
            return max(child_levels) if child_levels else level
        
        nesting_level = get_nesting_level(node)
        return nesting_level > self.config['analysis']['max_nested_blocks']

    def _check_too_many_arguments(self, node: ast.FunctionDef) -> bool:
        """Check if a function has too many arguments"""
        args_count = len(node.args.args)
        return args_count > self.config['analysis']['max_arguments']

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity

    def detect_patterns(self, tree: ast.AST) -> Dict[str, List[Dict[str, Any]]]:
        """Detect patterns in the AST"""
        results = {pattern: [] for pattern in self.patterns}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for pattern, checker in self.patterns.items():
                    if pattern in ('god_class', 'large_class'):
                        if checker(node):
                            results[pattern].append({
                                'type': pattern,
                                'name': node.name,
                                'line': node.lineno
                            })
                            
            elif isinstance(node, ast.FunctionDef):
                for pattern, checker in self.patterns.items():
                    if pattern in ('complex_function', 'long_function', 'too_many_arguments'):
                        if checker(node):
                            results[pattern].append({
                                'type': pattern,
                                'name': node.name,
                                'line': node.lineno
                            })
                            
            # Check nested blocks for any node
            if self.patterns['nested_blocks'](node):
                results['nested_blocks'].append({
                    'type': 'nested_blocks',
                    'line': getattr(node, 'lineno', 0)
                })
                
        return results 