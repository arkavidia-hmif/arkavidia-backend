from arkav.uploader.views import RetrieveUploadedFileView
from arkav.uploader.views import UploadFileView
from django.urls import path


urlpatterns = [
    path('uploaded-file', UploadFileView.as_view(), name='uploader-upload-file'),
    path('uploaded-file/<uuid:file_id>/', RetrieveUploadedFileView.as_view(), name='uploader-uploaded-file-detail'),
]
