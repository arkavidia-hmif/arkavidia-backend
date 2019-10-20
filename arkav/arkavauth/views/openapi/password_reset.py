from arkav.arkavauth.constants import K_INVALID_TOKEN
from arkav.arkavauth.constants import K_PASSWORD_RESET_EMAIL_SENT
from arkav.arkavauth.constants import K_PASSWORD_RESET_SUCCESSFUL
from arkav.arkavauth.constants import K_TOKEN_USED
from arkav.utils.openapi import generic_response_schema
from drf_yasg import openapi


password_reset_responses = {
    200: openapi.Response(description='OK', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Password reset email sent': {
                    'value': {
                        'code': K_PASSWORD_RESET_EMAIL_SENT,
                        'detail':
                        'If you have registered using that email, we have sent password reset link to your email.'
                        ' Please check your email.',
                    }
                },
            }
        }
    })
}

password_reset_confirmation_responses = {
    200: openapi.Response(description='OK', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Password reset successful': {
                    'value': {
                        'code': K_PASSWORD_RESET_SUCCESSFUL,
                        'detail': 'Your password has been successfully reset.',
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
                        'detail': 'Invalid token.',
                    }
                },
                'Token used': {
                    'value': {
                        'code': K_TOKEN_USED,
                        'detail': 'This token has been used.',
                    }
                },
            }
        }
    })
}
