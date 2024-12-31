import click
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.panel import Panel
from difflib import unified_diff
from ..core.improvement_tracker import ImprovementTracker
from ..core.safety import SafetyChecker
from ..learning.project_learner import ProjectLearner
from ..main import AutoCoder

console = Console()

class InteractiveCLI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.auto_coder = AutoCoder(config)
        self.tracker = ImprovementTracker(config)
        self.safety = SafetyChecker(config)
        self.learning_data = self._load_learning_data()

    def start(self):
        """Start the interactive CLI session"""
        console.print("[bold blue]Welcome to AutoCoder Interactive![/]")
        
        while True:
            self._show_menu()
            choice = click.prompt(
                "Choose an option", 
                type=click.Choice(['1', '2', '3', '4', '5', 'q'])
            )
            
            if choice == 'q':
                break
                
            options = {
                '1': self._analyze_file,
                '2': self._analyze_project,
                '3': self._show_learning_stats,
                '4': self._configure_settings,
                '5': self._show_improvement_history
            }
            
            options[choice]()

    async def _analyze_file(self):
        """Analyze and improve a single file with enhanced interaction"""
        file_path = click.prompt("Enter file path", type=click.Path(exists=True))
        path = Path(file_path)
        
        # Show file preview
        console.print("\n[bold]Current file:[/]")
        syntax = Syntax(path.read_text(), "python", theme="monokai")
        console.print(Panel(syntax, title=str(path)))
        
        with Progress(SpinnerColumn(), *Progress.get_default_columns()) as progress:
            task = progress.add_task("Analyzing...", total=None)
            
            # Get project patterns
            project_patterns = self.learning_data.get_project_patterns(path)
            
            # First, run safety checks
            safety_result = await self.safety.pre_check(path)
            if not safety_result['is_safe']:
                console.print("[bold red]Safety Check Failed:[/]")
                for issue in safety_result['issues']:
                    console.print(f"- {issue}")
                if not Confirm.ask("Continue anyway?"):
                    return
            
            # Analyze with learned patterns
            result = await self.auto_coder.improve_code(path, project_patterns)
            progress.update(task, completed=True)
        
        # Show improvements with diff
        if result['status'] == 'success':
            console.print("\n[bold green]Suggested Improvements:[/]")
            diff = unified_diff(
                path.read_text().splitlines(),
                result['improvements'].splitlines(),
                fromfile="Original",
                tofile="Improved"
            )
            console.print("\n".join(diff))
            
            # Show safety analysis
            safety_analysis = await self.safety.analyze_changes(
                path, 
                result['improvements']
            )
            self._show_safety_analysis(safety_analysis)
            
            # Interactive improvement application
            if Confirm.ask("Apply these improvements?"):
                backup_path = await self.safety.create_backup(path)
                console.print(f"[green]Backup created at: {backup_path}[/]")
                
                try:
                    path.write_text(result['improvements'])
                    console.print("[green]Improvements applied successfully![/]")
                    
                    # Verify after changes
                    if not await self.safety.verify_changes(path):
                        if Confirm.ask("Changes may have issues. Restore backup?"):
                            await self.safety.restore_backup(backup_path, path)
                            console.print("[yellow]Restored from backup[/]")
                            return
                except Exception as e:
                    console.print(f"[red]Error applying changes: {e}[/]")
                    await self.safety.restore_backup(backup_path, path)
                    return
            
            # Learn from the improvement
            feedback = Prompt.ask(
                "How would you rate this improvement?",
                choices=["helpful", "partially_helpful", "not_helpful"]
            )
            self.learning_data.record_improvement_feedback(
                result['pattern_type'],
                file_path,
                feedback
            )
            
            # Additional context
            if feedback in ["helpful", "partially_helpful"]:
                context = Prompt.ask(
                    "Any specific context about why this was helpful?",
                    default=""
                )
                if context:
                    self.learning_data.record_improvement_context(
                        result['pattern_type'],
                        context
                    )

    def _show_safety_analysis(self, analysis: Dict[str, Any]):
        """Show detailed safety analysis"""
        table = Table(title="Safety Analysis")
        table.add_column("Check", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Details", style="yellow")
        
        for check, details in analysis.items():
            status = "✓" if details['passed'] else "✗"
            table.add_row(
                check,
                status,
                details.get('message', '')
            )
        
        console.print(table)

    async def _analyze_project(self):
        """Analyze entire project with learning"""
        project_path = click.prompt("Enter project root", type=click.Path(exists=True))
        
        # Get all Python files
        files = list(Path(project_path).rglob("*.py"))
        
        with Progress() as progress:
            task = progress.add_task("Analyzing project...", total=len(files))
            
            for file in files:
                # Get learned patterns for this file's context
                patterns = self.learning_data.get_context_patterns(file)
                
                # Analyze with context
                result = await self.auto_coder.improve_code(file, patterns)
                
                # Learn from results
                self.learning_data.update_project_knowledge(file, result)
                
                progress.update(task, advance=1)

    def _show_learning_stats(self):
        """Show what the system has learned"""
        stats = self.learning_data.get_learning_stats()
        
        table = Table(title="Learning Statistics")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right", style="green")
        table.add_column("Success Rate", justify="right", style="yellow")
        
        for category, data in stats.items():
            table.add_row(
                category,
                str(data['count']),
                f"{data['success_rate']:.1f}%"
            )
        
        console.print(table)

    def _configure_settings(self):
        """Configure AutoCoder settings"""
        # Show current settings
        self._show_current_settings()
        
        # Allow updating settings
        if Confirm.ask("Would you like to update any settings?"):
            self._update_settings()

    def _show_improvement_history(self):
        """Show history of improvements"""
        history = self.tracker.get_improvement_stats()
        
        table = Table(title="Improvement History")
        table.add_column("Date", style="cyan")
        table.add_column("File", style="blue")
        table.add_column("Pattern", style="green")
        table.add_column("Success", style="yellow")
        
        for entry in history['recent_improvements']:
            table.add_row(
                entry['date'],
                entry['file'],
                entry['pattern'],
                "✓" if entry['success'] else "✗"
            )
        
        console.print(table) 