import json


def test_health(client):
    r = client.get('/api/v1/health')
    assert r.status_code == 200
    data = r.get_json()
    assert data['status'] == 'ok'


def test_api_login(client):
    r = client.post('/api/v1/auth/login',
                    data=json.dumps({'email': 'admin@test.com', 'password': 'Admin@123'}),
                    content_type='application/json')
    assert r.status_code == 200
    data = r.get_json()
    assert data['user']['email'] == 'admin@test.com'
    assert data['user']['role'] == 'Admin'


def test_api_login_fail(client):
    r = client.post('/api/v1/auth/login',
                    data=json.dumps({'email': 'admin@test.com', 'password': 'bad'}),
                    content_type='application/json')
    assert r.status_code == 401


def test_api_products_requires_auth(client):
    r = client.get('/api/v1/products')
    assert r.status_code == 401


def test_api_products_list(client):
    client.post('/api/v1/auth/login',
                data=json.dumps({'email': 'admin@test.com', 'password': 'Admin@123'}),
                content_type='application/json')
    r = client.get('/api/v1/products')
    assert r.status_code == 200
    data = r.get_json()
    assert 'products' in data


def test_api_create_product(client, app):
    client.post('/api/v1/auth/login',
                data=json.dumps({'email': 'mfr@test.com', 'password': 'Mfr@12345'}),
                content_type='application/json')
    from app.models import Organization
    with app.app_context():
        org_id = Organization.query.first().id
    r = client.post('/api/v1/products',
                    data=json.dumps({
                        'name': 'API Product',
                        'category': 'Test',
                        'manufacturer_org_id': org_id,
                        'origin_country': 'PK'
                    }),
                    content_type='application/json')
    assert r.status_code == 201
    data = r.get_json()
    assert data['name'] == 'API Product'
    assert data['passport_code'].startswith('TP-')


def test_api_public_verify_missing(client):
    r = client.get('/api/v1/public/verify')
    assert r.status_code == 400


def test_api_public_verify_not_found(client):
    r = client.get('/api/v1/public/verify?code=TP-NOTEXIST')
    assert r.status_code == 200
    assert r.get_json()['valid'] is False
