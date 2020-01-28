from arkav.eventcheckin.views import CheckInAttendeeView
from django.urls import path


urlpatterns = [
    path('', CheckInAttendeeView.as_view(), name='attendee-checkin'),
]
