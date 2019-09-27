from arkav.arkavauth.views.auth import get_current_session_view
from arkav.arkavauth.views.auth import login_view
from arkav.arkavauth.views.auth import logout_view
from arkav.arkavauth.views.password_reset import password_reset_confirmation_view
from arkav.arkavauth.views.password_reset import password_reset_view
from arkav.arkavauth.views.registration import registration_confirmation_view
from arkav.arkavauth.views.registration import registration_view
from arkav.arkavauth.views.user import edit_user_view
from arkav.arkavauth.views.user import password_change_view
from django.urls import path

urlpatterns = [
    path('', get_current_session_view, name='auth-current-session'),
    path('login/', login_view, name='auth-login'),
    path('logout/', logout_view, name='auth-logout'),
    path('register/', registration_view, name='auth-register'),
    path('confirm-registration/', registration_confirmation_view, name='auth-register-confirmation'),
    path('password-reset/', password_reset_view, name='auth-password-reset'),
    path('confirm-password-reset/', password_reset_confirmation_view, name='auth-confirm-passowrd-reset'),
    path('change-password/', password_change_view, name='auth-change-password'),
    path('edit-user/', edit_user_view, name='auth-edit-user'),
]
