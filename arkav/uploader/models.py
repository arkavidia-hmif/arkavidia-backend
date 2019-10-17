from arkav.arkavauth.models import User
from django.db import models
from django.conf import settings
import uuid


class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    content = models.FileField()
    original_filename = models.CharField(max_length=200)
    file_size = models.BigIntegerField(null=True)
    description = models.CharField(max_length=200)
    content_type = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(to=User, related_name='uploaded_files', on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_filename

    @property
    def file_link(self):
        link = 'https://%s/%s/%s' % (settings.AWS_S3_CUSTOM_DOMAIN, settings.AWS_LOCATION, self.id)
        return link
