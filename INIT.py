
from rich.console import Console
from rich.traceback import install
from tabulate import tabulate
import sys

# Instalar o traceback personalizado do Rich
install(show_locals=False)
console = Console()


def log_error_with_locals(exception: Exception, locals_data):
    console.print("An error occurred:", style="bold red")
    traceback_table = tabulate(
        locals_data.items(), headers=["Variable", "Value"], tablefmt="grid"
    )
    #console.print(traceback_table)
    console.print_exception()


def customTry(func):
    """Decorator to wrap a function with a try-except block."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_error_with_locals(e, sys._getframe(1).f_locals)
            return None

    return wrapper
