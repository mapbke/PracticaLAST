import pytest
from app.pricing import DEFAULT
from app.database import get_db

def payload(**extra):
    return {'name':'Тестовый клиент','contact':'@testuser','car_model':'Toyota Supra','message':'Тестовая заявка','consent':True,'configuration':DEFAULT,'cart':[],**extra}

def test_calculate(client,headers):
    response=client.post('/api/calculate',json={**DEFAULT,'centerMark':True,'quantity':2},headers=headers)
    assert response.status_code==200
    assert response.json['total']==66600

@pytest.mark.parametrize('patch',[{'quantity':-1},{'quantity':21},{'quantity':True},{'quantity':1.5},{'quantity':'2'},{'target':'unknown'},{'material':[]},{'carType':None},{'centerMark':'true'},{'stitchColor':'gold'}])
def test_invalid_config(client,headers,patch):
    assert client.post('/api/calculate',json={**DEFAULT,**patch},headers=headers).status_code==400

def test_price_cannot_be_overridden(client,headers):
    response=client.post('/api/calculate',json={**DEFAULT,'total':1,'unitPrice':1,'price':1},headers=headers)
    assert response.json['total']==30800

@pytest.mark.parametrize('patch',[{'name':''},{'name':'x'*81},{'contact':'abcde'},{'contact':[]},{'car_model':''},{'message':'x'*2001},{'consent':False},{'cart':[{'productId':'unknown'}]},{'cart':[DEFAULT]*31},{'configuration':None}])
def test_contact_validation(client,headers,patch):
    assert client.post('/api/contact',json=payload(**patch),headers=headers).status_code==400

def test_contact_persists_and_reprices(client,headers,app):
    response=client.post('/api/contact',json=payload(cart=[{**DEFAULT,'quantity':2,'total':1}],total=1),headers=headers)
    assert response.status_code==201
    assert response.json['total']==61600
    with app.app_context():
        row=get_db().execute('SELECT * FROM leads').fetchone()
        assert row['total']==61600
        assert row['name']=='Тестовый клиент'

@pytest.mark.parametrize('path',['/api/calculate','/api/contact'])
def test_csrf_required(client,path):
    assert client.post(path,json=DEFAULT).status_code==400

@pytest.mark.parametrize('value',[[],None,42,'text'])
def test_nonobject_json(client,headers,value):
    assert client.post('/api/calculate',json=value,headers=headers).status_code==400

def test_injection_is_inert(client,headers,app):
    attack="<script>alert(1)</script>'; DROP TABLE leads;--"
    response=client.post('/api/contact',json=payload(message=attack),headers=headers)
    assert response.status_code==201
    with app.app_context():
        assert get_db().execute('SELECT message FROM leads').fetchone()['message']==attack
        assert get_db().execute('SELECT count(*) FROM leads').fetchone()[0]==1
    assert attack not in client.get('/').get_data(as_text=True)

def test_body_limit(client,headers):
    assert client.post('/api/contact',json=payload(message='x'*70000),headers=headers).status_code==413

def test_invalid_csrf(client,headers):
    assert client.post('/api/calculate',json=DEFAULT,headers={'X-CSRFToken':'invalid'}).status_code==400

@pytest.mark.parametrize('contact',['-------','() () ()','+1----23','123456','1234567890123456','@____','@1234'])
def test_contact_requires_real_format(client,headers,contact):
    assert client.post('/api/contact',json=payload(contact=contact),headers=headers).status_code==400

@pytest.mark.parametrize('contact',['+7 (900) 000-00-00','89000000000','@testuser'])
def test_valid_contact_formats(client,headers,contact):
    assert client.post('/api/contact',json=payload(contact=contact),headers=headers).status_code==201

def test_rejected_cart_does_not_write_lead(client,headers,app):
    response=client.post('/api/contact',json=payload(cart=[{**DEFAULT,'quantity':-2}]),headers=headers)
    assert response.status_code==400
    with app.app_context():
        assert get_db().execute('SELECT count(*) FROM leads').fetchone()[0]==0
