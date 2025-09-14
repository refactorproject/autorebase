#!/usr/bin/env python3
"""
Wrapper script to run AutoRebase with correct environment setup
"""

import sys
import os
import subprocess
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent
run_script = script_dir / 'run_autorebase.py'

# Set up the environment
env = os.environ.copy()
env['PYTHONPATH'] = str(script_dir / 'src')

# Run the actual autorebase script
result = subprocess.run([
    sys.executable, 
    str(run_script)
] + sys.argv[1:], 
    env=env,
    cwd=str(script_dir),
    capture_output=True,
    text=True
)

# Print the output
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

# Exit with the same code
sys.exit(result.returncode)

