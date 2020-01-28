from arkav.eventcheckin.views import CheckInAttendeeView
from django.urls import path


urlpatterns = [
    path('<uuid:token>', CheckInAttendeeView.as_view(), name='attendee-checkin'),
]
