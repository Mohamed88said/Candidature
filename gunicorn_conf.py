# gunicorn.conf.py
import multiprocessing

# Nombre de workers adapté pour Render.com (limité en mémoire)
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 2

# Configuration mémoire
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Sécurité
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190