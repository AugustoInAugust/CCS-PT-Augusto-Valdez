from rest_framework import status
from rest_framework.exceptions import APIException


class PersonHasAccount(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'This person cannot be deleted while a login account is linked to it.'
    default_code = 'person_has_account'
