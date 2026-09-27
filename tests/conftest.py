import pytest
from app import create_app, db
from app.models import User, Role, Organization, Product


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        Role.insert_roles()
        # Demo org + admin
        org = Organization(
            name='Test Org',
            type='manufacturer',
            is_verified=True,
            is_active=True
        )
        db.session.add(org)
        db.session.flush()
        admin_role = Role.query.filter_by(name='Admin').first()
        customer_role = Role.query.filter_by(name='Customer').first()
        mfr_role = Role.query.filter_by(name='Manufacturer').first()

        admin = User(name='Admin', email='admin@test.com', role_id=admin_role.id,
                     organization_id=org.id, is_active=True)
        admin.password = 'Admin@123'
        customer = User(name='Customer', email='customer@test.com', role_id=customer_role.id, is_active=True)
        customer.password = 'Cust@1234'
        mfr = User(name='Manufacturer', email='mfr@test.com', role_id=mfr_role.id,
                   organization_id=org.id, is_active=True)
        mfr.password = 'Mfr@12345'
        db.session.add_all([admin, customer, mfr])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin_client(client):
    client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Admin@123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def mfr_client(client):
    client.post('/auth/login', data={
        'email': 'mfr@test.com',
        'password': 'Mfr@12345'
    }, follow_redirects=True)
    return client
