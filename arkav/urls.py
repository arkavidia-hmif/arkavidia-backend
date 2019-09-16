from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Django admin site
    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),

    # API routes
    path('api/auth/', include('arkav.arkavauth.urls')),
    # path('api/upload/', include('arkav.uploader.urls')),
    # path('api/competitions/', include('arkav.competition.urls')),
    # path('api/preevent/', include('arkav.preevent.urls')),
    # path('api/quiz/', include('arkav.quiz.urls')),
    # path('api/seminar/', include('arkav.seminar.urls')),
]
