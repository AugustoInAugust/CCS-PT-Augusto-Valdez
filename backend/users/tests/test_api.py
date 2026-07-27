import pytest

from conftest import USERS_URL
from users.models import Person

pytestmark = pytest.mark.django_db


def test_list_is_paginated(admin_client):
    response = admin_client.get(USERS_URL)

    assert response.status_code == 200
    assert set(response.data) == {'count', 'next', 'previous', 'results'}
    assert len(response.data['results']) == 10
    assert response.data['count'] == Person.objects.count()


def test_second_page_returns_the_remaining_records(admin_client):
    response = admin_client.get(USERS_URL, {'page': 2})

    assert response.status_code == 200
    assert response.data['previous'] is not None


def test_search_matches_country(admin_client):
    response = admin_client.get(USERS_URL, {'search': 'Japan'})

    assert response.status_code == 200
    assert response.data['count'] == 1
    assert response.data['results'][0]['country'] == 'Japan'


def test_search_without_matches_returns_an_empty_page(admin_client):
    response = admin_client.get(USERS_URL, {'search': 'Wakanda'})

    assert response.data['count'] == 0
    assert response.data['results'] == []


def test_ordering_is_applied(admin_client):
    response = admin_client.get(USERS_URL, {'ordering': 'country'})

    countries = [person['country'] for person in response.data['results']]
    assert countries == sorted(countries)


def test_retrieve_exposes_the_full_record(admin_client, person):
    response = admin_client.get(f'{USERS_URL}{person.id}/')

    assert response.status_code == 200
    assert response.data['full_name'] == 'Test Subject'
    assert set(response.data) == {
        'id',
        'first_name',
        'last_name',
        'full_name',
        'email',
        'phone',
        'country',
        'birth_date',
    }


def test_unknown_id_returns_404(admin_client):
    response = admin_client.get(f'{USERS_URL}999999/')

    assert response.status_code == 404
    assert response.data['error']['code'] == 'not_found'


def test_create_persists_the_person(admin_client, person_payload):
    response = admin_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 201
    assert Person.objects.filter(email=person_payload['email']).exists()


def test_update_replaces_the_record(admin_client, person, person_payload):
    person_payload['email'] = person.email
    person_payload['first_name'] = 'Renamed'

    response = admin_client.put(f'{USERS_URL}{person.id}/', person_payload, format='json')

    assert response.status_code == 200
    person.refresh_from_db()
    assert person.first_name == 'Renamed'


def test_delete_removes_the_record(admin_client, person):
    response = admin_client.delete(f'{USERS_URL}{person.id}/')

    assert response.status_code == 204
    assert not Person.objects.filter(pk=person.pk).exists()


def test_deleting_a_person_with_an_account_returns_409(admin_client):
    linked = Person.objects.get(email='admin@ccs.test')

    response = admin_client.delete(f'{USERS_URL}{linked.id}/')

    assert response.status_code == 409
    assert response.data['error']['code'] == 'person_has_account'
    assert Person.objects.filter(pk=linked.pk).exists()
