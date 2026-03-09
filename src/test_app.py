import pytest
from app import app, data


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        data.clear()
        yield client
    data.clear()


# --- UI Route Tests ---

def test_index_returns_html(client):
    """The root route serves the UI page."""
    res = client.get('/')
    assert res.status_code == 200
    assert b'Product Store' in res.data
    assert b'text/html' in res.content_type.encode()


def test_index_contains_form(client):
    """The UI contains the product form."""
    res = client.get('/')
    assert b'product-form' in res.data
    assert b'product-name' in res.data


def test_index_contains_product_list(client):
    """The UI contains the product list container."""
    res = client.get('/')
    assert b'product-list' in res.data


# --- API Tests ---

def test_get_products_empty(client):
    """GET /products returns empty list when no products exist."""
    res = client.get('/products')
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_product(client):
    """POST /products creates a new product."""
    res = client.post('/products', json={'name': 'test item', 'description': 'test description'})
    assert res.status_code == 201
    body = res.get_json()
    assert body['name'] == 'test item'
    assert body['description'] == 'test description'
    assert 'id' in body


def test_create_product_missing_name(client):
    """POST /products with missing name returns 400."""
    res = client.post('/products', json={'description': 'no name'})
    assert res.status_code == 400


def test_get_product_by_id(client):
    """GET /products/<id> returns the correct product."""
    create_res = client.post('/products', json={'name': 'test item'})
    product_id = create_res.get_json()['id']
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 200
    assert res.get_json()['name'] == 'test item'


def test_get_product_not_found(client):
    """GET /products/<id> returns 404 for nonexistent product."""
    res = client.get('/products/nonexistent-id')
    assert res.status_code == 404


def test_update_product(client):
    """PUT /products/<id> updates an existing product."""
    create_res = client.post('/products', json={'name': 'test item', 'description': 'test description'})
    product_id = create_res.get_json()['id']
    res = client.put(f'/products/{product_id}', json={'name': 'updated item', 'description': 'updated desc'})
    assert res.status_code == 200
    body = res.get_json()
    assert body['name'] == 'updated item'
    assert body['description'] == 'updated desc'


def test_update_product_not_found(client):
    """PUT /products/<id> returns 404 for nonexistent product."""
    res = client.put('/products/nonexistent-id', json={'name': 'test'})
    assert res.status_code == 404


def test_delete_product(client):
    """DELETE /products/<id> removes the product."""
    create_res = client.post('/products', json={'name': 'test item'})
    product_id = create_res.get_json()['id']
    res = client.delete(f'/products/{product_id}')
    assert res.status_code == 204
    # Verify it's gone
    res = client.get(f'/products/{product_id}')
    assert res.status_code == 404


def test_delete_product_not_found(client):
    """DELETE /products/<id> returns 404 for nonexistent product."""
    res = client.delete('/products/nonexistent-id')
    assert res.status_code == 404