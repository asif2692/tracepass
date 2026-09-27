def test_customer_cannot_access_admin(client):
    client.post('/auth/login', data={
        'email': 'customer@test.com',
        'password': 'Cust@1234'
    }, follow_redirects=True)
    r = client.get('/admin/')
    assert r.status_code == 403


def test_admin_can_access_admin(admin_client):
    r = admin_client.get('/admin/')
    assert r.status_code == 200


def test_customer_cannot_create_product(client):
    client.post('/auth/login', data={
        'email': 'customer@test.com',
        'password': 'Cust@1234'
    }, follow_redirects=True)
    r = client.get('/products/create')
    assert r.status_code == 403
