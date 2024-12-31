from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
import ast
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@dataclass
class SimpleImprovement:
    """Represents a simple code improvement that can be applied automatically."""
    type: str
    line: int
    message: str
    node_type: str
    name: str = ''
    function: str = ''
    argument: str = ''

class CodeModifier:
    """Handles simple code modifications using AST for safe transformations."""
    def __init__(self):
        """Initialize the code modifier."""
        self.changes: List[Dict[str, Any]] = []
        logger.debug("CodeModifier initialized")

    def can_handle_automatically(self, issue: Dict[str, Any]) -> bool:
        """Determine if an issue can be fixed automatically without AI."""
        can_handle = self._is_simple_fix(issue)
        logger.debug(f"Can handle issue automatically: {can_handle} for issue type: {issue.get('type')}")
        return can_handle

    def _is_simple_fix(self, issue: Dict[str, Any]) -> bool:
        """Check if an issue can be fixed automatically."""
        simple_fixes = {
            'missing_docstring',
            'unused_import',
            'missing_type_hint',
            'missing_return_type',
            'inconsistent_return',
            'redundant_parentheses'
        }
        is_simple = issue.get('type') in simple_fixes
        logger.debug(f"Is simple fix: {is_simple} for issue type: {issue.get('type')}")
        return is_simple

    def modify_file(self, file_path: Path, issues: List[Dict]) -> Dict[str, Any]:
        """Modify a file to fix issues."""
        logger.debug(f"Starting file modification for {file_path}")
        logger.debug(f"Issues to fix: {issues}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"File content loaded, length: {len(content)}")

            content_lines = content.splitlines()
            modified_lines = set()
            improvements = []

            for issue in issues:
                logger.debug(f"Processing issue: {issue}")
                if issue['line'] in modified_lines:
                    logger.debug(f"Skipping line {issue['line']} - already modified")
                    continue

                if issue['type'] == 'missing_docstring':
                    logger.debug(f"Attempting to add docstring at line {issue['line']}")
                    if self._add_docstring(content_lines, issue):
                        modified_lines.add(issue['line'])
                        improvements.append({
                            'type': 'docstring_added',
                            'line': issue['line'],
                            'message': 'Added docstring'
                        })
                        logger.debug(f"Successfully added docstring at line {issue['line']}")
                    else:
                        logger.debug(f"Failed to add docstring at line {issue['line']}")

                elif issue['type'] == 'missing_type_hint':
                    logger.debug(f"Attempting to add type hint at line {issue['line']}")
                    if self._add_type_hint(content_lines, issue):
                        modified_lines.add(issue['line'])
                        improvements.append({
                            'type': 'type_hint_added',
                            'line': issue['line'],
                            'message': 'Added type hint'
                        })
                        logger.debug(f"Successfully added type hint at line {issue['line']}")
                    else:
                        logger.debug(f"Failed to add type hint at line {issue['line']}")

            if improvements:
                logger.debug(f"Writing changes back to file. Improvements: {improvements}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(content_lines))
                logger.debug("File successfully updated")

            result = {
                'status': 'success',
                'changes': improvements
            }
            logger.debug(f"Modification complete. Result: {result}")
            return result

        except Exception as e:
            logger.error(f"Error modifying file: {e}", exc_info=True)
            return {
                'status': 'error',
                'message': str(e)
            }

    def _add_docstring(self, lines: List[str], issue: Dict) -> bool:
        """Add a docstring to a function or class."""
        logger.debug(f"Adding docstring for issue: {issue}")
        line_num = issue['line'] - 1
        
        # Check for existing docstring
        if any('"""' in line for line in lines[line_num:line_num + 2]):
            logger.debug("Docstring already exists, skipping")
            return False
            
        # Determine indentation
        current_line = lines[line_num]
        indentation = len(current_line) - len(current_line.lstrip())
        indent = ' ' * indentation
        
        # Create appropriate docstring
        if issue.get('node_type') == 'ClassDef':
            docstring = f'{indent}    """Class for handling {issue.get("name", "unknown")} functionality."""'
        else:
            docstring = f'{indent}    """Add description here."""'
        
        logger.debug(f"Inserting docstring: {docstring}")
        lines.insert(line_num + 1, docstring)
        return True

    def _add_type_hint(self, lines: List[str], issue: Dict) -> bool:
        """Add type hints to function parameters."""
        logger.debug(f"Adding type hint for issue: {issue}")
        line_num = issue['line'] - 1
        
        if '->' in lines[line_num]:
            logger.debug("Type hint already exists, skipping")
            return False

        func_line = lines[line_num]
        if 'def' in func_line:
            logger.debug(f"Original line: {func_line}")
            func_line = func_line.replace(')', ') -> None')
            lines[line_num] = func_line
            logger.debug(f"Modified line: {func_line}")
            return True

        return False

    def _create_simple_fix(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Create a simple fix for an issue."""
        issue_type = issue.get('type')
        
        if issue_type == 'missing_docstring':
            return {
                'type': 'docstring_added',
                'line': issue['line'],
                'message': 'Added docstring'
            }
        elif issue_type == 'missing_type_hint':
            return {
                'type': 'type_hint_added',
                'line': issue['line'],
                'message': 'Added type hint'
            }
        return None
