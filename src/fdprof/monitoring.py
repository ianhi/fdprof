"""
File descriptor monitoring functionality.
"""

import json
import select
import subprocess
import time
from typing import Callable, List, Optional

import psutil


def _get_fd_counter(psutil_proc: psutil.Process) -> Callable[[], int]:
    """Determine the best FD counting method for the current platform."""
    # Try methods in order of efficiency
    try:
        psutil_proc.num_fds()
        return lambda: psutil_proc.num_fds()
    except AttributeError:
        try:
            psutil_proc.num_handles()
            return lambda: psutil_proc.num_handles()
        except AttributeError:
            return lambda: len(psutil_proc.open_files())


def capture_output_and_monitor_fds(
    proc: subprocess.Popen,
    psutil_proc: Optional[psutil.Process],
    log_file: str,
    start_time: float,
    interval: float = 0.1,
) -> List[str]:
    """Capture process output and monitor FD usage simultaneously."""
    output_lines = []

    # Determine the FD counting method once at startup
    get_fd_count = None
    if psutil_proc:
        try:
            get_fd_count = _get_fd_counter(psutil_proc)
        except Exception:
            get_fd_count = None

    with open(log_file, "w") as f:
        while proc.poll() is None:
            # Monitor FD usage
            try:
                current_time = time.time()
                if get_fd_count:
                    try:
                        fd_count = get_fd_count()
                    except (psutil.AccessDenied, psutil.NoSuchProcess):
                        fd_count = -1
                else:
                    fd_count = -1

                fd_data = {
                    "timestamp": current_time,
                    "elapsed": current_time - start_time,
                    "open_fds": fd_count,
                }

                f.write(json.dumps(fd_data) + "\n")
                f.flush()
            except Exception:
                pass

            # Capture output
            try:
                ready, _, _ = select.select([proc.stdout], [], [], interval)
                if ready:
                    line = proc.stdout.readline()
                    if line:
                        line_stripped = line.strip()
                        output_lines.append(line_stripped)
                        print(line_stripped, flush=True)
            except Exception:
                pass

    # Capture any remaining output
    remaining = proc.stdout.read()
    if remaining:
        for line in remaining.strip().split("\n"):
            if line:
                output_lines.append(line)
                print(line, flush=True)

    return output_lines
