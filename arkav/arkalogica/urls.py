from django.urls import path
from arkav.arkalogica.views import SubmissionView, StartView, SubmitView

urlpatterns = [
    path('<int:session_id>', StartView.as_view(), name='arkalogica-start'),
    path('submissions/', SubmissionView.as_view(), name='arkalogica-submissions'),
    path('submit/', SubmitView.as_view(), name='arkalogica-submissions')
]
