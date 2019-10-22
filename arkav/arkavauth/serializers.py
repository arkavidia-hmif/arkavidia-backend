from arkav.arkavauth.constants import K_ACCOUNT_EMAIL_NOT_CONFIRMED
from arkav.arkavauth.constants import K_LOGIN_FAILED
from arkav.arkavauth.models import User
from arkav.utils.exceptions import ArkavAPIException
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=75)
    email = serializers.EmailField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_email_confirmed = serializers.BooleanField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'is_staff', 'is_active',
                  'is_email_confirmed', 'last_login', 'date_joined')
        read_only_fields = ('email', 'is_staff', 'is_active',
                            'is_email_confirmed', 'last_login', 'date_joined')


class LoginRequestSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.full_name

        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except exceptions.AuthenticationFailed:
            raise ArkavAPIException(
                detail='Wrong email / password',
                code=K_LOGIN_FAILED,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if (not self.user.is_email_confirmed):
            raise ArkavAPIException(
                detail='User email is not confirmed',
                code=K_ACCOUNT_EMAIL_NOT_CONFIRMED,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        return data


class RegistrationRequestSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=75)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField()


class RegistrationConfirmationRequestSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=30)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmationRequestSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=30)
    new_password = serializers.CharField()


class PasswordChangeRequestSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_password = serializers.CharField()
