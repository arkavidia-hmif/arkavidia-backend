from arkav.arkavauth.constants import K_ACCOUNT_EMAIL_NOT_CONFIRMED
from arkav.arkavauth.constants import K_LOGIN_FAILED
from arkav.arkavauth.models import User
from arkav.utils.exceptions import ArkavAPIException
from rest_framework import exceptions
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=75)
    email = serializers.EmailField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    current_education = serializers.CharField(max_length=30, allow_null=True)
    institution = serializers.CharField(max_length=75, allow_null=True)
    phone_number = serializers.CharField(max_length=20, allow_null=True)
    birth_date = serializers.DateField(allow_null=True)
    address = serializers.CharField(max_length=300, allow_null=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'date_joined', 'current_education', 'institution',
                  'phone_number', 'birth_date', 'address')
        read_only_fields = ('email', 'date_joined')


class LoginRequestSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)
        token['name'] = user.full_name

        return token

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)
            data['token'] = str(refresh.access_token)
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

        data['user'] = UserSerializer(self.user).data
        data['exp'] = refresh.payload['exp']

        return data


class LoginResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    exp = serializers.IntegerField(label='token expiry time')
    token = serializers.CharField(max_length=200)


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
