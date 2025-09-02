"""
File descriptor profiler for monitoring FD usage and detecting events.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "File descriptor profiler that monitors FD usage and captures timestamped events"

from .core import main


def cli_main():
    """Entry point for the fdprof command-line tool."""
    main()

__all__ = ["main"]
