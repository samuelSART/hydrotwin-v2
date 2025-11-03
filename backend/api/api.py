import os

from app import create_app

API_PORT = os.environ.get('API_PORT') or '5000'
app = create_app(os.getenv('ENVIRONMENT') or 'default')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=API_PORT)
