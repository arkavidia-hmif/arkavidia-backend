from arkav.competition.constants import K_TEAM_NAME_TAKEN
from arkav.competition.constants import K_TEAM_NAME_TAKEN_DETAIL
from arkav.competition.serializers import TeamSerializer
from arkav.utils.openapi import generic_response_schema
from drf_yasg import openapi


register_team_responses = {
    200: TeamSerializer(),
    400: openapi.Response(description='Bad Request', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Team name already taken': {
                    'value': {
                        'code': K_TEAM_NAME_TAKEN,
                        'detail': K_TEAM_NAME_TAKEN_DETAIL,
                    }
                },
            }
        }
    })
}
