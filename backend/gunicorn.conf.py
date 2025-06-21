# Gunicorn configuration for ValMed backend
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "valmed-backend"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None

# Server mechanics
preload_app = True
sendfile = True
reuse_port = True

# Worker timeout
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Worker timeout
graceful_timeout = 30

# Environment variables
raw_env = [
    "PYTHONPATH=/app",
    "PYTHONUNBUFFERED=1",
] 