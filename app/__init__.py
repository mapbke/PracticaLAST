import os
import secrets
from pathlib import Path
from flask import Flask, jsonify
from dotenv import load_dotenv
from .database import init_db, close_db
from .security import setup_security

def create_app(config=None):
    load_dotenv()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY=os.getenv('SECRET_KEY') or secrets.token_hex(32),
        DATABASE=str(Path(app.instance_path) / 'kurotsuki.db'), MAX_CONTENT_LENGTH=65536,
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('FORCE_HTTPS', 'false').lower() == 'true',
        FORCE_HTTPS=os.getenv('FORCE_HTTPS', 'false').lower() == 'true',
        PUBLIC_URL=os.getenv('PUBLIC_URL', 'http://127.0.0.1:5000'))
    if config:
        app.config.update(config)
    if app.config['FORCE_HTTPS'] and not app.config['PUBLIC_URL'].startswith('https://'):
        raise ValueError('FORCE_HTTPS requires an https:// PUBLIC_URL to avoid a redirect loop.')
    Path(app.instance_path).mkdir(exist_ok=True)
    setup_security(app)
    app.teardown_appcontext(close_db)
    from .routes import pages
    from .api import api
    app.register_blueprint(pages)
    app.register_blueprint(api)
    with app.app_context():
        init_db()
    @app.errorhandler(413)
    def too_large(error):
        return jsonify(error='Слишком большой запрос.'), 413
    return app
