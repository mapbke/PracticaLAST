from app import create_app
from scripts.generate_dev_cert import generate

if __name__ == '__main__':
    create_app({'SESSION_COOKIE_SECURE': True, 'PUBLIC_URL': 'https://127.0.0.1:5443'}).run(
        host='127.0.0.1', port=5443, ssl_context=generate(), debug=False)
