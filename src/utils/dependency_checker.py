import ast
from importlib import metadata
import importlib
import subprocess
import sysconfig
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
import sys
from .logger import logger

class DependencyChecker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.installed_packages = self._get_installed_packages()
        self.stdlib_modules = self._get_stdlib_modules()
        
    def check_dependencies(self, file_path: Path) -> Dict[str, Any]:
        """Check all dependencies for a file"""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            
            # Parse the code
            tree = ast.parse(code)
            
            # Get all imports
            imports = self._extract_imports(tree)
            
            # Analyze dependencies
            results = {
                'missing_packages': [],
                'unused_imports': [],
                'stdlib_imports': [],
                'third_party_imports': [],
                'local_imports': [],
                'requirements': set()
            }
            
            # Check each import
            for imp in imports:
                self._analyze_import(imp, results, file_path)
            
            # Check for unused imports
            used_names = self._get_used_names(tree)
            results['unused_imports'] = self._find_unused_imports(
                imports, used_names
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
            return {'error': str(e)}

    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all imports from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({
                        'module': name.name,
                        'alias': name.asname,
                        'line': node.lineno,
                        'type': 'import'
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for name in node.names:
                    imports.append({
                        'module': f"{module}.{name.name}" if module else name.name,
                        'alias': name.asname,
                        'line': node.lineno,
                        'type': 'from'
                    })
        
        return imports

    def _analyze_import(self, 
                       import_info: Dict[str, Any], 
                       results: Dict[str, Any],
                       file_path: Path):
        """Analyze a single import"""
        module_name = import_info['module'].split('.')[0]
        
        if module_name in self.stdlib_modules:
            results['stdlib_imports'].append(import_info)
            
        elif self._is_local_import(module_name, file_path):
            results['local_imports'].append(import_info)
            
        else:
            # Check if it's installed
            package_name = self._get_package_name(module_name)
            if package_name:
                results['third_party_imports'].append(import_info)
                results['requirements'].add(package_name)
            else:
                results['missing_packages'].append(module_name)

    def _get_installed_packages(self) -> Dict[str, str]:
        """Get all installed Python packages"""
        try:
            # Use importlib.metadata instead of pkg_resources
            return {
                dist.metadata['Name']: dist.version
                for dist in metadata.distributions()
            }
        except Exception as e:
            logger.error(f"Error getting installed packages: {e}")
            return {}

    def _get_stdlib_modules(self) -> Set[str]:
        """Get all Python standard library modules"""
        stdlib_path = sysconfig.get_path('stdlib')
        modules = set()
        
        # Add all stdlib modules
        for path in Path(stdlib_path).rglob('*.py'):
            module = path.stem
            if module != '__init__':
                modules.add(module)
        
        # Add built-in modules
        modules.update(sys.builtin_module_names)
        
        return modules

    def _is_local_import(self, module_name: str, file_path: Path) -> bool:
        """Check if import is a local module"""
        possible_paths = [
            file_path.parent / f"{module_name}.py",
            file_path.parent / module_name / "__init__.py"
        ]
        return any(path.exists() for path in possible_paths)

    def _get_package_name(self, module_name: str) -> str:
        """Get package name for a module"""
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, '__file__'):
                path = Path(module.__file__)
                site_packages = Path(self.installed_packages.__file__).parent.parent
                if site_packages in path.parents:
                    return module_name
        except ImportError:
            pass
        return None

    def _get_used_names(self, tree: ast.AST) -> Set[str]:
        """Get all used names in the code"""
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                used_names.add(node.attr)
        
        return used_names

    def _find_unused_imports(self, 
                           imports: List[Dict[str, Any]], 
                           used_names: Set[str]) -> List[Dict[str, Any]]:
        """Find imports that are not used"""
        unused = []
        
        for imp in imports:
            name = imp['alias'] or imp['module'].split('.')[-1]
            if name not in used_names:
                unused.append(imp)
        
        return unused

    def generate_requirements(self, results: Dict[str, Any]) -> str:
        """Generate requirements.txt content"""
        requirements = []
        
        for package in results['requirements']:
            if package in self.installed_packages:
                version = self.installed_packages[package]
                requirements.append(f"{package}=={version}")
        
        return '\n'.join(sorted(requirements)) 

    @staticmethod
    def check_package_version(package_name: str) -> str:
        try:
            return metadata.version(package_name)
        except Exception as e:
            return None 