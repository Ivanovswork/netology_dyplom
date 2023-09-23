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