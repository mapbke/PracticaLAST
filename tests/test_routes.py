import re
import pytest

@pytest.mark.parametrize('path,status', [('/',200),('/robots.txt',200),('/sitemap.xml',200),('/health',200),('/missing',404)])
def test_pages(client,path,status):
    assert client.get(path).status_code == status

def test_static_files(client):
    html = client.get('/').get_data(as_text=True)
    paths = set(re.findall(r'(?:src|href)="(/static/[^\"]+)"', html))
    assert len(paths) >= 10
    for path in paths:
        assert client.get(path).status_code == 200, path

def test_security_headers(client):
    response = client.get('/')
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert "script-src 'self'" in response.headers['Content-Security-Policy']
    assert response.headers['X-Content-Type-Options'] == 'nosniff'

def test_https_redirect(app):
    app.config.update(FORCE_HTTPS=True,PUBLIC_URL='https://example.test')
    response=app.test_client().get('/?a=1')
    assert response.status_code==308
    assert response.location=='https://example.test/?a=1'

def test_https_redirect_precedes_csrf(app):
    app.config.update(FORCE_HTTPS=True,PUBLIC_URL='https://example.test')
    client=app.test_client()
    assert client.post('/api/contact',json={}).status_code==308
    assert client.post('/api/contact',json={},base_url='https://example.test').status_code==400

def test_https_misconfiguration_fails_fast(tmp_path):
    from app import create_app
    with pytest.raises(ValueError,match='PUBLIC_URL'):
        create_app({'FORCE_HTTPS':True,'PUBLIC_URL':'http://example.test','DATABASE':str(tmp_path/'test.db')})
