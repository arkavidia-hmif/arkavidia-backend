from django.urls import path
from arkav.arkalogica.views import ListSubmissionsView, StartSessionView, ListSessionsView, SubmitView

urlpatterns = [
    path('', ListSessionsView.as_view(), name='arkalogica-available-session'),
    path('<uuid:session_id>', StartSessionView.as_view(), name='arkalogica-start-session'),
    path('submissions/', ListSubmissionsView.as_view(), name='arkalogica-submissions'),
    path('submit/', SubmitView.as_view(), name='arkalogica-submissions')
]
