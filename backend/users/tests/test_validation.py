import pytest

from conftest import USERS_URL

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'missing_field',
    ['first_name', 'last_name', 'email', 'phone', 'country', 'birth_date'],
)
def test_every_field_is_required(admin_client, person_payload, missing_field):
    person_payload.pop(missing_field)

    response = admin_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 400
    assert missing_field in response.data['error']['fields']


def test_email_must_be_well_formed(admin_client, person_payload):
    person_payload['email'] = 'not-an-email'

    response = admin_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 400
    assert 'email' in response.data['error']['fields']


def test_email_must_be_unique(admin_client, person, person_payload):
    person_payload['email'] = person.email

    response = admin_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 400
    assert response.data['error']['fields']['email'] == [
        'A person with this email already exists.'
    ]


def test_birth_date_cannot_be_in_the_future(admin_client, person_payload):
    person_payload['birth_date'] = '2190-01-01'

    response = admin_client.post(USERS_URL, person_payload, format='json')

    assert response.status_code == 400
    assert response.data['error']['fields']['birth_date'] == [
        'Birth date cannot be in the future.'
    ]


def test_validation_errors_use_the_shared_envelope(admin_client):
    response = admin_client.post(USERS_URL, {}, format='json')

    assert response.status_code == 400
    assert set(response.data['error']) == {'status', 'code', 'message', 'fields'}
