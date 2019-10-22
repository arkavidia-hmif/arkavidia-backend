from arkav.arkavauth.views.auth import LoginView
from arkav.arkavauth.views.password_reset import PasswordResetConfirmationView
from arkav.arkavauth.views.password_reset import PasswordResetView
from arkav.arkavauth.views.registration import RegistrationConfirmationView
from arkav.arkavauth.views.registration import RegistrationView
from arkav.arkavauth.views.session import SessionView
from arkav.arkavauth.views.user import EditUserView
from arkav.arkavauth.views.user import PasswordChangeView
from django.urls import path

urlpatterns = [
    path('', SessionView.as_view(), name='auth-current-session'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('register/', RegistrationView.as_view(), name='auth-register'),
    path('confirm-registration/', RegistrationConfirmationView.as_view(), name='auth-register-confirmation'),
    path('password-reset/', PasswordResetView.as_view(), name='auth-password-reset'),
    path('confirm-password-reset/', PasswordResetConfirmationView.as_view(), name='auth-confirm-passowrd-reset'),
    path('change-password/', PasswordChangeView.as_view(), name='auth-change-password'),
    path('edit-user/', EditUserView.as_view(), name='auth-edit-user'),
]
