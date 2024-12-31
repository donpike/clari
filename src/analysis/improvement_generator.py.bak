from typing import Dict, Any, List
import ast
from pathlib import Path
import textwrap

class ImprovementGenerator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.improvements = {
            # Structure Improvements
            'long_function': self._improve_long_function,
            'complex_function': self._improve_complex_function,
            'god_class': self._improve_god_class,
            
            # Quality Improvements
            'duplicate_code': self._improve_duplicates,
            'magic_numbers': self._improve_magic_numbers,
            
            # Security Improvements
            'hardcoded_secrets': self._improve_secrets,
            'unsafe_eval': self._improve_unsafe_eval,
            
            # Performance Improvements
            'inefficient_list_usage': self._improve_list_usage,
            'repeated_calls': self._improve_repeated_calls
        }

    def generate_improvements(self, pattern_type: str, 
                            pattern_data: Dict[str, Any], 
                            code: str) -> Dict[str, Any]:
        """Generate specific improvements based on pattern type"""
        if pattern_type in self.improvements:
            return self.improvements[pattern_type](pattern_data, code)
        return self._generate_general_improvement(pattern_data, code)

    def _improve_long_function(self, data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Generate improvement for long functions"""
        func_name = data['name']
        lines = data['lines']
        
        # Extract the function code
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                func_code = ast.get_source_segment(code, node)
                
                # Analyze function structure
                blocks = self._identify_code_blocks(node)
                
                # Generate new functions
                new_functions = []
                for i, block in enumerate(blocks, 1):
                    new_func_name = f"{func_name}_{block['purpose']}"
                    new_functions.append(
                        self._create_helper_function(new_func_name, block)
                    )
                
                # Generate refactored main function
                main_function = self._create_refactored_main(func_name, blocks)
                
                return {
                    'original_code': func_code,
                    'improved_code': '\n\n'.join(new_functions + [main_function]),
                    'explanation': textwrap.dedent(f"""
                        The long function '{func_name}' ({lines} lines) has been split into smaller, 
                        more focused functions:
                        
                        {self._format_function_summary(blocks)}
                        
                        This improves readability and maintainability while following the Single 
                        Responsibility Principle.
                    """)
                }
        
        return {'error': f"Could not find function {func_name}"}

    def _improve_god_class(self, data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Generate improvement for God classes"""
        class_name = data['name']
        methods = data['methods']
        
        # Analyze class methods and attributes
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Group related methods and attributes
                groups = self._group_related_members(node)
                
                # Generate new classes
                new_classes = []
                for group in groups:
                    new_class = self._create_focused_class(
                        f"{class_name}{group['purpose']}", 
                        group
                    )
                    new_classes.append(new_class)
                
                # Generate facade class
                facade = self._create_facade_class(class_name, groups)
                
                return {
                    'original_code': ast.get_source_segment(code, node),
                    'improved_code': '\n\n'.join(new_classes + [facade]),
                    'explanation': textwrap.dedent(f"""
                        The God class '{class_name}' has been split into smaller, focused classes:
                        
                        {self._format_class_summary(groups)}
                        
                        A facade class maintains the original interface while delegating to the new classes.
                        This follows the Single Responsibility and Interface Segregation Principles.
                    """)
                }
        
        return {'error': f"Could not find class {class_name}"}

    def _improve_duplicates(self, data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Generate improvement for duplicate code"""
        original = data['original']
        duplicate = data['duplicate']
        
        # Extract the duplicate code
        tree = ast.parse(code)
        duplicate_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if node.name in [original, duplicate]:
                    duplicate_nodes.append(node)
        
        if len(duplicate_nodes) == 2:
            # Create a new shared function/method
            shared_code = self._create_shared_function(
                f"shared_{original}_{duplicate}",
                duplicate_nodes[0],
                duplicate_nodes[1]
            )
            
            return {
                'original_code': '\n\n'.join(
                    ast.get_source_segment(code, node) 
                    for node in duplicate_nodes
                ),
                'improved_code': shared_code,
                'explanation': textwrap.dedent(f"""
                    Duplicate code found in '{original}' and '{duplicate}' has been 
                    extracted into a shared function.
                    
                    This reduces code duplication and improves maintainability.
                    Both original functions now call the shared implementation.
                """)
            }
        
        return {'error': "Could not find duplicate code"}

    def _improve_repeated_calls(self, data: Dict[str, Any], code: str) -> Dict[str, Any]:
        """Generate improvement for repeated function calls"""
        call_info = data['calls']
        
        # Generate caching or optimization solution
        if self._is_pure_function(call_info):
            # Use memoization for pure functions
            improved = self._add_memoization(code, call_info)
        else:
            # Use result caching for impure functions
            improved = self._add_result_caching(code, call_info)
            
        return {
            'original_code': call_info['original_code'],
            'improved_code': improved,
            'explanation': textwrap.dedent(f"""
                Optimized repeated calls to '{call_info['name']}' by adding 
                {'memoization' if self._is_pure_function(call_info) else 'result caching'}.
                
                This reduces redundant computations and improves performance.
                The results are now cached and reused when possible.
            """)
        }

    def _identify_code_blocks(self, node: ast.AST) -> List[Dict[str, Any]]:
        """Identify logical blocks in code for refactoring"""
        blocks = []
        current_block = {'nodes': [], 'purpose': ''}
        
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Expr) and isinstance(child.value, ast.Str):
                # Comments or docstrings indicate block purpose
                current_block['purpose'] = child.value.s
            elif isinstance(child, (ast.If, ast.For, ast.While)):
                # Control structures often indicate new blocks
                if current_block['nodes']:
                    blocks.append(current_block)
                current_block = {'nodes': [child], 'purpose': self._infer_purpose(child)}
            else:
                current_block['nodes'].append(child)
        
        if current_block['nodes']:
            blocks.append(current_block)
        
        return blocks

    def _infer_purpose(self, node: ast.AST) -> str:
        """Infer the purpose of a code block"""
        if isinstance(node, ast.If):
            return 'validation'
        elif isinstance(node, ast.For):
            return 'processing'
        elif isinstance(node, ast.While):
            return 'iteration'
        return 'helper'

    def _create_helper_function(self, name: str, block: Dict[str, Any]) -> str:
        """Create a helper function from a code block"""
        # Implementation details...
        pass

    def _format_function_summary(self, blocks: List[Dict[str, Any]]) -> str:
        """Format a summary of function blocks"""
        return '\n'.join(
            f"- {block['purpose']}: {len(block['nodes'])} operations"
            for block in blocks
        )

    def _is_pure_function(self, call_info: Dict[str, Any]) -> bool:
        """Check if a function is pure (no side effects)"""
        # Implementation details...
        pass

    # ... additional helper methods ... 