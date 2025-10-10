#!/bin/bash
#
# WritgoAI Content Automation Daemon Runner
# Wrapper script for scheduled execution
#

set -e

# Change to project directory
cd /home/ubuntu/github_repos/artikel-generator

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the daemon
python3 content_automation_daemon.py "$@"

# Exit with daemon's exit code
exit $?
