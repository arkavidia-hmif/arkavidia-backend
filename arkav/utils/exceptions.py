from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def exception_handler_with_code(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        default_response = response.data.copy()
        response.data = {}
        response.data['code'] = 'unknown_error'
        response.data['detail'] = default_response

    return response


class ArkavAPIException(Exception):
    def __init__(self, detail=None, code=None, status_code=None):
        if code is None:
            code = 'unknown_error'

        if status_code is None:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        self.detail = detail
        self.code = code
        self.status_code = status_code

    def as_response(self):
        return Response({
            'code': self.code,
            'detail': self.detail,
        }, status=self.status_code)
