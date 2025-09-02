# fdprof

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful file descriptor profiler that monitors FD usage and captures timestamped events in real-time. Perfect for debugging resource leaks, understanding application behavior, and performance analysis.

**🎯 Focus**: fdprof is designed for **whole-process monitoring** from the outside. It wraps any command without requiring code changes. See our [Mission Statement](MISSION.md) for design philosophy and scope.

## ✨ Features

- 📈 **Real-time FD monitoring** - Track file descriptor usage throughout command execution
- 🎯 **Event logging** - Capture timestamped events from your application output
- 📊 **Visual analysis** - Generate matplotlib plots with plateau detection and jump analysis
- 🔍 **Intelligent analysis** - Automatic detection of stable plateaus and significant jumps
- ⚙️ **Configurable** - Customizable sampling intervals and detection parameters
- 🚀 **Easy installation** - Install as a uvx tool for instant use

## 🚀 Installation

### Option 1: uv tool (Recommended)
Install as a persistent tool with uv:

```bash
# Install from PyPI (when published)
uv tool install fdprof

# Install from GitHub repository
uv tool install git+https://github.com/ianhi/fdprof

# Run without installing (temporary)
uvx fdprof <command> [args...]
```

### Option 2: pip install
```bash
pip install fdprof
```

### Option 3: Development install
```bash
git clone https://github.com/ianhi/fdprof
cd fdprof
uv sync --extra dev
```

### Verify Installation
```bash
# Check if fdprof is installed
fdprof --help

# Test with a simple command
fdprof echo "Hello World"
```

## 📖 Usage

### Basic Command Line Interface

```bash
fdprof [OPTIONS] <command> [command_args...]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--plot` | Show interactive plot after command completes | `False` |
| `--interval SECONDS` | Sampling interval in seconds | `0.1` |

### Quick Examples

```bash
# Basic monitoring
fdprof python my_script.py

# With visualization
fdprof --plot python my_script.py

# Custom sampling rate (every 0.05 seconds)
fdprof --interval 0.05 --plot python my_script.py

# Monitor a web server startup
fdprof --plot gunicorn app:app

# Profile a database migration
fdprof --plot python manage.py migrate
```

## 🎯 Event Logging

Add event logging to your applications to track important milestones:

### Python Example

```python
import time

def log_event(message: str):
    """Log a timestamped event that fdprof will capture"""
    print(f"EVENT: {time.time():.9f} {message}")

# Example application with events
log_event("Application startup")

# Open database connections
db_connections = []
for i in range(5):
    conn = create_db_connection()
    db_connections.append(conn)
    log_event(f"Database connection {i+1} established")

log_event("All connections ready")

# Your application logic here
process_data()

log_event("Processing complete")

# Cleanup
for conn in db_connections:
    conn.close()
log_event("All connections closed")
```

### Shell Script Example

```bash
#!/bin/bash
echo "EVENT: $(date +%s.%N) Script started"

# Open some files
for i in {1..3}; do
    exec {fd}< /etc/passwd
    echo "EVENT: $(date +%s.%N) Opened file descriptor $fd"
done

echo "EVENT: $(date +%s.%N) Processing data"
sleep 2

echo "EVENT: $(date +%s.%N) Script completed"
```

## 📊 Understanding the Output

### Console Output
```
Command: python my_script.py
Logging to: fdprof.jsonl
Sampling interval: 0.1s
----------------------------------------
Starting application...
EVENT: 1234567890.123 Application startup
...command output...
----------------------------------------
Command completed with exit code: 0
Found 8 events

Event Timeline:
    0.05s: Application startup
    0.12s: Database connection 1 established
    0.15s: Database connection 2 established
    0.89s: Processing complete
    1.23s: All connections closed

Detected 3 stable plateaus:
  Plateau 1: 25 FDs from 0.00s to 0.10s
  Plateau 2: 30 FDs from 0.15s to 0.85s  
  Plateau 3: 25 FDs from 0.90s to 1.25s

Detected 2 jumps between plateaus:
    0.12s: +5 FDs (25 → 30)
    0.87s: -5 FDs (30 → 25)
```

