from arkav.arkavauth.models import PasswordResetAttempt
from arkav.arkavauth.models import User
from arkav.arkavauth.services import UserService
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpResponseRedirect
from django.urls import path
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def resend_confirmation_email(modeladmin, request, queryset):
    for obj in queryset:
        UserService().send_registration_confirmation_email(obj)


resend_confirmation_email.short_description = 'Resend the email of the selected attempts with the same token.'


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    '''Define admin model for custom User model with no username field.'''

    fieldsets = (
        (
            None,
            {'fields': ['full_name', 'email', 'password']}
        ),
        (
            _('Permissions'),
            {'fields': ['is_active', 'is_email_confirmed', 'is_staff',
                        'is_superuser', 'groups', 'user_permissions']}
        ),
        (
            _('Important dates'),
            {'fields': ('last_login', 'date_joined')}
        ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'full_name', 'is_staff', 'is_active', 'is_email_confirmed', 'custom_action')
    search_fields = ('email', 'full_name')
    ordering = ('email',)
    actions = [resend_confirmation_email]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/impersonate/',
                self.admin_site.admin_view(self.impersonate),
                name='arkavauth-impersonate',
            ),
        ]
        return custom_urls + urls

    def custom_action(self, obj):
        return format_html(
            '<a class="button" href="{}">Impersonate</a>',
            reverse('admin:arkavauth-impersonate', args=[obj.pk]),
        )

    custom_action.short_description = 'Action'
    custom_action.allow_tags = True

    def impersonate(self, request, user_id):
        user = User.objects.filter(pk=user_id).first()
        jwt_token = TokenObtainPairSerializer.get_token(user)
        return HttpResponseRedirect('https://arkavidia.id/login?fromJwt={}'.format(jwt_token))


@admin.register(PasswordResetAttempt)
class PasswordResetAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'sent_time', 'used_time']
    search_fields = ['user__full_name', 'user__email']

    class Meta:
        ordering = ['-sent_time']
