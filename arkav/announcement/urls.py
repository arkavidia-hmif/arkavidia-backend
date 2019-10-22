from arkav.announcement.views import ListAnnouncementsView
from django.urls import path


urlpatterns = [
    path('announcements/', ListAnnouncementsView.as_view(), name='announcement-list'),
]
