from app.models import Shop, Product, Category, User
import pytest
from django.contrib.auth import authenticate
from rest_framework.test import APIClient
from model_bakery import baker



@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def shop():
    return Shop.objects.create(name='test', status=True)


@pytest.fixture
def category():
    return Category.objects.create(name='test')


@pytest.fixture
def product_factory():
    def factory(*args, **kwargs):
        return baker.make(Product, make_m2m=True, *args, **kwargs)

    return factory


@pytest.fixture
def auth_user():
    user = User.objects.create(email="test@mail.ru", password="testtest", username="test@mail.ru")
    return user


@pytest.fixture
def auth_client():
    client = APIClient()
    user = User.objects.create(email="test@mail.ru", password="testtest")
    client.force_authenticate(user)
    return client


@pytest.mark.django_db
def test_login_loguot(client):
    user = User.objects.create(email="test@mail.ru", password="testtest")
    data = {
        "username": "test@mail.ru",
        "password": "testtest"
    }
    response = client.post('/login/', data=data, format='json')

    assert response.status_code == 200

    data = response.json()
    token = data['token']

    assert token

    client.force_authenticate(user)
    response = client.post('/logout/')

    assert response.status_code == 200

    assert response.json()['status'] == "Logout has been completed"


@pytest.mark.django_db
def test_registration(client):
    data = {
        "email": 'test@mail.ru',
        "username": "test",
        "password": "testtest",
        "password2": "testtest"
    }
    response = client.post('/registration/', data=data, format='json')

    assert response.status_code == 200

    data = response.json()

    assert data['status'] == "Registration has been done"


@pytest.mark.django_db
def test_contact_info(auth_client):
    data = {
        "adress": "adress",
        "t_number": "23123123123123"
    }
    response = auth_client.post('/contact_info/', data=data, format="json")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "OK"

    response = auth_client.get('/contact_info/')
    assert response.status_code == 200

    data = {
        "adress": "adress1",
        "t_number": "2312312312312311"
    }
    response = auth_client.put('/contact_info/', data=data, format='json')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "OK"

    response = auth_client.delete('/contact_info/')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == "OK"


@pytest.mark.django_db
def test_product(product_factory, auth_client, shop, client):
    products = product_factory(_quantity=10)

    response = auth_client.get("/product/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == len(products)
