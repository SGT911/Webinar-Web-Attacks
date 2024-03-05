from dotenv import load_dotenv
import os

load_dotenv()

wsgi_app = 'main:app'

bind = os.environ.get('GUNICORN_BIND', 'unix:/run/app.sock')
workers = os.environ.get('GUNICORN_WORKERS', 4)
timeout = os.environ.get('GUNICORN_TIMEOUT', 30)
