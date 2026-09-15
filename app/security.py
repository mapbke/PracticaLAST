from flask import current_app, request, redirect, jsonify
from flask_wtf.csrf import CSRFProtect, CSRFError

csrf = CSRFProtect()

def setup_security(app):
    @app.before_request
    def enforce_https():
        if current_app.config['FORCE_HTTPS'] and not request.is_secure:
            return redirect(current_app.config['PUBLIC_URL'].rstrip('/') + request.full_path.rstrip('?'), code=308)

    # Redirect before CSRF validation; the HTTPS endpoint still validates every POST.
    csrf.init_app(app)

    @app.after_request
    def headers(response):
        response.headers.update({
            'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
            'Content-Security-Policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'",
        })
        if request.path.startswith('/api/') or request.path == '/':
            response.headers['Cache-Control'] = 'no-store'
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error='Сессия устарела. Обновите страницу и повторите отправку.'), 400
