from arkav.preevent.views import ListPreeventsView
from arkav.preevent.views import ListRegistrantsView
from arkav.preevent.views import RegisterRegistrantView
from arkav.preevent.views import RetrieveUpdateDestroyRegistrantView
from arkav.preevent.views import SubmitTaskResponseView
from django.urls import path


urlpatterns = [
    path('', ListPreeventsView.as_view(), name='preevent-list'),
    path('register/', RegisterRegistrantView.as_view(), name='preevent-registrant-register'),
    path('registrants/', ListRegistrantsView.as_view(), name='preevent-registrant-list'),
    path('registrants/<int:registrant_id>/',
         RetrieveUpdateDestroyRegistrantView.as_view(), name='preevent-registrant-detail'),
    path('registrants/<int:registrant_id>/tasks/<int:task_id>/',
         SubmitTaskResponseView.as_view(), name='preevent-registrant-task-detail'),
]
