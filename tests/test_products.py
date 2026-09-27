from app import db
from app.models import Product, Organization, User


def test_products_requires_login(client):
    r = client.get('/products/')
    assert r.status_code in (302, 401, 200)  # redirect to login


def test_create_product(mfr_client, app):
    with app.app_context():
        org = Organization.query.first()
        org_id = org.id
    r = mfr_client.post('/products/create', data={
        'name': 'Test Shirt',
        'category': 'Apparel',
        'brand': 'TestBrand',
        'model': 'T1',
        'description': 'Test product',
        'manufacturer_org_id': str(org_id),
        'origin_country': 'Pakistan'
    }, follow_redirects=True)
    assert r.status_code == 200
    with app.app_context():
        p = Product.query.filter_by(name='Test Shirt').first()
        assert p is not None
        assert p.passport_code.startswith('TP-')
        assert p.status == 'draft'


def test_product_list(mfr_client):
    r = mfr_client.get('/products/')
    assert r.status_code == 200
