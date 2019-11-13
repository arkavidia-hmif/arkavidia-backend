from arkav.arkavauth.constants import K_PASSWORD_CHANGE_FAILED
from arkav.arkavauth.constants import K_PASSWORD_CHANGE_SUCCESSFUL
from arkav.utils.openapi import generic_response_schema
from drf_yasg import openapi

password_change_responses = {
    200: openapi.Response(description='OK', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Registration confirmation successful': {
                    'value': {
                        'code': K_PASSWORD_CHANGE_SUCCESSFUL,
                        'detail': 'Your password has been changed.'
                    }
                },
            }
        }
    }),
    401: openapi.Response(description='Unauthorized', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Invalid token': {
                    'value': {
                        'code': K_PASSWORD_CHANGE_FAILED,
                        'detail': 'Wrong old password.'
                    }
                },
            }
        }
    })
}
