from os import getenv, name
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

PORT = getenv('PORT', default=5000)
TIMEOUT = int(getenv('TIMEOUT', default=30))
HEALTHCHECK_URL = f'http://localhost:{PORT}/healthcheck'

def check():
    try:
        urlopen(url=HEALTHCHECK_URL, timeout=TIMEOUT)
    except HTTPError as http_err:
        print(f'[HEALTHCHECK] HTTP error occurred: {http_err.code}')
        exit(1)
    except URLError as url_err:
        print(f'[HEALTHCHECK] URL error occurred: {url_err.reason}')
        exit(1)
    except Exception as err:
        print(f'[HEALTHCHECK] Other error occurred: {err}')
        exit(1)
    else:
        print('[HEALTHCHECK] Healthcheck OK!')
        exit(0)

if __name__ == '__main__':
    check()
