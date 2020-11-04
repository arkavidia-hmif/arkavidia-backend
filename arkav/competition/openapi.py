from drf_yasg import openapi

from arkav.competition.serializers import TeamSerializer
from arkav.competition.serializers import TeamMemberSerializer
from arkav.utils.openapi import generic_response_schema

from arkav.competition.constants import K_TEAM_NAME_TAKEN
from arkav.competition.constants import K_TEAM_NAME_TAKEN_DETAIL
from arkav.competition.constants import K_COMPETITION_REGISTRATION_CLOSED
from arkav.competition.constants import K_COMPETITION_REGISTRATION_CLOSED_DETAIL
from arkav.competition.constants import K_TEAM_NOT_PARTICIPATING
from arkav.competition.constants import K_TEAM_NOT_PARTICIPATING_DETAIL
from arkav.competition.constants import K_TEAM_HAS_SELECTED_MEMBER
from arkav.competition.constants import K_TEAM_HAS_SELECTED_MEMBER_DETAIL
from arkav.competition.constants import K_TEAM_FULL
from arkav.competition.constants import K_TEAM_FULL_DETAIL


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

add_team_member_responses = {
    200: TeamMemberSerializer(),
    400: openapi.Response(description='Bad Request', content={
        'application/json': {
            'schema': generic_response_schema,
            'examples': {
                'Competition registration closed': {
                    'value': {
                        'code': K_COMPETITION_REGISTRATION_CLOSED,
                        'detail': K_COMPETITION_REGISTRATION_CLOSED_DETAIL,
                    }
                },
                'Team not participating': {
                    'value': {
                        'code': K_TEAM_NOT_PARTICIPATING,
                        'detail': K_TEAM_NOT_PARTICIPATING_DETAIL,
                    }
                },
                'Team full': {
                    'value': {
                        'code': K_TEAM_FULL,
                        'detail': K_TEAM_FULL_DETAIL,
                    }
                },
                'Team has selected member': {
                    'value': {
                        'code': K_TEAM_HAS_SELECTED_MEMBER,
                        'detail': K_TEAM_HAS_SELECTED_MEMBER_DETAIL,
                    }
                },
            }
        }
    })
}
