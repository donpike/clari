import click
import asyncio
import yaml
from pathlib import Path
from typing import Optional
from .main import AutoCoder
from .utils.logger import logger
from .core.batch_processor import BatchProcessor

@click.group()
def cli():
    """CLI tool for automated code improvements"""
    pass

@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), 
              default='config/settings.yaml', help='Path to config file')
@click.option('--output', '-o', type=click.Path(), 
              help='Path to save improvements (default: print to console)')
def improve(file_path: str, config: str, output: Optional[str]):
    """Analyze and improve the given Python file"""
    try:
        # Load configuration
        with open(config, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Create AutoCoder instance
        auto_coder = AutoCoder(config_data)
        
        # Run the improvement
        result = asyncio.run(auto_coder.improve_code(Path(file_path)))
        
        # Format output
        output_text = format_result(result)
        
        # Handle output
        if output:
            Path(output).write_text(output_text)
            click.echo(f"Improvements saved to {output}")
        else:
            click.echo(output_text)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Scan directory recursively')
def scan(directory: str, recursive: bool):
    """Scan a directory for Python files and show potential improvements"""
    path = Path(directory)
    pattern = '**/*.py' if recursive else '*.py'
    
    for file in path.glob(pattern):
        click.echo(f"\nScanning {file}...")
        improve.callback(str(file), 'config/settings.yaml', None)

@cli.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--batch-size', '-b', default=5, help='Number of files to process in parallel')
@click.option('--priority', '-p', 
              type=click.Choice(['size', 'complexity', 'issues']), 
              help='How to prioritize files')
def batch(directory: str, batch_size: int, priority: str):
    """Process multiple files in batches"""
    try:
        # Load configuration
        with open('config/settings.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize batch processor
        processor = BatchProcessor(config)
        
        # Get all Python files
        files = list(Path(directory).rglob('*.py'))
        
        if priority:
            files = processor.prioritize_files(files, priority)
        
        # Process files
        results = asyncio.run(processor.process_batch(files, batch_size))
        
        # Display results
        for result in results:
            if result['status'] == 'success':
                click.echo(f"\nProcessed {result['file']}:")
                click.echo(format_result(result['analysis']))
            else:
                click.echo(f"\nError processing {result['file']}: {result['error']}")
                
    except Exception as e:
        logger.error(f"Batch processing error: {e}")
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()

def format_result(result: dict) -> str:
    """Format the improvement result for output"""
    lines = [
        f"Analysis Results for {result['file_path']}",
        "\nIssues Found:",
    ]
    
    for issue in result['analysis']['issues']:
        lines.append(f"- {issue['message']} (line {issue['line']})")
    
    metrics = result['analysis']['metrics']
    lines.extend([
        "\nCode Metrics:",
        f"- Functions: {metrics['num_functions']}",
        f"- Classes: {metrics['num_classes']}",
        f"- Long functions: {len(metrics['long_functions'])}",
        f"- Large classes: {len(metrics['large_classes'])}"
    ])
    
    lines.extend([
        "\nSuggested Improvements:",
        result['improvements']
    ])
    
    return '\n'.join(lines)

if __name__ == '__main__':
    cli() 