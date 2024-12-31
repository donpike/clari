# Clari

An AI-powered code improvement tool that helps analyze and enhance Python code.

## Installation

# Basic installation (just the core features):
pip install .

# For code quality features (recommended for most users):
pip install .[quality]
# This adds:
# - mypy (type checking)
# - pylint (code quality analysis)

# For development (if you want to contribute or modify the tool):
pip install .[dev]
# This adds:
# - pytest (testing)
# - black (code formatting)
# - isort (import sorting)
# - flake8 (linting)]

## Features

- Code analysis and improvement suggestions
- Pattern detection and learning
- Safety checks and backups
- Interactive CLI interface
- Project-wide improvements

## Usage

bash
Analyze a single file
clari improve file.py
Analyze a project
clari improve-project ./my_project
Interactive mode
clari interactive


## Optional Features

- Type checking (requires mypy)
- Code quality analysis (requires pylint)
- Development tools (black, isort, flake8)

## License

MIT