# auth
K_LOGIN_FAILED = 'login_failed'
K_ACCOUNT_EMAIL_NOT_CONFIRMED = 'account_email_not_confirmed'

# password_reset
K_PASSWORD_RESET_EMAIL_SENT = 'password_reset_email_sent'
K_PASSWORD_RESET_SUCCESSFUL = 'password_reset_successful'
K_INVALID_TOKEN = 'invalid_token'
K_TOKEN_USED = 'token_used'
K_PROFILE_INCOMPLETE = 'profile_incomplete'

# registration
K_REGISTRATION_SUCCESSFUL = 'registration_successful'
K_REGISTRATION_FAILED_EMAIL_USED = 'registration_failed_email_used'
K_REGISTRATION_CONFIRMATION_SUCCESSFUL = 'registration_confirmation_successful'

# user
K_PASSWORD_CHANGE_FAILED = 'password_change_failed'
K_PASSWORD_CHANGE_SUCCESSFUL = 'password_change_successful'

# current education
SMA = 'SMA'
KULIAH = 'Kuliah'
CURRENT_EDUCATION_CHOICES = (
    (SMA, SMA),
    (KULIAH, KULIAH),
)
SMA_KULIAH = '{}/{}'.format(SMA, KULIAH)
EDUCATION_LEVEL_CHOICES = (
    (SMA, SMA),
    (KULIAH, KULIAH),
    (SMA_KULIAH, SMA_KULIAH)
)
