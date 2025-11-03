from multiprocessing import cpu_count
from os import environ

DEBUG = environ.get('DEBUG', default='False').upper() in ['TRUE','YES','1']

# General
bind = '0.0.0.0:' + environ.get('PORT', '8000')
workers = cpu_count() * 2 + 1
# threads = cpu_count() * 2
worker_class = 'gevent'
timeout = 121
worker_tmp_dir = '/dev/shm'
pidfile='/home/ows/gunicorn.pid'
reload=DEBUG

# Logging
loglevel = 'debug' if DEBUG else 'info'
accesslog = '-' if DEBUG else None
errorlog = '-'
enable_stdio_inheritance = True
