import ast
import sys
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import importlib.util
from ..utils.logger import logger
from ..utils.dependency_checker import DependencyChecker
import platform

class SafetyChecker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backup_dir = Path(config['safety']['backup_dir'])
        self.max_changes = config['safety']['max_changes_per_file']
        self.safety_level = config['safety']['safety_level']
        self.unsafe_patterns = [
            'os.system',
            'subprocess.call',
            'eval(',
            'exec(',
            '__import__',
            'globals()',
            'locals()',
        ]
        self.excluded_dirs = {
            'venv',
            '.git',
            '__pycache__',
            'node_modules',
            'build',
            'dist'
        }

    async def pre_check(self, file_path: Path) -> Dict[str, Any]:
        """Run safety checks before modifying a file"""
        try:
            # Check if file exists
            if not file_path.exists():
                return {
                    'is_safe': False,
                    'issues': ['File does not exist']
                }
            
            # Check file size
            if file_path.stat().st_size > self.config['analysis']['max_file_size']:
                return {
                    'is_safe': False,
                    'issues': ['File too large']
                }
            
            # Parse and check syntax
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError:
                return {
                    'is_safe': False,
                    'issues': ['Invalid Python syntax']
                }
            
            return {
                'is_safe': True,
                'issues': []
            }
            
        except Exception as e:
            logger.error(f"Safety check error: {str(e)}")
            return {
                'is_safe': False,
                'issues': [str(e)]
            }
    
    async def analyze_changes(self, 
                            file_path: Path, 
                            new_code: str) -> Dict[str, Any]:
        """Comprehensive analysis of proposed changes"""
        results = {}
        
        # Run checks in parallel
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(self._check_syntax, new_code),
                executor.submit(self._check_imports, new_code),
                executor.submit(self._run_pylint, new_code),
                executor.submit(self._check_complexity, new_code),
                executor.submit(self._check_type_safety, new_code)
            ]
            
            # Collect results
            results['syntax'] = futures[0].result()
            results['imports'] = futures[1].result()
            results['lint'] = futures[2].result()
            results['complexity'] = futures[3].result()
            results['types'] = futures[4].result()
        
        # Run tests if available
        results['tests'] = await self._run_tests(file_path, new_code)
        
        return results
    
    async def verify_changes(self, file_path: Path) -> bool:
        """Verify file after changes"""
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                "module", file_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Run module's tests if available
            test_result = await self._run_module_tests(file_path)
            
            return test_result.get('success', True)
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    async def create_backup(self, file_path: Path) -> Path:
        """Create a secure backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.stem}_{timestamp}.bak"
        
        # Create backup with original permissions
        backup_path.write_text(file_path.read_text())
        backup_path.chmod(file_path.stat().st_mode)
        
        return backup_path
    
    async def restore_backup(self, backup_path: Path, target_path: Path):
        """Safely restore from backup"""
        if not backup_path.exists():
            raise FileNotFoundError("Backup file not found")
            
        # Verify backup integrity
        if not self._verify_backup_integrity(backup_path):
            raise ValueError("Backup integrity check failed")
            
        # Restore with original permissions
        target_path.write_text(backup_path.read_text())
        target_path.chmod(backup_path.stat().st_mode)
    
    def _check_complexity(self, code: str) -> Dict[str, Any]:
        """Check code complexity"""
        tree = ast.parse(code)
        complexity = {
            'max_depth': 0,
            'max_line_length': 0,
            'cognitive_complexity': 0
        }
        
        # Analyze complexity
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While)):
                depth = self._get_nesting_depth(node)
                complexity['max_depth'] = max(
                    complexity['max_depth'], 
                    depth
                )
                
            complexity['cognitive_complexity'] += self._get_cognitive_complexity(node)
        
        # Check against thresholds
        passed = (
            complexity['max_depth'] <= self.config['safety']['max_depth'] and
            complexity['cognitive_complexity'] <= self.config['safety']['max_complexity']
        )
        
        return {
            'passed': passed,
            'details': complexity,
            'message': "Complexity within acceptable limits" if passed else
                      "Code may be too complex"
        }
    
    async def check_project(self, project_path: Path) -> List[Dict[str, Any]]:
        """Check project for potential safety issues"""
        issues = []
        
        try:
            # Check all Python files in the project, excluding venv and other special directories
            for file_path in project_path.rglob('*.py'):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in self.excluded_dirs):
                    continue
                    
                file_issues = await self._check_file(file_path)
                if file_issues:
                    issues.extend(file_issues)
            
            logger.info(f"Safety check completed. Found {len(issues)} potential issues.")
            return issues
            
        except Exception as e:
            logger.error(f"Error during safety check: {str(e)}")
            return [{'type': 'error', 'message': f"Safety check failed: {str(e)}"}]
    
    async def _check_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Check a single file for safety issues"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse the file
            tree = ast.parse(content)
            
            # Check for unsafe patterns
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check function calls
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if any(pattern in func_name for pattern in self.unsafe_patterns):
                            issues.append({
                                'file': str(file_path),
                                'line': node.lineno,
                                'type': 'unsafe_call',
                                'message': f'Potentially unsafe function call: {func_name}'
                            })
                    
                    # Check attribute calls (like os.system)
                    elif isinstance(node.func, ast.Attribute):
                        call = f"{node.func.value.id}.{node.func.attr}" if hasattr(node.func.value, 'id') else node.func.attr
                        if any(pattern in call for pattern in self.unsafe_patterns):
                            issues.append({
                                'file': str(file_path),
                                'line': node.lineno,
                                'type': 'unsafe_call',
                                'message': f'Potentially unsafe function call: {call}'
                            })
            
            # Only check file permissions on Unix-like systems
            if platform.system() != 'Windows':
                self._check_file_permissions(file_path, issues)
            
        except Exception as e:
            issues.append({
                'file': str(file_path),
                'type': 'error',
                'message': f"Error analyzing file: {str(e)}"
            })
            
        return issues
    
    def _check_file_permissions(self, file_path: Path, issues: List[Dict[str, Any]]):
        """Check file permissions for potential security issues"""
        try:
            import stat
            st = file_path.stat()
            
            # Check if file is world-writable on Unix systems
            if st.st_mode & stat.S_IWOTH:
                issues.append({
                    'file': str(file_path),
                    'type': 'permission',
                    'message': 'File is world-writable, which may be a security risk'
                })
        except Exception as e:
            logger.warning(f"Could not check file permissions for {file_path}: {e}")

    # ... additional helper methods ... 