from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clari",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered code improvement tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/clari",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich>=10.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        'quality': [
            'mypy>=1.0.0',
            'pylint>=2.17.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'black>=22.0.0',
            'isort>=5.0.0',
            'flake8>=4.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'clari=clari.cli:main',
        ],
    },
) 