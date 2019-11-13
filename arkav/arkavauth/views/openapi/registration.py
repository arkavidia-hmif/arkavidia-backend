from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_REGISTRATION_FAILED_EMAIL_USED
from arkav.arkavauth.constants import K_REGISTRATION_SUCCESSFUL
from arkav.arkavauth.constants import K_REGISTRATION_CONFIRMATION_SUCCESSFUL
from arkav.utils.openapi import generic_response_schema
from drf_yasg import openapi

registration_responses = {
    200: openapi.Response(description='OK', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Registration successful': {
                    'value': {
                        'code': K_REGISTRATION_SUCCESSFUL,
                        'detail': 'Email confirmation link has been sent to your email.'
                    }
                },
            }
        }
    }),
    400: openapi.Response(description='Bad Request', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Invalid token': {
                    'value': {
                        'code': K_REGISTRATION_FAILED_EMAIL_USED,
                        'detail': 'Account with specified email is already registered.'
                    }
                },
            }
        }
    })
}

registration_confirmation_responses = {
    200: openapi.Response(description='OK', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Registration confirmation successful': {
                    'value': {
                        'code': K_REGISTRATION_CONFIRMATION_SUCCESSFUL,
                        'detail': 'Your email has been successfully confirmed.'
                    }
                },
            }
        }
    }),
    400: openapi.Response(description='Bad Request', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Invalid token': {
                    'value': {
                        'code': K_INVALID_TOKEN,
                        'detail': 'Invalid token.'
                    }
                },
            }
        }
    })
}
