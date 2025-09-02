"""
File descriptor monitoring functionality.
"""

import json
import select
import subprocess
import time
from typing import List, Optional

import psutil


def capture_output_and_monitor_fds(
    proc: subprocess.Popen,
    psutil_proc: Optional[psutil.Process],
    log_file: str,
    start_time: float,
    interval: float = 0.1,
) -> List[str]:
    """Capture process output and monitor FD usage simultaneously."""
    output_lines = []

    with open(log_file, "w") as f:
        while proc.poll() is None:
            # Monitor FD usage
            try:
                current_time = time.time()
                fd_count = psutil_proc.num_fds() if psutil_proc else -1

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
