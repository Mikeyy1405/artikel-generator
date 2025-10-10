"""
Gunicorn configuration file for artikel-generator
This file ensures timeout settings are applied regardless of how Gunicorn is started
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"
backlog = 2048

# Worker processes
workers = 2
worker_class = 'sync'
worker_connections = 1000
threads = 4

# Timeout settings - CRITICAL for long-running AI operations
timeout = 300  # 5 minutes for worker timeout
graceful_timeout = 300  # 5 minutes for graceful shutdown
keepalive = 5  # Keep-alive connections

# Logging
loglevel = 'info'
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'artikel-generator'

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Performance tuning
max_requests = 1000  # Restart workers after this many requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

print(f"🚀 Gunicorn configuration loaded:")
print(f"   - Workers: {workers}")
print(f"   - Threads per worker: {threads}")
print(f"   - Timeout: {timeout}s")
print(f"   - Graceful timeout: {graceful_timeout}s")
print(f"   - Port: {os.getenv('PORT', '10000')}")
