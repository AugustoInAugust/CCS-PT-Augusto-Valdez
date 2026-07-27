import pytest

from conftest import ADMIN_CREDENTIALS, LOGIN_URL, READER_CREDENTIALS

REFRESH_URL = '/api/v1/token/refresh/'
LOGOUT_URL = '/api/v1/logout/'

pytestmark = pytest.mark.django_db


def test_admin_login_returns_tokens_and_profile(api_client):
    response = api_client.post(LOGIN_URL, ADMIN_CREDENTIALS, format='json')

    assert response.status_code == 200
    assert response.data['username'] == 'admin'
    assert response.data['role'] == 'ADMIN'
    assert response.data['person_id']
    assert response.data['access']
    assert response.data['refresh']


def test_regular_account_logs_in_with_user_role(api_client):
    response = api_client.post(LOGIN_URL, READER_CREDENTIALS, format='json')

    assert response.status_code == 200
    assert response.data['role'] == 'USER'


def test_password_is_never_returned(api_client):
    response = api_client.post(LOGIN_URL, ADMIN_CREDENTIALS, format='json')

    assert 'password' not in response.data


@pytest.mark.parametrize(
    'credentials',
    [
        {'username': 'admin', 'password': 'WrongPassword'},
        {'username': 'does-not-exist', 'password': 'Password1!'},
    ],
    ids=['wrong-password', 'unknown-username'],
)
def test_invalid_credentials_share_the_same_message(api_client, credentials):
    response = api_client.post(LOGIN_URL, credentials, format='json')

    assert response.status_code == 401
    assert response.data['error']['message'] == 'Invalid username or password.'


def test_missing_fields_are_reported_per_field(api_client):
    response = api_client.post(LOGIN_URL, {}, format='json')

    assert response.status_code == 400
    assert 'username' in response.data['error']['fields']
    assert 'password' in response.data['error']['fields']


def test_refresh_returns_a_new_access_token(api_client):
    tokens = api_client.post(LOGIN_URL, ADMIN_CREDENTIALS, format='json').data

    response = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')

    assert response.status_code == 200
    assert response.data['access'] != tokens['access']


def test_rotated_refresh_token_cannot_be_replayed(api_client):
    tokens = api_client.post(LOGIN_URL, ADMIN_CREDENTIALS, format='json').data
    api_client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')

    replay = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')

    assert replay.status_code == 401


def test_logout_blacklists_the_refresh_token(api_client):
    tokens = api_client.post(LOGIN_URL, ADMIN_CREDENTIALS, format='json').data

    assert api_client.post(LOGOUT_URL, {'refresh': tokens['refresh']}, format='json').status_code == 200

    reuse = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']}, format='json')
    assert reuse.status_code == 401
