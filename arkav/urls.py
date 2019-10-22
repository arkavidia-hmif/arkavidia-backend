from django.contrib import admin
from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title='Arkavidia Backend API',
        default_version='v1',
        description='Arkavidia 6.0 Backend API Documentation',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='contact@snippets.local'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Django admin site
    path('administration-panel/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),

    # API Documentation
    path('arkavapi-documentation/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # API routes
    path('api/auth/', include('arkav.arkavauth.urls')),
    path('api/announcement/', include('arkav.announcement.urls')),
    path('api/uploader/', include('arkav.uploader.urls')),
    path('api/competition/', include('arkav.competition.urls')),
    # path('api/preevent/', include('arkav.preevent.urls')),
    # path('api/quiz/', include('arkav.quiz.urls')),
    # path('api/seminar/', include('arkav.seminar.urls')),
]
