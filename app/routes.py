from flask import Blueprint, render_template, current_app, Response
from .catalog import SERVICES, PRODUCTS, CASES, FAQ
from .pricing import CARS, TARGETS, MATERIALS, STITCHES, EXTRAS
from xml.sax.saxutils import escape

pages = Blueprint('pages', __name__)

@pages.get('/')
def index():
    return render_template('index.html', services=SERVICES, products=PRODUCTS, cases=CASES, faq=FAQ,
        cars=CARS, targets=TARGETS, materials=MATERIALS, stitches=STITCHES, extras=EXTRAS,
        canonical=current_app.config['PUBLIC_URL'].rstrip('/') + '/')

@pages.get('/robots.txt')
def robots():
    return Response('User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: ' + current_app.config['PUBLIC_URL'].rstrip('/') + '/sitemap.xml\n', mimetype='text/plain')

@pages.get('/sitemap.xml')
def sitemap():
    url = escape(current_app.config['PUBLIC_URL'].rstrip('/') + '/')
    return Response(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{url}</loc></url></urlset>', mimetype='application/xml')

@pages.get('/health')
def health():
    return {'status': 'ok'}

@pages.app_errorhandler(404)
def missing(error):
    return render_template('404.html'), 404
