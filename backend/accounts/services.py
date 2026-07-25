import logging

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)

INVALID_CREDENTIALS = 'Invalid username or password.'


def login(username, password):
    account = authenticate(username=username, password=password)

    if account is None:
        logger.warning('Failed login attempt for username %r', username)
        raise AuthenticationFailed(INVALID_CREDENTIALS)

    logger.info('Account %r logged in', account.username)
    refresh = RefreshToken.for_user(account)

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'person_id': account.person_id,
        'username': account.username,
        'role': account.role,
    }