### Generated Files

- **`fdprof.jsonl`** - Raw timestamped FD data in JSON Lines format
- **Interactive plot** (with `--plot`) showing:
  - FD usage over time (blue line)
  - Stable plateaus (gray horizontal lines)
  - Jump annotations with size labels
  - Event markers (colored vertical lines)

## 🔧 Advanced Usage

### Analyzing Different Application Types

#### Web Applications
```bash
# Monitor Flask development server
fdprof --plot flask run

# Monitor Django with database migrations
fdprof --plot python manage.py runserver

# Profile Gunicorn startup
fdprof --interval 0.05 --plot gunicorn -w 4 app:app
```

#### Database Operations
```bash
# Monitor PostgreSQL dump
fdprof --plot pg_dump mydb > backup.sql

# Profile database migration
fdprof --plot python manage.py migrate --verbosity=2
```

#### File Processing
```bash
# Monitor large file processing
fdprof --plot python process_large_files.py

# Profile backup operations
fdprof --plot tar -czf backup.tar.gz /important/data/
```

### Customizing Analysis Parameters

The plateau detection can be tuned by modifying the source code parameters:

- `min_length`: Minimum points for a plateau (default: 10)
- `tolerance`: Variance tolerance for stability (default: 3.0)
- `merge_threshold`: Level difference for merging plateaus (default: 50.0)

## 🐛 Troubleshooting

### Common Issues

#### "psutil not available" warning
```bash
# Install psutil if missing
pip install psutil
# or with uvx
uvx install --force fdprof
```

#### Permission denied on macOS/Linux
Some systems require elevated privileges for FD monitoring:
```bash
sudo fdprof --plot python my_script.py
```

#### No plot displayed
Ensure matplotlib backend is properly configured:
```bash
# Install GUI backend for matplotlib
pip install matplotlib[gui]
# or try different backend
export MPLBACKEND=TkAgg
```

### Platform-Specific Notes

- **Linux**: Full support for all features
- **macOS**: Full support, may need GUI backend for plotting
- **Windows**: Limited support (psutil.num_fds() not available)

## 📈 Use Cases

### Performance Analysis
- **Resource leak detection** - Monitor FD usage patterns to identify leaks
- **Application profiling** - Understand FD usage during different phases
- **Load testing** - Track FD consumption under various loads

### Development & Debugging
- **Database connection pooling** - Verify connection management
- **File handling** - Monitor file open/close patterns  
- **Network programming** - Track socket lifecycle
- **Service startup** - Profile initialization sequences

### Operations & Monitoring
- **Deployment validation** - Ensure services start correctly
- **Resource monitoring** - Track FD usage in production
- **Incident analysis** - Analyze FD patterns during outages

## 🔍 Example Analysis

Here's what fdprof revealed when analyzing a web application startup:

```bash
fdprof --plot gunicorn -w 4 myapp:app
```

**Key insights:**
- **Initial spike** (0-2s): 15→45 FDs during worker process creation
- **Stable plateau** (2-10s): 45 FDs during normal operation  
- **Event correlation**: Each "Worker spawned" event matched +8 FD increase
- **Resource leak detected**: Gradual increase from 45→52 FDs over time

This analysis helped identify a file descriptor leak in the logging module!

## 🤝 Contributing

```bash
# Setup development environment
git clone https://github.com/ianhi/fdprof
cd fdprof
make dev-setup

# Run tests
make test

# Run linting
make lint

# Run all checks
make check
```

## 📋 Requirements

- **Python 3.8+**
- **psutil** - Cross-platform process monitoring
- **matplotlib** - Plotting and visualization  
- **numpy** - Numerical analysis
- **scipy** - Statistical functions

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋 Support

- 📖 **Documentation**: See examples above and `fdprof --help`
- 🐛 **Issues**: Report bugs and feature requests
- 💡 **Discussions**: Share use cases and analysis results

---

**Quick Start**: `uvx run fdprof --plot python your_script.py` 🚀