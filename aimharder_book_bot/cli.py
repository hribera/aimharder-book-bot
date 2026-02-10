#
# AimHarder Booking Bot
# Author: Helena Ribera <heleribera@gmail.com>
# Website: www.hriberaponsa.com
#
"""AimHarder Booking Bot CLI."""

from typing import Annotated

from rich.console import Console
from typer import Option, Typer

from aimharder_book_bot import __version__
from aimharder_book_bot.main import run_bot

app = Typer()
console = Console(tab_size=4)


@app.callback(invoke_without_command=True, no_args_is_help=True)
def main_callback(version: bool = Option(False, help="Show the package version.")):
    """AimHarder Booking Bot command line interface."""
    if version:
        console.print(f"AimHarder Booking Bot, version {__version__}")


@app.command()
def run(
    user: Annotated[str, Option("--user", help="Name of the user to book the classes")],
):
    """Run the booking bot."""
    run_bot(user=user)


if __name__ == "__main__":
    run()
