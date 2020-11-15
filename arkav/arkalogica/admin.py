from django.contrib import admin
from arkav.arkalogica.models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass
