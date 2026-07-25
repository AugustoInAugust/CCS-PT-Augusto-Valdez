import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        logger.exception('Unhandled exception in %s', context.get('view'))
        return Response(
            {
                'error': {
                    'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                    'code': 'internal_error',
                    'message': 'An unexpected error occurred.',
                    'fields': {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    payload = response.data
    code = getattr(exc, 'default_code', 'error')

    if isinstance(payload, dict) and 'detail' in payload:
        detail = payload['detail']
        code = getattr(detail, 'code', None) or code
        message = str(detail)
        fields = {}
    elif isinstance(payload, dict):
        message = 'The submitted data is not valid.'
        fields = payload
    else:
        message = 'The request could not be processed.'
        fields = {'non_field_errors': payload}

    response.data = {
        'error': {
            'status': response.status_code,
            'code': code,
            'message': message,
            'fields': fields,
        }
    }

    return response
