#!/usr/bin/env python3
"""
File descriptor profiler that monitors FD usage and captures timestamped events.

Usage: fdprof [--plot] [--interval SECONDS] <command> [args...]

Options:
    --plot              Show plot after command completes
    --interval SECONDS  Sampling interval in seconds (default: 0.1)

In your code, use a log_event function like:
    def log_event(message: str):
        print(f"EVENT: {time.time():.9f} {message}")
"""

import subprocess
import sys
import time
from typing import Any, Dict, List

import psutil

from .events import parse_events
from .monitoring import capture_output_and_monitor_fds
from .plotting import create_plot


def parse_args() -> tuple[bool, float, List[str]]:
    """Parse command line arguments."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    show_plot = False
    interval = 0.1
    i = 1

    # Parse options
    while i < len(sys.argv) and sys.argv[i].startswith("--"):
        if sys.argv[i] == "--plot":
            show_plot = True
            i += 1
        elif sys.argv[i] == "--interval":
            if i + 1 >= len(sys.argv):
                print("Error: --interval requires a value")
                sys.exit(1)
            try:
                interval = float(sys.argv[i + 1])
                if interval <= 0:
                    print("Error: interval must be positive")
                    sys.exit(1)
            except ValueError:
                print("Error: interval must be a number")
                sys.exit(1)
            i += 2
        elif sys.argv[i] in ("--help", "-h"):
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Error: unknown option {sys.argv[i]}")
            sys.exit(1)

    command = sys.argv[i:]
    if not command:
        print("Error: No command specified")
        sys.exit(1)

    return show_plot, interval, command


def print_summary(events: List[Dict[str, Any]], return_code: int) -> None:
    """Print execution summary."""
    print("-" * 40)
    print(f"Command completed with exit code: {return_code}")
    print(f"Found {len(events)} events")

    if events:
        print("\nEvent Timeline:")
        for event in events:
            print(f"  {event['elapsed']:6.2f}s: {event['message']}")


def main() -> None:
    """Main execution function."""
    show_plot, interval, command = parse_args()
    log_file = "fdprof.jsonl"

    print(f"Command: {' '.join(command)}")
    print(f"Logging to: {log_file}")
    print(f"Sampling interval: {interval}s")
    print("-" * 40)

    # Start the process
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    # Get psutil process handle
    try:
        psutil_proc = psutil.Process(proc.pid)
    except Exception:
        print("Warning: psutil not available")
        psutil_proc = None

    start_time = time.time()

    # Capture output and monitor FDs simultaneously
    output_lines = capture_output_and_monitor_fds(
        proc, psutil_proc, log_file, start_time, interval
    )

    # Wait for process completion
    return_code = proc.wait()

    # Parse events from captured output
    events = parse_events(output_lines, start_time)

    # Print summary
    print_summary(events, return_code)

    # Create plot if requested
    if show_plot:
        create_plot(log_file, events)


if __name__ == "__main__":
    main()
