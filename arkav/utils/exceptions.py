from rest_framework.views import exception_handler

def exception_handler_with_code(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        default_response = response.data.copy()
        response.data = {}
        response.data['code'] = 'unknown_error'
        response.data['detail'] = default_response

    return response
