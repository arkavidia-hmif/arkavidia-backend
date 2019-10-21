from arkav.arkavauth.constants import K_LOGIN_FAILED
from arkav.arkavauth.constants import K_ACCOUNT_EMAIL_NOT_CONFIRMED
from arkav.arkavauth.serializers import UserSerializer
from arkav.utils.openapi import generic_response_schema
from drf_yasg import openapi

login_responses = {
    200: UserSerializer(),
    401: openapi.Response(description='Unauthorized', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Login failed': {
                    'value': {
                        'code': K_LOGIN_FAILED,
                        'detail': 'Wrong email or password.',
                    }
                },
                'Account email not confirmed': {
                    'value': {
                        'code': K_ACCOUNT_EMAIL_NOT_CONFIRMED,
                        'detail': 'Account email hasn\'t been confirmed. Check inbox for confirmation email.',
                    }
                }
            }
        }
    })
}
