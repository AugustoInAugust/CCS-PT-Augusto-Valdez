from datetime import date

import pytest
from rest_framework.test import APIClient

from users.models import Person

LOGIN_URL = '/api/v1/login/'
USERS_URL = '/api/v1/users/'

ADMIN_CREDENTIALS = {'username': 'admin', 'password': 'Admin123!'}
READER_CREDENTIALS = {'username': 'user123', 'password': 'Password1!'}


def authenticated_client(credentials):
    client = APIClient()
    response = client.post(LOGIN_URL, credentials, format='json')
    assert response.status_code == 200, response.data
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
    return client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_client(db):
    return authenticated_client(ADMIN_CREDENTIALS)


@pytest.fixture
def reader_client(db):
    return authenticated_client(READER_CREDENTIALS)


@pytest.fixture
def person(db):
    return Person.objects.create(
        first_name='Test',
        last_name='Subject',
        email='test.subject@example.com',
        phone='+51 900 111 222',
        country='Peru',
        birth_date=date(1992, 5, 4),
    )


@pytest.fixture
def person_payload():
    return {
        'first_name': 'Nuevo',
        'last_name': 'Registro',
        'email': 'nuevo.registro@example.com',
        'phone': '+51 999 111 222',
        'country': 'Peru',
        'birth_date': '1999-02-10',
    }
