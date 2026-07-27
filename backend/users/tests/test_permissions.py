import pytest

from conftest import USERS_URL

pytestmark = pytest.mark.django_db


def test_anonymous_requests_are_rejected(api_client):
    response = api_client.get(USERS_URL)

    assert response.status_code == 401


def test_reader_can_list_people(reader_client):
    assert reader_client.get(USERS_URL).status_code == 200


def test_reader_can_retrieve_a_person(reader_client, person):
    assert reader_client.get(f'{USERS_URL}{person.id}/').status_code == 200


def test_reader_cannot_create(reader_client, person_payload):
    response = reader_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 403
    assert response.data['error']['message'] == 'Only administrators can modify user records.'


def test_reader_cannot_update(reader_client, person, person_payload):
    response = reader_client.put(f'{USERS_URL}{person.id}/', person_payload, format='json')

    assert response.status_code == 403


def test_reader_cannot_delete(reader_client, person):
    response = reader_client.delete(f'{USERS_URL}{person.id}/')

    assert response.status_code == 403


def test_admin_can_create(admin_client, person_payload):
    assert admin_client.post(USERS_URL, person_payload, format='json').status_code == 201
