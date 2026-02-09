"""Booking Bot Command Line Interface."""

from rich.console import Console
from typer import Option, Typer

from aimharder_book_bot import __version__
from aimharder_book_bot.main import run_bot

app = Typer()
console = Console(tab_size=4)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main_callback(version: bool = Option(False, help="Show the package version.")):
    """Dbt2Pdf command line interface."""
    if version:
        console.print(f"dbt2pdf, version {__version__}")


@app.command()
def run():
    """Run the booking bot."""
    run_bot()


if __name__ == "__main__":
    run()
