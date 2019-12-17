from arkav.mainevent.views import DetailMaineventView
from arkav.mainevent.views import ListMaineventsView
from arkav.mainevent.views import ListRegistrantsView
from arkav.mainevent.views import RegisterRegistrantView
from arkav.mainevent.views import RetrieveUpdateDestroyRegistrantView
from arkav.mainevent.views import SubmitTaskResponseView
from django.urls import path


urlpatterns = [
    path('', ListMaineventsView.as_view(), name='mainevent-list'),
    path('<int:mainevent_id>', DetailMaineventView.as_view(), name='mainevent-mainevent-detail'),
    path('register/', RegisterRegistrantView.as_view(), name='mainevent-registrant-register'),
    path('registrants/', ListRegistrantsView.as_view(), name='mainevent-registrant-list'),
    path('registrants/<int:registrant_id>/',
         RetrieveUpdateDestroyRegistrantView.as_view(), name='mainevent-registrant-detail'),
    path('registrants/<int:registrant_id>/tasks/<int:task_id>/',
         SubmitTaskResponseView.as_view(), name='mainevent-registrant-task-detail'),
]
