# Generated by Django 2.2.5 on 2019-09-16 10:35

from django.conf import settings
from django.db import migrations
from django.db import models
import arkav.arkavauth.managers
import arkav.arkavauth.utils
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    default=False,
                    help_text='Designates that this user has all permissions without explicitly assigning them.',
                    verbose_name='superuser status')),
                ('is_staff', models.BooleanField(
                    default=False,
                    help_text='Designates whether the user can log into this admin site.',
                    verbose_name='staff status')),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Designates whether this user should be treated as active. '
                              'Unselect this instead of deleting accounts.',
                    verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('full_name', models.CharField(max_length=75)),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email address')),
                ('is_email_confirmed', models.BooleanField(default=False)),
                ('confirmation_token', models.CharField(default=arkav.arkavauth.utils.generate_random_token,
                                                        max_length=30, unique=True)),
                ('confirmation_email_last_sent_time', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(
                    blank=True,
                    help_text='The groups this user belongs to. '
                              'A user will get all permissions granted to each of their groups.',
                    related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user',
                                                            to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', arkav.arkavauth.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PasswordResetAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(default=arkav.arkavauth.utils.generate_random_token,
                                           max_length=30, unique=True)),
                ('sent_time', models.DateTimeField(blank=True, null=True)),
                ('used_time', models.DateTimeField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                                              related_name='password_reset_attempt',
                                              to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
