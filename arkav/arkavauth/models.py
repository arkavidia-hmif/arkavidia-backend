from arkav.arkavauth.managers import UserManager
from arkav.arkavauth.utils import generate_random_token
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    '''
    User model.
    We dont need the username. Login will use email.
    First name and last name is joined as full name.
    User have is_email_confirmed. The account wont be able
    to be used if this field is false.
    Confirmation token for the email confirmation is saved too.
    '''
    EDUCATION_CHOICE_HIGH_SCHOOL = 'SCHOOL'
    EDUCATION_CHOICE_HIGHER_EDUCATION = 'COLLEGE'
    EDUCATION_CHOICES = (
        (EDUCATION_CHOICE_HIGH_SCHOOL, 'SMA / Sederajat'),
        (EDUCATION_CHOICE_HIGHER_EDUCATION, 'Universitas / Sederajat'),
    )

    username = None
    first_name = None
    last_name = None
    full_name = models.CharField(max_length=75)
    email = models.EmailField(_('Email address'), unique=True)
    is_email_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=30, default=generate_random_token, unique=True)
    confirmation_email_last_sent_time = models.DateTimeField(null=True, blank=True)

    current_education = models.CharField(max_length=10, choices=EDUCATION_CHOICES, null=True, default=None)
    institution = models.CharField(max_length=75, null=True, blank=True, default=None)
    phone_number = models.CharField(max_length=20, null=True, default=None)
    birth_date = models.DateField(null=True, default=None)
    address = models.TextField(null=True, default=None)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class PasswordResetAttempt(models.Model):
    '''
    An attempt to confirm password reset using email.
    '''
    user = models.OneToOneField(to=User, related_name='password_reset_attempt', on_delete=models.CASCADE)
    token = models.CharField(max_length=30, default=generate_random_token, unique=True)
    sent_time = models.DateTimeField(null=True, blank=True)
    used_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return '%s' % self.user

    @property
    def is_used(self):
        return self.used_time is not None
