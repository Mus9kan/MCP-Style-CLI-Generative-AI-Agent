"""Rich terminal output formatting for CLI AI Agent."""

from typing import Optional, List, Dict, Any, Generator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich import box

console = Console()


class Formatter:
    """Professional terminal output formatter using Rich."""

    @staticmethod
    def print_header(title: str, subtitle: Optional[str] = None) -> None:
        """Print a styled header."""
        header_text = Text(title, style="bold blue", justify="center")
        if subtitle:
            header_text.append(f"\n{subtitle}", style="dim")
        
        panel = Panel(
            header_text,
            box=box.DOUBLE,
            border_style="blue",
            padding=(1, 2),
        )
        console.print(panel)

    @staticmethod
    def print_section(title: str) -> None:
        """Print a section divider with title."""
        console.print(f"\n[bold cyan]▶ {title}[/bold cyan]")
        console.print("[dim]" + "─" * 60 + "[/dim]")

    @staticmethod
    def print_success(message: str) -> None:
        """Print success message."""
        console.print(f"[green]✓[/green] {message}")

    @staticmethod
    def print_error(message: str, title: str = "Error") -> None:
        """Print error message."""
        panel = Panel(
            f"[bold red]{title}[/bold red]\n{message}",
            box=box.ROUNDED,
            border_style="red",
        )
        console.print(panel)

    @staticmethod
    def print_warning(message: str) -> None:
        """Print warning message."""
        console.print(f"[yellow]⚠ {message}[/yellow]")

    @staticmethod
    def print_info(message: str) -> None:
        """Print info message."""
        console.print(f"[blue]ℹ {message}[/blue]")

    @staticmethod
    def print_data(data: Dict[str, Any], title: str = "Data") -> None:
        """Print structured data as a table."""
        table = Table(
            title=title,
            box=box.ROUNDED,
            border_style="blue",
            show_header=True,
        )
        
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        
        for key, value in data.items():
            table.add_row(str(key), str(value))
        
        console.print(table)

    @staticmethod
    def print_code(code: str, language: str = "python", title: Optional[str] = None) -> None:
        """Print syntax-highlighted code."""
        syntax = Syntax(
            code,
            language,
            theme="monokai",
            line_numbers=True,
            word_wrap=True,
        )
        
        if title:
            panel = Panel(
                syntax,
                title=title,
                border_style="green",
                box=box.ROUNDED,
            )
            console.print(panel)
        else:
            console.print(syntax)

    @staticmethod
    def print_markdown(content: str) -> None:
        """Print formatted markdown."""
        md = Markdown(content)
        console.print(md)

    @staticmethod
    def print_debug_report(problem: str, root_cause: str, suggested_fix: str) -> None:
        """Print structured debug report."""
        content = f"""[bold red]Problem:[/bold red]
{problem}

[bold yellow]Root Cause:[/bold yellow]
{root_cause}

[bold green]Suggested Fix:[/bold green]
{suggested_fix}
"""
        panel = Panel(
            content,
            title="[bold]Debug Analysis[/bold]",
            border_style="yellow",
            box=box.ROUNDED,
        )
        console.print(panel)

    @staticmethod
    def context_manager(description: str = "Processing"):
        """Context manager for loading spinner."""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ).add_task(description, total=None)

    @staticmethod
    def print_result(result: str, title: str = "Result") -> None:
        """Print final result."""
        panel = Panel(
            result,
            title=f"[bold green]{title}[/bold green]",
            border_style="green",
            box=box.ROUNDED,
        )
        console.print(panel)

    @staticmethod
    def print_tool_execution(tool_name: str, parameters: Dict[str, Any]) -> None:
        """Print tool execution info."""
        params_str = ", ".join(f"{k}={v}" for k, v in parameters.items())
        console.print(f"[dim]🔧 Executing tool: {tool_name}({params_str})[/dim]")

    @staticmethod
    def print_streaming(text_generator: Generator[str, None, None], prefix: str = "", title: str = "Streaming Response") -> str:
        """
        Print streaming text with real-time updates.
        
        Args:
            text_generator: Generator yielding text chunks
            prefix: Text to show before streamed content
            title: Panel title
            
        Returns:
            Complete streamed text
        """
        full_text = prefix
        
        # Use Rich Live display for real-time updates
        with Live(
            Panel(
                Text(full_text + "▌", style="green"),  # Cursor effect
                title=f"[bold green]{title}[/bold green]",
                border_style="green",
                box=box.ROUNDED,
            ),
            console=console,
            refresh_per_second=10,  # Update 10 times per second
            transient=False,
        ) as live:
            for chunk in text_generator:
                if chunk:
                    full_text += chunk
                    # Update with new chunk and blinking cursor
                    live.update(
                        Panel(
                            Text(full_text + "▌", style="green"),
                            title=f"[bold green]{title}[/bold green]",
                            border_style="green",
                            box=box.ROUNDED,
                        )
                    )
        
        # Print final result without cursor
        print_result(full_text, title=title)
        
        return full_text


# Convenience functions
print_header = Formatter.print_header
print_section = Formatter.print_section
print_success = Formatter.print_success
print_error = Formatter.print_error
print_warning = Formatter.print_warning
print_info = Formatter.print_info
print_data = Formatter.print_data
print_code = Formatter.print_code
print_markdown = Formatter.print_markdown
print_debug_report = Formatter.print_debug_report
print_result = Formatter.print_result
print_tool_execution = Formatter.print_tool_execution
print_streaming = Formatter.print_streaming
