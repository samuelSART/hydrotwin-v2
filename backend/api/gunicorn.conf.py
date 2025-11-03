from multiprocessing import cpu_count
from os import environ

DEBUG = environ.get('DEBUG', default='False').upper() in ['TRUE','YES','1']

# General
bind = '0.0.0.0:' + environ.get('PORT', '5000')
workers = cpu_count() * 2 + 1
# threads = cpu_count() * 2
worker_class = 'sync'
worker_connections = 1000
timeout = environ.get('TIMEOUT', 30)
keepalive = 2
worker_tmp_dir = '/dev/shm'

# Logging
loglevel = 'debug' if DEBUG else 'info'
accesslog = '-' if DEBUG else None
errorlog = '-'
