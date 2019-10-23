from arkav.uploader.views import upload_file_view
from arkav.uploader.views import RetrieveUploadedFileView
from django.urls import path


urlpatterns = [
    path('uploaded-file', upload_file_view, name='uploader-uploaded-file'),
    path('uploaded-file/<uuid:file_id>/', RetrieveUploadedFileView.as_view(), name='uploader-uploaded-file-detail'),
]
