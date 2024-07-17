import os

from app import app
from waitress import serve


def main():
    print('Running', f"PORT:{os.getenv('APP_PORT')}")
    serve(app, host='0.0.0.0', port=os.getenv("APP_PORT"), threads=600,
          channel_timeout=60, cleanup_interval=30, expose_tracebacks=True, connection_limit=2000)


if __name__ == '__main__':
    main()
