def test_login_page(client):
    r = client.get('/auth/login')
    assert r.status_code == 200
    assert b'Login' in r.data


def test_register_page(client):
    r = client.get('/auth/register')
    assert r.status_code == 200
    assert b'Customer' in r.data or b'Register' in r.data


def test_login_success(client):
    r = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'Admin@123'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Dashboard' in r.data or b'Welcome' in r.data or b'admin' in r.data.lower()


def test_login_fail(client):
    r = client.post('/auth/login', data={
        'email': 'admin@test.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b'Invalid' in r.data or b'invalid' in r.data.lower()


def test_register_creates_customer(client, app):
    r = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'newuser@test.com',
        'password': 'Password1',
        'password2': 'Password1'
    }, follow_redirects=True)
    assert r.status_code == 200
    from app.models import User
    with app.app_context():
        u = User.query.filter_by(email='newuser@test.com').first()
        assert u is not None
        assert u.role.name == 'Customer'


def test_admin_required(client, admin_client):
    # anonymous cannot access admin
    r = client.get('/admin/', follow_redirects=True)
    assert r.status_code == 200
    # admin can
    r2 = admin_client.get('/admin/')
    assert r2.status_code == 200
