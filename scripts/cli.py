import click
import asyncio
import json
from pathlib import Path
from src.auto_coder import AutoCoder

@click.group()
def cli():
    """Semi-automated coding assistant using OpenRouter"""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for improvements')
def improve(file_path, output):
    """Analyze and improve a Python file"""
    async def run():
        auto_coder = AutoCoder()
        result = await auto_coder.improve_code(Path(file_path))
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2)
        else:
            click.echo(json.dumps(result, indent=2))
    
    asyncio.run(run())

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
def batch(directory):
    """Analyze and improve all Python files in a directory"""
    async def run():
        auto_coder = AutoCoder()
        results = {}
        
        for file_path in Path(directory).glob('**/*.py'):
            results[str(file_path)] = await auto_coder.improve_code(file_path)
            
        click.echo(json.dumps(results, indent=2))
    
    asyncio.run(run())

if __name__ == '__main__':
    cli() 